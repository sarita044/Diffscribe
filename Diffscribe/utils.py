# helper functions (e.g. git diff)

# utils.py
import re
import unicodedata
import subprocess


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

def truncate_diff(diff: str, max_lines: int = 100) -> str:
    """
    Truncates and sanitizes a git diff.

    Args:
        diff (str): Git diff text.
        max_lines (int): Max number of lines to send to LLM.

    Returns:
        str: Cleaned and trimmed diff.
    """
    sanitized = sanitize_diff(diff)
    lines = sanitized.strip().splitlines()

    if len(lines) <= max_lines:
        return sanitized

    truncated = lines[:max_lines]
    truncated.append(f"\n# Diff truncated to first {max_lines} lines.")
    return "\n".join(truncated)

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