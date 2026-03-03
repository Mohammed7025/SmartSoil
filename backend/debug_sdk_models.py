import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    # The SDK uses a different way to list models, or we can just try a simple generation to test.
    # But let's try to list standard models if possible, or just test a few known ones.
    
    print("Testing common models...")
    
    test_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    for model_name in test_models:
        print(f"Testing {model_name}...", end=" ")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hello"
            )
            print(f"SUCCESS! (Response: {response.text})")
        except Exception as e:
            print(f"FAILED. Error: {e}")
            
except Exception as e:
    print(f"SDK Init Error: {e}")
