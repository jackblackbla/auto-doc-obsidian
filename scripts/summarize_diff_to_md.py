import subprocess
import os
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

def chunk_diff(diff_text, max_tokens=3000):
    """대용량 diff를 파일 단위로 분리"""
    files = {}
    current_file = None
    current_content = []
    
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
    
    return files

def get_diff_text():
    """최근 커밋과 직전 커밋 간 diff 텍스트를 가져온다."""
    diff = subprocess.check_output(["git", "diff", "HEAD^", "HEAD"])
    return diff.decode("utf-8")

def summarize_diff(diff_text):
    """DeepSeek API를 사용해 diff 내용을 요약"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes code diffs."},
            {"role": "user", "content": f"Please summarize the following diff:\n{diff_text}"}
        ],
        "model": "deepseek-chat",
        "temperature": 0.2
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error in summarize_diff: {e}")
        return f"Failed to summarize diff: {str(e)}"

def summarize_large_diff(diff_text):
    """파일별로 분리하여 각각 요약"""
    files = chunk_diff(diff_text)
    summaries = []
    
    for filename, file_diff in files.items():
        summary = summarize_diff(file_diff)
        summaries.append(f"## {filename}\n{summary}\n")
    
    return "\n".join(summaries)

def create_markdown_file(content, base_dir="summaries"):
    """요약 결과를 Markdown 파일로 저장"""
    now = datetime.datetime.utcnow()
    year_dir = os.path.join(base_dir, str(now.year))
    month_dir = os.path.join(year_dir, f"{now.month:02d}")
    
    os.makedirs(month_dir, exist_ok=True)
    
    filename = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_summary.md"
    filepath = os.path.join(month_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Code Update Summary ({now.strftime('%Y-%m-%d %H:%M:%S')} UTC)\n\n")
        f.write(content + "\n")
    
    return filepath

def main():
    diff_text = get_diff_text()
    if not diff_text.strip():
        print("No diff found between HEAD^ and HEAD.")
        return
    
    # 큰 변경사항은 파일별로 분리하여 요약
    if len(diff_text) > 3000:
        summary = summarize_large_diff(diff_text)
    else:
        summary = summarize_diff(diff_text)
    
    print("=== Summary ===")
    print(summary)
    
    md_file = create_markdown_file(summary)
    print(f"Markdown file created: {md_file}")

if __name__ == "__main__":
    main()