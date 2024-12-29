import subprocess
import os
import datetime 
import requests
import re

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"
MAX_DIFF_SIZE = 3000  # 단일 요청당 최대 토큰 수
MAX_FILES_PER_SUMMARY = 5  # 한 번에 요약할 최대 파일 수

def get_diff_text():
    """최근 커밋과 직전 커밋 간 diff 텍스트를 가져온다."""
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD^", "HEAD"])
        return diff.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff: {e}")
        return ""

def estimate_tokens(text):
    """텍스트의 대략적인 토큰 수를 추정"""
    # 단순히 단어 수로 추정 (실제 토큰화보다 덜 정확하지만 빠름)
    return len(re.findall(r'\w+', text))

def chunk_diff(diff_text):
    """대용량 diff를 관리 가능한 청크로 분리"""
    files = {}
    current_file = None
    current_content = []
    
    # 파일별로 분리
    for line in diff_text.split('\n'):
        if line.startswith('diff --git'):
            if current_file:
                files[current_file] = '\n'.join(current_content)
            current_file = line.split()[-1].replace('b/', '')
            current_content = [line]
        else:
            current_content.append(line)
    
    if current_file:
        files[current_file] = '\n'.join(current_content)

    # 파일들을 크기에 따라 정렬
    sorted_files = sorted(
        files.items(),
        key=lambda x: estimate_tokens(x[1]),
        reverse=True
    )

    # 큰 파일들은 개별 처리, 작은 파일들은 그룹화
    chunks = []
    current_chunk = []
    current_chunk_size = 0

    for filename, content in sorted_files:
        tokens = estimate_tokens(content)
        
        if tokens > MAX_DIFF_SIZE:
            # 큰 파일은 여러 청크로 분할
            lines = content.split('\n')
            chunk_lines = []
            current_size = 0
            
            for line in lines:
                line_tokens = estimate_tokens(line)
                if current_size + line_tokens > MAX_DIFF_SIZE:
                    if chunk_lines:
                        chunks.append((f"{filename} (부분)", '\n'.join(chunk_lines)))
                    chunk_lines = [line]
                    current_size = line_tokens
                else:
                    chunk_lines.append(line)
                    current_size += line_tokens
            
            if chunk_lines:
                chunks.append((f"{filename} (부분)", '\n'.join(chunk_lines)))
        
        elif current_chunk_size + tokens > MAX_DIFF_SIZE or len(current_chunk) >= MAX_FILES_PER_SUMMARY:
            # 현재 청크가 가득 차면 새 청크 시작
            if current_chunk:
                chunks.append(("여러 파일", '\n'.join(c[1] for c in current_chunk)))
            current_chunk = [(filename, content)]
            current_chunk_size = tokens
        else:
            # 현재 청크에 파일 추가
            current_chunk.append((filename, content))
            current_chunk_size += tokens

    if current_chunk:
        chunks.append(("여러 파일", '\n'.join(c[1] for c in current_chunk)))

    return chunks

def summarize_diff(diff_text, context=""):
    """DeepSeek API를 사용해 diff 내용을 요약"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are a helpful assistant that summarizes code changes.
Focus on:
1. What functionality was added/modified
2. Any significant refactoring
3. Important bug fixes
4. Potential breaking changes
Be concise but informative."""

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Context: {context}\nPlease summarize these code changes:\n\n{diff_text}"
            }
        ],
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error in API call: {str(e)}")
        if hasattr(response, 'text'):
            print(f"API Response: {response.text}")
        return f"Failed to summarize diff: {str(e)}"

def create_markdown_file(content, base_dir="summaries"):
    """요약 결과를 연/월 구조의 Markdown 파일로 저장"""
    now = datetime.datetime.utcnow()
    year_dir = os.path.join(base_dir, str(now.year))
    month_dir = os.path.join(year_dir, f"{now.month:02d}")
    
    os.makedirs(month_dir, exist_ok=True)
    
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
        commit_msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"]).decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting git info: {e}")
        commit_hash = "unknown"
        branch_name = "unknown"
        commit_msg = "unknown"
    
    filename = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_summary.md"
    filepath = os.path.join(month_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Code Update Summary\n\n")
        f.write(f"- **Date**: {now.strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        f.write(f"- **Branch**: {branch_name}\n")
        f.write(f"- **Commit**: {commit_hash}\n")
        f.write(f"- **Message**: {commit_msg}\n\n")
        f.write("## Changes Summary\n\n")
        f.write(content + "\n")
    
    return filepath

def main():
    diff_text = get_diff_text()
    if not diff_text.strip():
        print("No diff found between HEAD^ and HEAD.")
        return

    chunks = chunk_diff(diff_text)
    summaries = []
    
    for context, chunk in chunks:
        print(f"Processing chunk: {context}")
        summary = summarize_diff(chunk, context)
        if not summary.startswith("Failed to summarize"):
            summaries.append(f"### {context}\n{summary}\n")
    
    if summaries:
        final_summary = "\n".join(summaries)
    else:
        final_summary = "No significant changes to summarize."
    
    md_file = create_markdown_file(final_summary)
    print(f"Markdown file created: {md_file}")

if __name__ == "__main__":
    main()