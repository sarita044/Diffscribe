from diffscribe import utils as diffscribe_utils
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

def ensure_api_keys():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")

    if "your_" in gemini_key or not gemini_key or "your_" in groq_key or not groq_key:
        setup_keys()
        load_dotenv()

ensure_api_keys()


def main():
    parser = argparse.ArgumentParser(description="🧠 Diffscribe: Semantic Git commit message generator")
    parser.add_argument("--commit", action="store_true", help="Automatically commit with the generated message")
    args = parser.parse_args()
    
    print("🧠 Diffscribe: Generating commit message using secure diff...")

    # Get the Git diff
    raw_diff = diffscribe_utils.get_staged_diff()
    if not raw_diff:
        print("⚠️ No staged changes found. Please run `git add <file>` first.")
        sys.exit(1)

    short_diff = diffscribe_utils.truncate_diff(raw_diff, max_words=2000)
    short_diff = re.sub(r'\x1b\[[0-9;]*m', '', short_diff)
    scrubbed_diff = diffscribe_utils.scrub_sensitive_data(short_diff)
    # Generate commit message from diff
    try:
        if args.commit:
            cached_message = diffscribe_utils.load_commit_message_from_cache()
            if cached_message:
                subprocess.run(["git", "commit", "-m", cached_message])
                diffscribe_utils.clear_commit_message_cache()
            else:
                # Fallback to generating a new one
                commit_message = generate_commit_message(scrubbed_diff)
                subprocess.run(["git", "commit", "-m", commit_message])
        else:
            commit_message = generate_commit_message(scrubbed_diff)
            diffscribe_utils.save_commit_message_to_cache(commit_message)
            print("✅ Suggested Commit Message:\n")
            print(commit_message)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
