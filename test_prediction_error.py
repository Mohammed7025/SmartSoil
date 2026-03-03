
import requests
import json

def test_prediction():
    url = "http://127.0.0.1:8000/predict/crop"
    
    # Sample input based on the screenshot
    payload = {
        "n": 45,
        "p": 26,
        "k": 33,
        "temperature": 30.58,
        "humidity": 44,
        "ph": 6.5,
        "rainfall": 0.13
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("Response Status: 200 OK")
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Request failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_prediction()
