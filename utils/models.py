import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Load your API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env file.")
else:
    # 2. Configure the library
    genai.configure(api_key=api_key)

    print("🔍 Checking available Gemini models for your API key...\n")
    
    try:
        # 3. List models that support content generation
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Found: {m.name}")
                
    except Exception as e:
        print(f"❌ Error listing models: {e}")