from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from gemini_llm import generate_commit_message as gemini_generate
from groq_llm import generate_commit_message as groq_generate

MAX_GEMINI_TIMEOUT = 15  # seconds

def generate_commit_message(diff_text: str) -> str:
    """
    Try Gemini first with a timeout. If it fails or takes too long, fallback to Groq.
    If both fail, raise a clean error.
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(gemini_generate, diff_text)

        try:
            return future.result(timeout=MAX_GEMINI_TIMEOUT)
        
        except FuturesTimeout:
            print(f"⚠️ Gemini is taking too long (> {MAX_GEMINI_TIMEOUT}s). Falling back to Groq...")
        
        except Exception as gemini_error:
            print(f"⚠️ Gemini failed: {gemini_error}. Trying Groq...")

    # Fallback to Groq
    try:
        return groq_generate(diff_text)
    except Exception as groq_error:
        raise RuntimeError(
            f"❌ Both Gemini and Groq failed.\n\nGemini timeout/error handled.\nGroq Error: {groq_error}"
        )