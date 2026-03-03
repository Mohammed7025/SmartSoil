import requests
import json

url = "http://localhost:8000/predict/crop"

# Case 1: Rice (High Rain)
data_rice = {
    "n": 90, "p": 42, "k": 43, 
    "temperature": 25, "humidity": 80, "ph": 6.5, "rainfall": 220
}
print("\n--- Test 1: Rice Scenario ---")
try:
    res = requests.post(url, json=data_rice)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(e)

# Case 2: Wheat Conditions BUT with High Temp (Should Block Wheat)
data_hot = {
    "n": 30, "p": 30, "k": 30,
    "temperature": 40, "humidity": 60, "ph": 6.0, "rainfall": 50
}
print("\n--- Test 2: Hot Wheat Scenario (Should NOT be Wheat) ---")
try:
    res = requests.post(url, json=data_hot)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(e)
    
# Case 3: Rainfall Sanity Check (Input 2mm -> Should betreated as 60mm)
data_dry = {
    "n": 90, "p": 42, "k": 43, 
    "temperature": 25, "humidity": 80, "ph": 6.5, "rainfall": 2
}
print("\n--- Test 3: Rainfall Autocorrection (Input=2) ---")
try:
    res = requests.post(url, json=data_dry)
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print(e)
