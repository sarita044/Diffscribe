# 🧠 Diffscribe

**Diffscribe** is an intelligent CLI tool that automatically generates meaningful Git commit messages using your **staged diffs**. It leverages **Gemini (by Google)** and **Groq** APIs to analyze your code changes and produce clean, contextual commit messages — all from the terminal.

---

## ✨ Features

- 📜 AI-generated commit messages based on `git diff --cached`
- 🤖 Supports **Gemini** (Google) and **Groq** AI models
- 🔁 Auto fallback: If Gemini fails, Groq takes over
- 🔐 First-time setup with API key prompts and secure `.env` storage
- 🚫 Your code is never stored — only diff sent securely to model

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install diffscribe
```
Or install locally for development:

```bash
git clone https://github.com/yourusername/diffscribe.git
cd diffscribe
pip install -e .
```

🚀 Usage
Stage your changes as usual:
```bash
git add .
```
Then run:
diffscribe

You’ll see an AI-generated commit message based on your staged diff.

✅ Commit directly

To auto-generate and commit in one step:

```bash
diffscribe --commit
```

This will generate a commit message and run: git commit -m "<generated-message>"

🔑 First-Time Setup (API Keys)
When you run diffscribe for the first time, you'll be prompted to enter free API keys for Gemini and Groq.

1. 🌐 Gemini (Google) API Key
🔗 Generate at: https://makersuite.google.com/app/apikey

📌 After login, click on your profile icon > API Keys > Create API key

2. ⚡ Groq API Key
🔗 Generate at: https://console.groq.com/keys

📌 Log in > Go to API Keys tab > Create new key

✅ Once entered, your keys will be saved automatically to a local .env file — no need to enter them again.

If your keys ever expire or are invalid, you'll be prompted to enter new ones on the next run.

🛡️ Security & Privacy
Your .env file is local only and never uploaded.

Only the staged diff is sent securely to Gemini/Groq.

No code or messages are stored by diffscribe.

