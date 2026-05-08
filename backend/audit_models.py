import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def audit_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Total Models Found: {len(models)}")
            for m in models:
                name = m['name']
                # Check for 1.5 flash
                if "1.5-flash" in name:
                    print(f"FOUND 1.5 FLASH: {name}")
                # Check for 1.5 pro
                if "1.5-pro" in name:
                    print(f"FOUND 1.5 PRO: {name}")
                # Check for 2.0
                if "2.0-flash" in name:
                    print(f"FOUND 2.0 FLASH: {name}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"EX: {e}")

if __name__ == "__main__":
    audit_models()
