import os
import sys
from google import genai
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
print("START_TEST")

candidates = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]

for m in candidates:
    try:
        print(f"TRYING: {m}")
        client.models.generate_content(model=m, contents="hi")
        print(f"WORKS: {m}")
        break  # Stop at first working one
    except Exception as e:
        print(f"FAIL: {m}")
