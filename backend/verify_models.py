import pandas as pd
import numpy as np
import os
from train_tabnet import train_tabnet
from train_swift import train_swift
from train_ttl import train_ttl
from models.inference import model_service
from utils.data_processing_layer import data_processor

DATA_PATH = "smart_soil_dataset.csv"

def create_dummy_data():
    print("Creating dummy dataset...")
    data = {
        'nitrogen': np.random.randint(0, 100, 100),
        'phosphorus': np.random.randint(0, 100, 100),
        'potassium': np.random.randint(0, 100, 100),
        'temperature': np.random.randint(20, 35, 100),
        'humidity': np.random.randint(40, 90, 100),
        'ph': np.random.uniform(5.5, 7.5, 100),
        'rainfall_forecast': np.random.randint(0, 50, 100),
        'crop': np.random.choice(['Rice', 'Wheat', 'Maize'], 100),
        'irrigation_hours': np.random.uniform(0, 5, 100),
        'fertilizer_n': np.random.uniform(0, 50, 100),
        'fertilizer_p': np.random.uniform(0, 30, 100),
        'fertilizer_k': np.random.uniform(0, 20, 100)
    }
    pd.DataFrame(data).to_csv(DATA_PATH, index=False)

def verify():
    # 1. Ensure Data
    if not os.path.exists(DATA_PATH):
        create_dummy_data()
        
    # 2. Train Models
    try:
        train_tabnet()
        train_swift()
        train_ttl()
    except Exception as e:
        print(f"Training failed: {e}")
        return

    # 3. Load Inference Service
    model_service.load_models()
    
    # 4. Process a Sample Input
    raw_input = {
        "n": 60, "p": 45, "k": 40, 
        "temperature": 28, "humidity": 75, "ph": 6.5, "rainfall": 10
    }
    processed = data_processor.process_pipeline(raw_input)
    
    vec_minmax = np.array(processed['vectors']['minmax'])
    vec_std = np.array(processed['vectors']['std'])
    
    # 5. Predict
    print("\n--- Prediction Results ---")
    crop = model_service.predict_crop(vec_minmax)
    fert = model_service.predict_fertilizer(vec_std)
    irrig = model_service.predict_irrigation(vec_minmax)
    
    print(f"Crop: {crop}")
    print(f"Fertilizer: {fert}")
    print(f"Irrigation: {irrig}")
    
    # Basic Checks
    if crop['confidence'] == 0: print("FAIL: TabNet prediction failed")
    else: print("PASS: TabNet")
    
    if fert['n'] == 0 and fert['p'] == 0: print("WARN: SwiFT might be predicting zeros or not loaded") # Zeros are possible but unlikely for all
    else: print("PASS: SwiFT")
    
    if irrig['irrigation_hours'] >= 0: print("PASS: TTL")
    else: print("FAIL: TTL negative output")

if __name__ == "__main__":
    verify()
