import requests
import time

url = "http://localhost:8000/chat"
payload = {
    "message": "Hello, how are you?",
    "context": "Testing connection"
}

print(f"Sending request to {url}...")
start_time = time.time()

try:
    response = requests.post(url, json=payload, timeout=35)
    end_time = time.time()
    
    print(f"Status Code: {response.status_code}")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
    print("Response:", response.text)

except Exception as e:
    print(f"Error: {e}")
