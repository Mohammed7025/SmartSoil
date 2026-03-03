import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import pickle
import sys
import kagglehub

# Ensure we can import architecture
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models.architectures import TTLModel

# Configuration
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "ttl_irrigation_model.pth")
ENCODER_PATH = os.path.join(MODEL_DIR, "ttl_label_encoder.pkl")
os.makedirs(MODEL_DIR, exist_ok=True)

class IrrigationDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def train_ttl():
    print("--- Training TTL (Irrigation Status) ---")
    
    # 1. Load Data
    try:
        path = kagglehub.dataset_download("chineduchukwuemeka/smart-irrigation-data-derive-dataset")
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if not files:
            print("No CSV found.")
            return
        df = pd.read_csv(os.path.join(path, files[0]))
        print(f"Loaded dataset keys: {df.columns.tolist()}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Normalize cols
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Features: temperature, pressure, soilmiosture
    # Map soilmiosture -> moisture
    if 'soilmiosture' in df.columns:
        df['moisture'] = df['soilmiosture']
    
    # Select features
    # API will provide: temperature, humidity, moisture, pressure?
    # Dataset has: temperature, pressure, moisture.
    # We will usage these 3 features.
    features = ['temperature', 'pressure', 'moisture']
    target = 'status' # 'class' seems to be same or similar? 'status' has 'Dry'/'Wet'.
    
    # Handle mising
    df = df.dropna(subset=features + [target])
    
    X = df[features].values
    y = df[target].values
    
    # Preprocessing (MinMax)
    # T(0-50), P(900-1100?), M(0-100) / (0-1024?)
    # Let's simple usage training data min/max
    mins = X.min(axis=0)
    maxs = X.max(axis=0)
    print(f"Stats: Mins={mins}, Maxs={maxs}")
    
    X_norm = (X - mins) / (maxs - mins + 1e-6)
    
    # Encode Target
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    print(f"Classes: {encoder.classes_}")
    
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoder, f)
        
    X_train, X_val, y_train, y_val = train_test_split(X_norm, y_encoded, test_size=0.2, random_state=42)
    
    train_ds = IrrigationDataset(X_train, y_train)
    val_ds = IrrigationDataset(X_val, y_val)
    
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32)
    
    # Initialize Model
    # input_dim=3 (Temp, Press, Moist)
    # output_dim=num_classes
    num_classes = len(encoder.classes_)
    model = TTLModel(input_dim=3, output_dim=num_classes)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Train Loop
    epochs = 20
    best_loss = float('inf')
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for X_b, y_b in train_loader:
            optimizer.zero_grad()
            out = model(X_b)
            loss = criterion(out, y_b)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
        # Val
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        with torch.no_grad():
            for X_b, y_b in val_loader:
                out = model(X_b)
                loss = criterion(out, y_b)
                val_loss += loss.item()
                _, predicted = torch.max(out.data, 1)
                total += y_b.size(0)
                correct += (predicted == y_b).sum().item()
        
        avg_train = train_loss / len(train_loader)
        avg_val = val_loss / len(val_loader)
        acc = 100 * correct / total
        
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {avg_train:.4f} | Val Loss: {avg_val:.4f} | Acc: {acc:.2f}%")
        
        if avg_val < best_loss:
            best_loss = avg_val
            torch.save(model.state_dict(), MODEL_PATH)
            
    print(f"Training Complete. Saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_ttl()
