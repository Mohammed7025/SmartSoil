import requests
import os
import sys
from dotenv import load_dotenv

# Force output encoding
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        # Only print models that support generation, limit to first 10
        valid_models = [m['name'] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
        print(f"VALID: {valid_models[:10]}")
    else:
        print(f"ERR: {response.status_code}")
except Exception as e:
    print(f"EX: {e}")
