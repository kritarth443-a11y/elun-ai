import os

def generate_edit_plan(hook_delay, wpm, dead_air_count):
    """
    Generate editing recommendations using Gemini,
    only when explicitly configured. The rest of ELUN AI can run without Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        return "AI recommendation unavailable: GEMINI_API_KEY not set. Running in local-only mode."

    prompt = f"""
    You are an elite short-form video analyst for new influencers.
    Your goal is to give brutal, data-driven editing advice to fix retention drops.

    DATA FOR ANALYSIS:
    - Hook Delay: {hook_delay}s (Target: < 1.0s)
    - Speaking Pace: {wpm} WPM (Target: 150-170 WPM)
    - Dead Air Spots: {dead_air_count} (Target: 0)

    Write a short, punchy 3-point action plan for the creator.
    Do not be polite. Be direct. Tell them exactly what to cut and how to fix it for their next upload.
    """

    try:
        # Import the external SDK only when Gemini is enabled
        from google import genai
        from google.genai import errors
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text
    except Exception as error:
        return f"⚠️ **AI Error:** {type(error).__name__}: {error}"

if __name__ == "__main__":
    print("Thinking...")
    advice = generate_edit_plan(23.6, 60, 0)
    print("\n--- AI ADVICE ---")
    print(advice)