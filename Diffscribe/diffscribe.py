from utils import get_staged_diff, truncate_diff, scrub_sensitive_data
import argparse
import subprocess
import sys
import re
from llm_router import generate_commit_message


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

    short_diff = truncate_diff(raw_diff, max_lines=150)
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
