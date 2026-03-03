import requests
try:
    print("Testing Location API...")
    r = requests.get("http://127.0.0.1:8000/locations/search?q=London")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
