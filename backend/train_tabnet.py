import pandas as pd
import numpy as np
import torch
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import pickle

# Configuration
DATA_PATH = "smart_soil_dataset.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "tabnet_crop_model.pth")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_tabnet():
    print("--- Training TabNet (Crop Recommendation) ---")
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Features & Target
    # Ensure these match the DataProcessor logic
    feature_cols = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall_forecast']
    if 'rainfall_forecast' not in df.columns and 'rainfall' in df.columns:
         feature_cols[-1] = 'rainfall'

    X = df[feature_cols].values
    y = df['crop'].values # String labels
    
    # 2. Preprocessing (Min-Max Normalization logic implied or explicit)
    # We will use explicit stats aligned with DataProcessor for the model to learn correctly
    # stats linked to backend/utils/data_processing_layer.py
    # For training simplicity, we assume the dataset is raw and we apply the transformation 
    # that the inference time DataProcessor will use.
    
    # Using hardcoded min/max typical for this domain to normalize 0-1
    # N(0-200), P(0-200), K(0-200), T(0-50), H(0-100), ph(0-14), Rain(0-300)
    MINS = np.array([0, 0, 0, 0, 0, 0, 0])
    MAXS = np.array([200, 200, 200, 50, 100, 14, 300])
    
    X_norm = (X - MINS) / (MAXS - MINS + 1e-6)
    
    # Encode Target
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    
    # Save Encoder for Inference
    with open(os.path.join(MODEL_DIR, "crop_label_encoder.pkl"), "wb") as f:
        pickle.dump(encoder, f)
        
    # Ensure X_norm is 2D
    if X_norm.ndim == 1:
        X_norm = X_norm.reshape(-1, 1)
        
    # Save SHAP background data (Summary of training data, e.g., k-means or random sample)
    # Saving 100 random samples
    if X_norm.shape[0] > 100:
        indices = np.random.choice(X_norm.shape[0], 100, replace=False)
        background_data = X_norm[indices]
    else:
        background_data = X_norm
    np.save(os.path.join(MODEL_DIR, "tabnet_shap_background.npy"), background_data)

    # Split
    X_train, X_val, y_train, y_val = train_test_split(X_norm, y_encoded, test_size=0.2, random_state=42)
    
    # 3. Define Model
    # TabNetClassifier internally handles the architecture
    clf = TabNetClassifier(
        optimizer_fn=torch.optim.Adam,
        optimizer_params=dict(lr=2e-2),
        scheduler_params={"step_size": 10, "gamma": 0.9},
        scheduler_fn=torch.optim.lr_scheduler.StepLR,
        mask_type='entmax', # Sparse features
        verbose=1
    )
    
    # 4. Train
    clf.fit(
        X_train=X_train, y_train=y_train,
        eval_set=[(X_val, y_val)],
        eval_name=['val'],
        eval_metric=['accuracy'],
        max_epochs=100,
        patience=15,
        batch_size=256, 
        virtual_batch_size=128,
        num_workers=0,
        drop_last=False
    )
    
    # 5. Save Model
    # pytorch_tabnet saves as a zip file. We want strictly .pth if possible for weight loading,
    # but the library standard is save_model -> .zip.
    # To satisfy the ".pth" file request and simple torch loading, we can extract the state_dict.
    # However, TabNet is complex. We will save the library format model AND the state dict.
    
    clf.save_model(MODEL_PATH.replace(".pth", "")) # Saves as tabnet_crop_model.zip
    
    # Also save state dict for manual loading if needed
    torch.save(clf.network.state_dict(), MODEL_PATH)
    print(f"TabNet model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_tabnet()
