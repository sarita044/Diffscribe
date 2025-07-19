from diffscribe.utils import get_staged_diff, truncate_diff, scrub_sensitive_data
import argparse
import subprocess
import sys
import re
from diffscribe.llm_router import generate_commit_message
import os
from dotenv import load_dotenv
from pathlib import Path
from diffscribe.setup_keys import setup_keys

env_path = Path(__file__).resolve().parent.parent / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    setup_keys(first_setup=True)
    load_dotenv()

# Check and prompt if missing or default
def ensure_api_keys():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")

    if "your_" in gemini_key or not gemini_key or "your_" in groq_key or not groq_key:
        setup_keys()
        load_dotenv()  # Reload after writing

ensure_api_keys()

# Optional: Validate at runtime
if not os.getenv("GEMINI_API_KEY") and not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("❌ Both GEMINI_API_KEY and GROQ_API_KEY are missing from environment.")



def main():
    parser = argparse.ArgumentParser(description="🧠 Diffscribe: Semantic Git commit message generator")
    parser.add_argument("--commit", action="store_true", help="Automatically commit with the generated message")
    args = parser.parse_args()
    
    print("🧠 Diffscribe: Generating commit message using secure diff...")

    # Step 1: Get the Git diff
    raw_diff = get_staged_diff()
    if not raw_diff:
        print("⚠️ No staged changes found. Please run `git add <file>` first.")
        sys.exit(1)

    short_diff = truncate_diff(raw_diff, max_words=2000)
    short_diff = re.sub(r'\x1b\[[0-9;]*m', '', short_diff)
    scrubbed_diff = scrub_sensitive_data(short_diff)
    # Step 2: Generate commit message from diff
    try:
        message = generate_commit_message(scrubbed_diff)
        print("✅ Suggested Commit Message:\n")
        print(message)
        if args.commit:
            subprocess.run(["git", "commit", "-m", message])
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
