import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
import os
from models.architectures import TTLModel

# Configuration
DATA_PATH = "smart_soil_dataset.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "ttl_irrigation_model.pth")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_ttl():
    print("--- Training TTL (Irrigation Scheduling) ---")
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return
        
    df = pd.read_csv(DATA_PATH)
    
    feature_cols = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall_forecast']
    if 'rainfall_forecast' not in df.columns and 'rainfall' in df.columns:
         feature_cols[-1] = 'rainfall'

    X = df[feature_cols].values
    
    # Target: Irrigation Time/Amount
    if 'irrigation_hours' not in df.columns:
        df['irrigation_hours'] = 0.0 # Dummy
        
    y = df[['irrigation_hours']].values
    
    # 2. Preprocessing (Min-Max) - MATCHES TABNET/TTL logic in processing layer
    # N(0-200), P(0-200), K(0-200), T(0-50), H(0-100), ph(0-14), Rain(0-300)
    MINS = np.array([0, 0, 0, 0, 0, 0, 0])
    MAXS = np.array([200, 200, 200, 50, 100, 14, 300])
    
    X_norm = (X - MINS) / (MAXS - MINS + 1e-6)
    
    # Save SHAP background
    indices = np.random.choice(X_norm.shape[0], 100, replace=False)
    background_data = X_norm[indices]
    np.save(os.path.join(MODEL_DIR, "ttl_shap_background.npy"), background_data)
    
    X_tensor = torch.tensor(X_norm, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    
    X_train, X_val, y_train, y_val = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)
    
    # 3. Define Model
    model = TTLModel(input_dim=7, output_dim=1)
    criterion = nn.L1Loss() # MAE Loss as requested
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    
    # 4. Train
    print("Training TTL...")
    for epoch in range(50):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        
        if epoch % 5 == 0:
            model.eval()
            with torch.no_grad():
                val_loss = criterion(model(X_val), y_val)
            print(f"Epoch {epoch}: Train Loss {loss.item():.4f}, Val Loss {val_loss.item():.4f}")
            
    # 5. Save Model
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"TTL model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_ttl()
