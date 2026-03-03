import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import pickle
import kagglehub

# Configuration
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "tabnet_fertilizer_prediction.zip") # TabNet saves without extension usually, checking lib
ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_label_encoder.pkl")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_tabnet_fertilizer():
    print("--- Training TabNet (Fertilizer Prediction) ---")
    
    # 1. Load Data
    try:
        path = kagglehub.dataset_download("irakozekelly/fertilizer-prediction")
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if not files:
            print("No CSV found.")
            return
        df = pd.read_csv(os.path.join(path, files[0]))
        print(f"Loaded dataset keys: {df.columns.tolist()}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Normalizing column names to lowercase/strip
    df.columns = [c.strip() for c in df.columns]
    
    # Map to our standard keys if they differ slightly
    # Expected in dataset: Temparature, Humidity, Moisture, Soil Type, Crop Type, Nitrogen, Potassium, Phosphorous, Fertilizer Name
    # We want to usage: Nitrogen, Phosphorous, Potassium, Temparature, Humidity
    # We will ignore Soil Type and Crop Type for now if we can't provide them, 
    # OR we encourage the user to provide them. 
    # For now, let's train on numeric features available: N, P, K, Temp, Humidity, Moisture (if we treat Moisture as derived or 0)
    
    # Rename for consistency
    rename_map = {
        'Temparature': 'temperature',
        'Humidity': 'humidity',
        'Nitrogen': 'n',
        'Phosphorous': 'p',
        'Potassium': 'k',
        'Fertilizer Name': 'fertilizer'
    }
    df = df.rename(columns=rename_map)
    
    # Features to usage
    # We MUST usage features available at inference.
    # Our API has: n, p, k, temperature, humidity, (ph, rainfall - not in this dataset)
    # This dataset has: n, p, k, temperature, humidity, Moisture, Soil Type, Crop Type.
    # Intersection: n, p, k, temperature, humidity.
    feature_cols = ['n', 'p', 'k', 'temperature', 'humidity']
    target_col = 'fertilizer'
    
    print(f"Training on features: {feature_cols}")
    
    X = df[feature_cols].values
    y = df[target_col].values
    
    # 2. Preprocessing
    # Min-Max usually good for DL
    # using global bounds from earlier for n,p,k,temp,hum
    # N(0-200), P(0-200), K(0-200), T(0-50), H(0-100)
    MINS = np.array([0, 0, 0, 0, 0])
    MAXS = np.array([200, 200, 200, 50, 100])
    
    X_norm = (X - MINS) / (MAXS - MINS + 1e-6)
    
    # Encode Target
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoder, f)
        
    X_train, X_val, y_train, y_val = train_test_split(X_norm, y_encoded, test_size=0.2, random_state=42)
    
    # 3. Train
    clf = TabNetClassifier(verbose=1)
    clf.fit(
        X_train=X_train, y_train=y_train,
        eval_set=[(X_val, y_val)],
        max_epochs=100,
        patience=15,
        batch_size=256, 
        virtual_batch_size=128,
        num_workers=0,
        drop_last=False
    )
    
    # 4. Save
    clf.save_model(MODEL_PATH.replace(".zip", ""))
    print(f"TabNet Fertilizer model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_tabnet_fertilizer()
