import requests
try:
    print("Testing Backend Root...")
    r = requests.get("http://127.0.0.1:8000/")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
