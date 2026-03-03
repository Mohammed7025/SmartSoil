import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

payload = {
    "contents": [{"parts": [{"text": "Hello"}]}]
}

print(f"Testing Direct API Call to: {url}")
start = time.time()
try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Time: {time.time() - start:.2f}s")
    print(f"Response: {response.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")
