import subprocess
import os
import datetime
import requests
import json

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

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
        "model": "deepseek-coder-33b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes code diffs."},
            {"role": "user", "content": f"Please summarize the following diff:\n{diff_text}"}
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }
    
    try:
        print("Sending request to DeepSeek API...")  # 디버깅용
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"API Response Status: {response.status_code}")  # 디버깅용
        print(f"API Response: {response.text}")  # 디버깅용
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error in summarize_diff: {str(e)}")
        print(f"Full error details: {e.__class__.__name__}")  # 디버깅용
        return f"Failed to summarize diff: {str(e)}"