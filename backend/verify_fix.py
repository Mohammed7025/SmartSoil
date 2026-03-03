import requests
import json

BASE_URL = "http://localhost:8000"

def test_crop_prediction():
    print("\n--- Testing Crop Prediction (MinMax) ---")
    data = {
        "n": 90, "p": 42, "k": 43, 
        "temperature": 20.8, "humidity": 82, 
        "ph": 6.5, "rainfall": 202.9
    }
    try:
        res = requests.post(f"{BASE_URL}/predict/crop", json=data)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_fertilizer_prediction():
    print("\n--- Testing Fertilizer Prediction (Standard) ---")
    data = {
        "n": 20, "p": 20, "k": 20, # Low values, should suggest addition
        "temperature": 25, "humidity": 50, 
        "ph": 6.5, "rainfall": 100
    }
    try:
        res = requests.post(f"{BASE_URL}/predict/fertilizer", json=data)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_irrigation_prediction():
    print("\n--- Testing Irrigation Prediction (MinMax) ---")
    data = {"n": 90, "p": 42, "k": 43, 
        "temperature": 35, "humidity": 30, # Hot & Dry -> High irrigation expected
        "ph": 6.5, "rainfall": 0
    }
    try:
        res = requests.post(f"{BASE_URL}/predict/irrigation", json=data)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_crop_prediction()
    test_fertilizer_prediction()
    test_irrigation_prediction()
