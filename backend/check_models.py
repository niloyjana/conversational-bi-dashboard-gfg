import google.generativeai as genai
import os
from dotenv import load_dotenv

# Look for both .env and backend/backend.env
load_dotenv()
load_dotenv("backend/backend.env")

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    print("Listing available models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("API Key not found.")
