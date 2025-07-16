from groq_llm import generate_commit_message as groq_generate
from gemini_llm import generate_commit_message as gemini_generate
    
def generate_commit_message(diff_text: str) -> str:
    """
    Try Groq first. If it fails, fallback to Gemini.
    If both fail, raise a final error.
    """
    try:
        return groq_generate(diff_text)
    except Exception as groq_error:
        try:
            return gemini_generate(diff_text)
        except Exception as gemini_error:
            raise RuntimeError(
                f"❌ Both Groq and Gemini failed.\n\nGroq Error: {groq_error}\nGemini Error: {gemini_error}"
            )