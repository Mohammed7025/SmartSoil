import requests
import json

BASE_URL = "http://localhost:8000"

def test_fertilizer():
    payload = {
        "n": 90,
        "p": 42,
        "k": 43,
        "temperature": 25,
        "humidity": 60,
        "ph": 6.5,
        "rainfall": 200
    }
    try:
        response = requests.post(f"{BASE_URL}/predict/fertilizer", json=payload)
        print(f"Fertilizer Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Fertilizer Error: {e}")

def test_irrigation():
    payload = {
        "n": 90,
        "p": 42,
        "k": 43,
        "temperature": 25,
        "humidity": 60,
        "ph": 6.5,
        "rainfall": 200
    }
    try:
        response = requests.post(f"{BASE_URL}/predict/irrigation", json=payload)
        print(f"Irrigation Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Irrigation Error: {e}")

if __name__ == "__main__":
    test_fertilizer()
    test_irrigation()
