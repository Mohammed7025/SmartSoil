
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_signup():
    url = f"{BASE_URL}/auth/signup"
    data = {"email": "test_user_unique@example.com", "password": "password123", "full_name": "Test User", "role": "farmer"}
    try:
        response = requests.post(url, json=data)
        print(f"Signup: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Signup Error: {e}")

def test_login():
    url = f"{BASE_URL}/auth/login"
    data = {"email": "test_user_unique@example.com", "password": "password123"}
    try:
        response = requests.post(url, json=data)
        print(f"Login: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Login Error: {e}")

if __name__ == "__main__":
    test_signup()
    test_login()
