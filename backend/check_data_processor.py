from utils.data_processing_layer import data_processor
import json

# Sample Input (Noisy, missing values)
sample_input = {
    "n": 60,
    "p": 45,
    "k": 3000, # Out of range (Max 500)
    "temperature": 28,
    "humidity": 75,
    # "ph" is missing
    "rainfall": 120,
    "moisture": 40
}

print("Processing Sample Input...")
result = data_processor.process_pipeline(sample_input)

print("\n--- Processed Result ---")
print(json.dumps(result, indent=2))

print("\n--- Validation ---")
print(f"Original K: {sample_input['k']} -> Cleaned K: {result['engineered']['k']} (Should be clamped to 200 or 500)")
print(f"Missing pH filled with default: {result['engineered']['ph']}")
print(f"Computed Moisture Deficit: {result['engineered']['moisture_deficit']}")
print(f"Standardized Vector: {result['vectors']['std']}")
print(f"MinMax Vector: {result['vectors']['minmax']}")
