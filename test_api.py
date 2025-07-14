import os
from dotenv import load_dotenv
import google.generativeai as genai
import traceback

print("--- Starting API Test ---")

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in .env file.")
else:
    print("API Key found.")
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        print("Gemini AI configured.")

        # Create a model instance
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("Model 'gemini-1.5-flash' loaded.")

        # Define a simple prompt
        prompt = "Hello, world! This is a test."
        print(f"Sending prompt: '{prompt}'")

        # Generate content with a 30-second timeout
        request_options = {"timeout": 30}
        response = model.generate_content(prompt, request_options=request_options)
        print("--- API Response ---")
        print(response.text)
        print("--------------------")
        print("SUCCESS: API call was successful.")

    except Exception as e:
        print("\n--- ERROR ---")
        print(f"An error occurred: {e}")
        print("\n--- TRACEBACK ---")
        traceback.print_exc()
        print("---------------")

print("\n--- API Test Finished ---")