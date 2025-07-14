# test_gemini.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print("Using API Key:", api_key)

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Say hi")
print(response.text)
