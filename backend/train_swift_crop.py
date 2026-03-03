import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import pickle
import kagglehub
from kagglehub import KaggleDatasetAdapter
from models.architectures import SwiFTModel

# Configuration
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "swift_crop_model.pth")
ENCODER_PATH = os.path.join(MODEL_DIR, "swift_crop_label_encoder.pkl")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_swift_crop():
    print("--- Training SwiFT (Crop Recommendation) Optimized ---")
    
    # 1. Load Data
    try:
        print("Downloading/Loading dataset from Kaggle...")
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "atharvaingle/crop-recommendation-dataset",
            "Crop_recommendation.csv",
        )
        print(f"Dataset Loaded. Shape: {df.shape}")
        
        # Rename columns standard
        df = df.rename(columns={
            "N": "nitrogen", "P": "phosphorus", "K": "potassium", "label": "crop"
        })
    except Exception as e:
        print(f"Error loading Kaggle dataset: {e}")
        return

    # --- Step 1: Pre-filter Crops (Business Rules) ---
    print("Skipping Pre-filtering Rules to use full dataset...")
    # original_size = len(df)
    
    # # Rule 1: Remove Wheat/Barley if Temp > 35 (Too hot)
    # criteria_hot = (df['temperature'] > 35) & (df['crop'].isin(['wheat', 'barley'])) # Check crop names in dataset
    # df = df[~criteria_hot]
    
    # # Rule 2: Remove Rice if Rainfall < 100 (Needs water)
    # criteria_dry_rice = (df['rainfall'] < 100) & (df['crop'] == 'rice')
    # df = df[~criteria_dry_rice]
    
    # # Rule 3: Remove Banana/Mango if Humidity < 30 (Tropics)
    # criteria_dry_fruit = (df['humidity'] < 30) & (df['crop'].isin(['banana', 'mango']))
    # df = df[~criteria_dry_fruit]
    
    # print(f"Removed {original_size - len(df)} rows based on agronomic rules.")

    # --- Step 2: Feature Engineering ---
    print("Generating Derived Features...")
    
    # 1. Season Heuristic
    # Kharif: High Rain (>100)
    # Rabi: Low Temp (<25) & Low Rain
    # Zaid: High Temp & Low Rain
    def get_season(row):
        if row['rainfall'] > 100:
            return 0 # Kharif
        elif row['temperature'] < 25:
            return 1 # Rabi
        else:
            return 2 # Zaid

    df['season'] = df.apply(get_season, axis=1)
    
    # 2. Other Features
    df["npk_ratio"] = (df["nitrogen"] + df["phosphorus"] + df["potassium"]) / 3
    df["heat_index"] = df["temperature"] * df["humidity"]
    df["soil_health"] = df["ph"] + (df["npk_ratio"] / 100.0)
    
    # Define Column Groups
    CATEGORICAL_COLS = ['season']
    CONTINUOUS_COLS = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'npk_ratio', 'heat_index', 'soil_health']
    
    # --- Step 3: Normalization (Continuous ONLY) ---
    print("Normalizing Continuous Features (Standardization)...")
    X_cont = df[CONTINUOUS_COLS].values
    
    # Statistics for Standardization (Mean/Std)
    mean_vals = X_cont.mean(axis=0)
    std_vals = X_cont.std(axis=0)
    
    # Save scalers for inference
    scaler_params = {'mean': mean_vals, 'std': std_vals}
    with open(os.path.join(MODEL_DIR, "swift_scaler_params.pkl"), "wb") as f:
        pickle.dump(scaler_params, f)
        
    X_cont_norm = (X_cont - mean_vals) / (std_vals + 1e-6)
    
    # Categorical Data
    X_cat = df[CATEGORICAL_COLS].values # (N, 1)

    # Encode Targets
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(df['crop'])
    num_classes = len(encoder.classes_)
    print(f"Training on {num_classes} crop classes.")
    
    # Save Encoder
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoder, f)

    # --- Step 4: Class Weighting ---
    from sklearn.utils import class_weight
    class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_encoded), y=y_encoded)
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
    print("Class weights computed.")

    # --- Convert to Tensors & Split ---
    X_cont_tensor = torch.tensor(X_cont_norm, dtype=torch.float32)
    X_cat_tensor = torch.tensor(X_cat, dtype=torch.long)
    y_tensor = torch.tensor(y_encoded, dtype=torch.long)
    
    # Split
    # Since we have two Inputs (Cont, Cat), we split indices instead
    indices = np.arange(len(df))
    train_idx, val_idx = train_test_split(indices, test_size=0.1, random_state=42) # Increased training data
    
    # Arrays
    X_cont_train, X_cont_val = X_cont_tensor[train_idx], X_cont_tensor[val_idx]
    X_cat_train, X_cat_val = X_cat_tensor[train_idx], X_cat_tensor[val_idx]
    y_train, y_val = y_tensor[train_idx], y_tensor[val_idx]
    
    # --- Step 5: Define SwiFT Model ---
    model = SwiFTModel(
        num_continuous=len(CONTINUOUS_COLS),
        num_categories=[3], # Season has 3 classes
        embedding_dims=[8], 
        # Increased capacity
        hidden_layers=[256, 128, 64], 
        output_dim=num_classes,
        dropout_rate=0.3 # Slightly higher dropout
    )
    
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=20, verbose=True)

    # --- Training Loop ---
    print("Starting Training...")
    epochs = 300
    best_acc = 0.0
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        logits = model(X_cont_train, X_cat_train)
        loss = criterion(logits, y_train)
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            model.eval()
            with torch.no_grad():
                val_logits = model(X_cont_val, X_cat_val)
                # Accuracy
                preds = torch.argmax(val_logits, dim=1)
                acc = (preds == y_val).float().mean()
                
            scheduler.step(acc)
            
            if acc > best_acc:
                best_acc = acc
                torch.save(model.state_dict(), MODEL_PATH)
                print(f"Epoch {epoch}: New Best Val Acc: {acc:.4f} - Saved")
            else:
                print(f"Epoch {epoch}: Val Acc: {acc:.4f} (Best: {best_acc:.4f})")
                
    print(f"Training Complete. Best Accuracy: {best_acc:.4f}")
    if best_acc < 0.9:
        print("Warning: Accuracy is below 90%. Review params.")
        
if __name__ == "__main__":
    train_swift_crop()
