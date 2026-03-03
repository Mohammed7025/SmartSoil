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
from models.architectures import SwiFTModel

# Configuration
MODEL_DIR = "backend/models" # Save directly to backend/models
MODEL_PATH = os.path.join(MODEL_DIR, "swift_fertilizer_model.pth")
ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_label_encoder.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "swift_fertilizer_scaler.pkl")
SOIL_ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_soil_encoder.pkl")
CROP_TYPE_ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_crop_encoder.pkl")

# Ensure directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def train_swift_fertilizer():
    print("--- Training SwiFT (Fertilizer Classification) - Augmented Data ---")
    
    # 1. Load Data
    try:
        data_path = "backend/data/fertilizer_augmented.csv"
        if not os.path.exists(data_path):
            print(f"Data not found at {data_path}. Run augment_fertilizer_data.py first.")
            return

        print(f"Loading dataset from {data_path}...")
        df = pd.read_csv(data_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Columns already clean from augmentation script
    print("Columns:", df.columns.tolist())
    
    # Features: N, P, K, Temp, Humidity, Moisture (Cont) + Soil Type, Crop Type (Cat)
    # Ensure column names match what we expect
    rename_map = {
        'Temparature': 'temperature', 
        'Humidity': 'humidity', 
        'Moisture': 'moisture',
        'Nitrogen': 'n',
        'Phosphorous': 'p', 
        'Potassium': 'k', 
        'Fertilizer Name': 'fertilizer',
        'Soil Type': 'soil_type', 
        'Crop Type': 'crop_type'
    }
    # Only rename if keys exist (augmentation script already renamed them, but safety check)
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
    print("Columns:", df.columns.tolist())
    
    # Features: N, P, K, Temp, Humidity, Moisture (Cont) + Soil Type, Crop Type (Cat)
    CONTINUOUS_COLS = ['n', 'p', 'k', 'temperature', 'humidity', 'moisture']
    CATEGORICAL_COLS = ['soil_type', 'crop_type']
    TARGET_COL = 'fertilizer'
    
    X_cont = df[CONTINUOUS_COLS].values.astype(float)
    X_cat_raw = df[CATEGORICAL_COLS].values
    y_raw = df[TARGET_COL].values
    
    # 2. Normalization (Standardization)
    print("Normalizing (Standardization)...")
    mean_vals = X_cont.mean(axis=0)
    std_vals = X_cont.std(axis=0)
    
    scaler_params = {'mean': mean_vals, 'std': std_vals}
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler_params, f)
        
    X_cont_norm = (X_cont - mean_vals) / (std_vals + 1e-6)
    
    # 3. Encoding Categorical Features
    print("Encoding Categorical Features...")
    soil_encoder = LabelEncoder()
    crop_encoder = LabelEncoder()
    
    # Soil Type
    soil_encoded = soil_encoder.fit_transform(X_cat_raw[:, 0])
    with open(SOIL_ENCODER_PATH, "wb") as f:
        pickle.dump(soil_encoder, f)
        
    # Crop Type
    crop_encoded = crop_encoder.fit_transform(X_cat_raw[:, 1])
    with open(CROP_TYPE_ENCODER_PATH, "wb") as f:
        pickle.dump(crop_encoder, f)
        
    X_cat_encoded = np.stack([soil_encoded, crop_encoded], axis=1)
    
    num_soil_classes = len(soil_encoder.classes_)
    num_crop_classes = len(crop_encoder.classes_)
    print(f"Soil Types: {num_soil_classes}, Crop Types: {num_crop_classes}")
    
    # 4. Encoding Target
    target_encoder = LabelEncoder()
    y_encoded = target_encoder.fit_transform(y_raw)
    num_classes = len(target_encoder.classes_)
    print(f"Classes ({num_classes}): {target_encoder.classes_}")
    
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(target_encoder, f)

    # 5. Class Weights
    from sklearn.utils import class_weight
    class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_encoded), y=y_encoded)
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)

    # 6. Split
    indices = np.arange(len(df))
    train_idx, val_idx = train_test_split(indices, test_size=0.1, random_state=42)
    
    # Tensors
    X_cont_train = torch.tensor(X_cont_norm[train_idx], dtype=torch.float32)
    X_cont_val = torch.tensor(X_cont_norm[val_idx], dtype=torch.float32)
    
    X_cat_train = torch.tensor(X_cat_encoded[train_idx], dtype=torch.long)
    X_cat_val = torch.tensor(X_cat_encoded[val_idx], dtype=torch.long)
    
    y_train = torch.tensor(y_encoded[train_idx], dtype=torch.long)
    y_val = torch.tensor(y_encoded[val_idx], dtype=torch.long)

    # DataLoader - Using smaller batch size for small dataset
    from torch.utils.data import TensorDataset, DataLoader
    train_dataset = TensorDataset(X_cont_train, X_cat_train, y_train)
    val_dataset = TensorDataset(X_cont_val, X_cat_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True) # Batch 16 for 99 rows
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # 7. Model
    model = SwiFTModel(
        num_continuous=len(CONTINUOUS_COLS), # 6
        num_categories=[num_soil_classes, num_crop_classes], 
        embedding_dims=[4, 8], 
        hidden_layers=[128, 64],
        output_dim=num_classes,
        dropout_rate=0.3
    )
    
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=10, verbose=True)

    # 8. Train
    print("Starting Training (Mini-Batch)...")
    epochs = 100
    best_acc = 0.0
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_x_cont, batch_x_cat, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x_cont, batch_x_cat)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        avg_loss = total_loss / len(train_loader)
        
        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for batch_x_cont, batch_x_cat, batch_y in val_loader:
                val_logits = model(batch_x_cont, batch_x_cat)
                preds = torch.argmax(val_logits, dim=1)
                correct += (preds == batch_y).sum().item()
                total += batch_y.size(0)
        
        acc = correct / total
        scheduler.step(acc)
        
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), MODEL_PATH)
            print(f"Epoch {epoch}: Loss {avg_loss:.4f} | New Best Val Acc: {acc:.4f} - Saved")
        elif epoch % 5 == 0:
            print(f"Epoch {epoch}: Loss {avg_loss:.4f} | Val Acc: {acc:.4f}")
                
    print(f"Training Complete. Best Accuracy: {best_acc:.4f}")

if __name__ == "__main__":
    train_swift_fertilizer()
