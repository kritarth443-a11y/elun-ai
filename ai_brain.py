from google import genai
from google.genai import errors

# Replace the text inside the quotes with your actual Google AI Studio key!
API_KEY = "AQ.Ab8RN6J9HUoETzQm9PnzeM_Eippr99pSNwQJT1WqoFt0J78DKw"
client = genai.Client(api_key=API_KEY)

def generate_edit_plan(hook_delay, wpm, dead_air_count):
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
        # Using the current, active flash model
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt
        )
        return response.text
        
    except errors.ServerError:
        return "⚠️ **Server Busy:** Google's AI is currently overloaded with requests. Please wait 60 seconds and click Analyze again."
    except Exception as e:
        return f"⚠️ **Connection Error:** {str(e)}"

# Test it directly
if __name__ == "__main__":
    print("Thinking...")
    advice = generate_edit_plan(23.6, 60, 0)
    print("\n--- AI ADVICE ---")
    print(advice)