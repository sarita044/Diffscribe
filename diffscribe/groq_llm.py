import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

def generate_commit_message(diff_text: str) -> str:
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY not set. Please check your .env file.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
                You are a helpful assistant that writes semantic Git commit messages.

                Format:
                - feat(scope): new feature
                - fix(scope): bug fix
                - refactor(scope): code cleanup
                - chore(scope): config or tooling changes

                Only output the commit message — no extra text.

                Git diff:
                ```diff
                {diff_text} 
                """
                
    payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt.strip()}],
    "temperature": 0.3,
    "max_tokens": 80
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        raise RuntimeError(f"❌ Groq API error: {response.status_code} - {response.text}")