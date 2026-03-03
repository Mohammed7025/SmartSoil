import requests
import json

url = "http://localhost:8000/predict/fertilizer"

# Case 1: Ideal conditions (checking if logic breaks)
data_ideal = {
    "n": 100, "p": 50, "k": 50,
    "temperature": 25, "humidity": 60, "ph": 6.5, "rainfall": 100
}
print("\n--- Test 1: Ideal Scenario ---")
try:
    res = requests.post(url, json=data_ideal)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(e)

# Case 2: User Scenario (Low Rainfall, specific NPK)
# N=45 (Low), P=26, K=33, Rain=0.61 (Low)
data_user = {
    "n": 45, "p": 26, "k": 33,
    "temperature": 26.45, "humidity": 83, "ph": 6.5, "rainfall": 0.61
}
print("\n--- Test 2: User Scenario (Low Rain + NPK Context) ---")
try:
    res = requests.post(url, json=data_user)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(e)
