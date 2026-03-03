import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
import os
from models.architectures import SwiFTModel

# Configuration
DATA_PATH = "smart_soil_dataset.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "swift_fertilizer_model.pth")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_swift():
    print("--- Training SwiFT (Fertilizer Recommendation) ---")
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Features: [N, P, K, T, H, pH, R]
    feature_cols = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall_forecast']
    if 'rainfall_forecast' not in df.columns and 'rainfall' in df.columns:
         feature_cols[-1] = 'rainfall'

    X = df[feature_cols].values
    
    # Targets: [N_new, P_new, K_new] 
    # For now, we simulate targets based on "ideal" values logic or existing columns if available.
    # We will assume columns 'fertilizer_n', 'fertilizer_p', 'fertilizer_k' exist or creates dummies.
    
    if 'fertilizer_k' not in df.columns:
        # Dummy if missing, just for script validty
        df['fertilizer_k'] = 0.0
    if 'fertilizer_n' not in df.columns:
        df['fertilizer_n'] = 0.0
    if 'fertilizer_p' not in df.columns:
        df['fertilizer_p'] = 0.0

    y = df[['fertilizer_n', 'fertilizer_p', 'fertilizer_k']].values
    
    # 2. Preprocessing (Standardization)
    # Using hardcoded MEAN/STD aligned with backend/utils/data_processing_layer.py
    MEAN = np.array([50.0, 50.0, 50.0, 25.0, 50.0, 6.5, 100.0])
    STD = np.array([20.0, 20.0, 20.0, 5.0, 20.0, 1.0, 50.0])
    
    X_std = (X - MEAN) / (STD + 1e-6)
    
    # Save SHAP background data
    indices = np.random.choice(X_std.shape[0], 100, replace=False)
    background_data = X_std[indices]
    np.save(os.path.join(MODEL_DIR, "swift_shap_background.npy"), background_data)
    
    # Convert to Tensors
    X_tensor = torch.tensor(X_std, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    
    # Split
    X_train, X_val, y_train, y_val = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)
    
    # 3. Define Model
    model = SwiFTModel(input_dim=7, output_dim=3)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    
    # 4. Train
    print("Training loop...")
    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            model.eval()
            with torch.no_grad():
                val_loss = criterion(model(X_val), y_val)
            print(f"Epoch {epoch}: Train Loss {loss.item():.4f}, Val Loss {val_loss.item():.4f}")
            
    # 5. Save Model
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"SwiFT model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_swift()
