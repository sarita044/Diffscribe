import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Load .env if present

def generate_commit_message(diff_text: str) -> str:
    """
    Sends the scrubbed Git diff to Gemini and returns a semantic commit message.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ GEMINI_API_KEY not set. Add it to your environment or .env file.")

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = f"""
        You are a helpful assistant that writes semantic Git commit messages.

        Format:
        - feat(scope): new feature
        - fix(scope): bug fix
        - refactor(scope): code cleanup
        - chore(scope): config or tooling changes

        Only return the commit message. No extra text.

        Git diff:
        ```diff
        {diff_text}
        ```
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        raise RuntimeError(f"❌ Gemini request failed: {e}")
