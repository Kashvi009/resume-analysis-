import os
from dotenv import load_dotenv
import google.generativeai as genai
import traceback

def test_gemini_api():
    """
    A diagnostic script to test the connection and response from the Google Gemini API.
    """
    print("--- Starting Gemini API Connection Test ---")

    # 1. Load environment variables
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file.")
        print("Please ensure you have a .env file with your key.")
        return

    print("✅ API Key found in .env file.")

    # 2. Configure and test the API
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini AI configured successfully.")

        model = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Model 'gemini-1.5-flash' loaded.")

        prompt = "This is a test prompt. If you see this, respond with a short success message."
        print(f"▶️ Sending test prompt: '{prompt}'")

        # Generate content with a timeout
        response = model.generate_content(prompt, request_options={"timeout": 60})
        
        print("\\n--- API Response ---")
        print(response.text)
        print("--------------------")
        print("✅ SUCCESS: API call was successful and returned a response.")

    except Exception as e:
        print("\\n--- ❌ API TEST FAILED ---")
        print(f"An error occurred: {e}")
        print("\\n--- Traceback ---")
        traceback.print_exc()
        print("-------------------")

    print("\\n--- API Test Finished ---")

if __name__ == "__main__":
    test_gemini_api()