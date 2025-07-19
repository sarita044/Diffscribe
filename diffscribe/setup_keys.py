# diffscribe/setup_keys.py
import os

def setup_keys(first_setup = False):
    if first_setup:
        print("🔐 Diffscribe: First-time setup for API keys")
    else:
        print("❌ Either your API keys are missing, expired, or no longer valid.")
        print("🔄 Let's update them to continue using DiffScribe.")

    print("\n👉 To use Diffscribe, you need API keys from Gemini and Groq.")
    print("✨ Both keys are FREE to create!\n")
    print("🔹 Gemini (by Google):")
    print("    👉 Visit: https://makersuite.google.com/app/apikey")
    print("    ✅ Click the **'Generate API Key'** button")
    gemini_key = input("🔑 Enter your Gemini API Key (from https://makersuite.google.com/app/apikey): ").strip()

    print("🔹 Groq:")
    print("    👉 Visit: https://console.groq.com/keys")
    print("    ✅ Click **'Create API Key'**, name it, and copy the token")
    groq_key = input("🔑 Enter your Groq API Key (from https://console.groq.com/keys): ").strip()

    env_path = ".env"

    # Avoid duplicate keys
    existing_keys = {}
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    existing_keys[k] = v

    with open(env_path, "a") as f:
        if gemini_key and existing_keys.get("GEMINI_API_KEY") != gemini_key:
            f.write(f"\nGEMINI_API_KEY={gemini_key}")
        if groq_key and existing_keys.get("GROQ_API_KEY") != groq_key:
            f.write(f"\nGROQ_API_KEY={groq_key}")

    print("\n✅ API keys saved in `.env`. You’re all set!\n")
