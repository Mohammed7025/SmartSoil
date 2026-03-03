import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def check_backend():
    print(f"Checking backend at {BASE_URL}...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend is RUNNING and accessible.")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️ Backend is running but returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT reachable.")
        print("   Make sure you are running: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)

def check_endpoints():
    endpoints = [
        ("/", "GET", None),
        ("/predict/crop", "POST", {
            "n": 90, "p": 42, "k": 43, "temperature": 20, "humidity": 82, "ph": 6, "rainfall": 202
        }),
        ("/predict/fertilizer", "POST", {
            "n": 90, "p": 42, "k": 43, "temperature": 25, "humidity": 60, "ph": 6.5, "rainfall": 200
        }),
        ("/predict/irrigation", "POST", {
            "n": 90, "p": 42, "k": 43, "temperature": 25, "humidity": 60, "ph": 6.5, "rainfall": 200
        }),
        ("/weather/current", "POST", {
             "lat": 10.8505, "lon": 76.2711 
        })
    ]

    for endpoint, method, payload in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json=payload)
            
            print(f"[{response.status_code}] {method} {endpoint}")
            if response.status_code != 200:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Failed to connect to {endpoint}: {e}")

if __name__ == "__main__":
    check_backend()
    check_endpoints()
    print("\n---------------------------------------------------")
    print("If all checks passed, your backend is good.")
    print("If Flutter still fails, the issue is Android-side (Manifest/Network).")
