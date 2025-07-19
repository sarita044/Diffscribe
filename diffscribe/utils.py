# helper functions (e.g. git diff)

# utils.py
import re
import unicodedata
import subprocess
import json
import os


def get_staged_diff() -> str:
    """
    Returns the current staged Git diff (i.e., `git diff --cached` output).

    Returns:
        str: The staged Git diff text.

    Raises:
        RuntimeError: If there's an error running the Git command.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        diff = result.stdout.strip()
        return diff

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ Failed to get staged Git diff: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("❌ Git is not installed or not found in PATH.")

def sanitize_diff(diff: str) -> str:
    """
    Sanitizes the diff by removing emojis, binary content, and excessive unicode.

    Args:
        diff (str): Original git diff.

    Returns:
        str: Cleaned diff for LLM processing.
    """
    def is_emoji(s):
        return any(unicodedata.category(char).startswith("So") for char in s)

    cleaned_lines = []
    for line in diff.splitlines():
        # Skip long hex/base64-looking lines (often image diffs)
        if len(line) > 300 and re.match(r'^[A-Za-z0-9+/=]+$', line.strip()):
            continue

        # Remove emojis and special unicode symbols
        cleaned = ''.join(
            char for char in line
            if not is_emoji(char) and unicodedata.category(char)[0] != "C"
        )
        cleaned_lines.append(cleaned)

    return "\n".join(cleaned_lines)

def truncate_diff(diff: str, max_words: int = 1000) -> str:
    """
    Truncates and sanitizes a git diff by word count, preserving line structure.

    Args:
        diff (str): Git diff text.
        max_words (int): Maximum number of words to include.

    Returns:
        str: Cleaned and word-trimmed diff.
    """
    sanitized = sanitize_diff(diff)
    lines = sanitized.strip().splitlines()

    total_words = 0
    truncated_lines = []

    for line in lines:
        word_count = len(line.split())
        if total_words + word_count > max_words:
            break
        truncated_lines.append(line)
        total_words += word_count

    # If diff was truncated
    if total_words < len(sanitized.strip().split()):
        truncated_lines.append(f"\n# Diff truncated to first {max_words} words.")

    return "\n".join(truncated_lines)


def scrub_sensitive_data(diff: str) -> str:
    """
    Aggressively scrubs sensitive values from Git diffs by combining:
    - Variable name-based heuristics
    - Value pattern matching
    """

    # Variable name–based matchers (if var name looks sensitive)
    var_name_patterns = [
        r"password",
        r"secret",
        r"token",
        r"api[_-]?key",
        r"auth[_-]?key",
        r"bearer",
        r"client[_-]?secret",
        r"access[_-]?key",
        r"private[_-]?key",
        r"aws[_-]secret",
        r"authorization",
        r"passphrase",
        r"access[_-]?token",
        r"auth[_-]?token",
        r"aws[_-]?access",
        r"azure[_-]?client",
        r"gcp[_-]?key",
    ]

    # Sensitive value patterns (detect values directly)
    value_patterns = [
        (r"sk-[A-Za-z0-9]{20,}", "****"),  # OpenAI keys
        (r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+", "<jwt_token>"),  # JWT
        (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "<email>"),  # Email
        (r"https?:\/\/[^\/\s:@]+:[^\/\s:@]+@[^\/\s]+", "https://****:****@redacted"),  # Basic auth URL
        (r"\b\d{10,}\b", "<phone>"),  # Phone
        (r"\b(?:\d[ -]*?){13,16}\b", "<credit_card?>"),  # Credit card
        (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip_address>"),  # IPv4
        (r"\b[A-Fa-f0-9]{32,}\b", "<hex_secret>"),  # Long hex
        (r"[a-zA-Z0-9_\-]{40,}", "<long_token>"),  # Generic long token
        (r"[A-Za-z0-9+/]{20,}={0,2}", "<base64_blob>")  # Base64 blobs
    ]

    assignment_pattern = re.compile(r"(\b[\w\-]+\b)\s*[:=]\s*([\"'])(.+?)([\"'])")

    def scrub_line(line: str) -> str:
        # Handle + added diff lines only
        if not line.strip().startswith("+"):
            return line

        match = assignment_pattern.search(line)
        if not match:
            return line

        var_name, quote1, value, quote2 = match.groups()
        scrubbed_value = value

        # 1. If var_name looks sensitive → always scrub
        if any(re.search(rf"\b{pattern}\b", var_name, re.IGNORECASE) for pattern in var_name_patterns):
            scrubbed_value = "****"

        else:
            # 2. Otherwise scrub value if it matches any sensitive value pattern
            for pattern, replacement in value_patterns:
                if re.search(pattern, value):
                    scrubbed_value = replacement
                    break  # only first match applied

        # Replace original value in line
        scrubbed_line = line.replace(f"{quote1}{value}{quote2}", f"{quote1}{scrubbed_value}{quote2}")
        return scrubbed_line

    # Process line by line
    return "\n".join([scrub_line(line) for line in diff.splitlines()])


CACHE_FILE = ".diffscribe_cache"

def save_commit_message_to_cache(message: str):
    with open(CACHE_FILE, "w") as f:
        json.dump({"message": message}, f)

def load_commit_message_from_cache() -> str:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            return data.get("message")
    return None

def clear_commit_message_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        