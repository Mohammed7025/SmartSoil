import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import os
import pickle
import kagglehub
from kagglehub import KaggleDatasetAdapter
from models.architectures import SwiFTModel, TTLModel
# Check imports: TabNetClassifier is usually from pytorch_tabnet.tab_model
from pytorch_tabnet.tab_model import TabNetClassifier
import sys

# Constants - Update paths to be relative to where script is run or absolute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# SwiFT Crop
SWIFT_MODEL_PATH = os.path.join(MODEL_DIR, "swift_crop_model.pth")
SWIFT_ENCODER_PATH = os.path.join(MODEL_DIR, "swift_crop_label_encoder.pkl")
SWIFT_SCALER_PATH = os.path.join(MODEL_DIR, "swift_scaler_params.pkl")

# TabNet Fertilizer
TABNET_MODEL_PATH = os.path.join(MODEL_DIR, "tabnet_fertilizer_prediction.zip")
TABNET_ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_label_encoder.pkl")

# TTL Irrigation
TTL_MODEL_PATH = os.path.join(MODEL_DIR, "ttl_irrigation_model.pth")
TTL_ENCODER_PATH = os.path.join(MODEL_DIR, "ttl_label_encoder.pkl")

# Constants for Cached Datasets
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "kagglehub", "datasets")
CROP_DATA_PATH = os.path.join(CACHE_DIR, "atharvaingle", "crop-recommendation-dataset", "versions", "1", "Crop_recommendation.csv")
FERT_DATA_PATH = os.path.join(CACHE_DIR, "irakozekelly", "fertilizer-prediction", "versions", "1", "Fertilizer Prediction.csv")
IRRI_DATA_PATH = os.path.join(CACHE_DIR, "chineduchukwuemeka", "smart-irrigation-data-derive-dataset", "versions", "2", "data.csv")
# Note: Irrigation path version might differ, checking file existence logic below is better.

def evaluate_swift_crop():
    print("\n" + "="*50)
    print("Evaluating SwiFT (Crop Recommendation) - Optimized")
    print("="*50)

    # 1. Load Data
    try:
        print("Loading Crop Data from Cache...")
        if os.path.exists(CROP_DATA_PATH):
             df = pd.read_csv(CROP_DATA_PATH)
        else:
             print("Cache not found, trying download...")
             path = kagglehub.dataset_download("atharvaingle/crop-recommendation-dataset")
             files = [f for f in os.listdir(path) if f.endswith('.csv')]
             df = pd.read_csv(os.path.join(path, files[0]))
    except Exception as e:
        print(f"Failed to load crop dataset: {e}")
        return

    df = df.rename(columns={"N": "nitrogen", "P": "phosphorus", "K": "potassium", "label": "crop"})

    # 2. Skip Pre-filtering (Matches new training logic)
    print("Skipping pre-filtering (using full dataset)...")
    
    # 3. Feature Engineering
    print("Feature Engineering...")
    def get_season(row):
        if row['rainfall'] > 100: return 0
        elif row['temperature'] < 25: return 1
        else: return 2
    
    df['season'] = df.apply(get_season, axis=1)
    df["npk_ratio"] = (df["nitrogen"] + df["phosphorus"] + df["potassium"]) / 3
    df["heat_index"] = df["temperature"] * df["humidity"]
    df["soil_health"] = df["ph"] + (df["npk_ratio"] / 100.0)

    CONTINUOUS_COLS = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'npk_ratio', 'heat_index', 'soil_health']
    CATEGORICAL_COLS = ['season']
    
    X_cont = df[CONTINUOUS_COLS].values
    X_cat = df[CATEGORICAL_COLS].values
    y_labels = df['crop'].values

    # 4. Normalization (Standardization)
    if os.path.exists(SWIFT_SCALER_PATH):
        print("Loading scaler params...")
        with open(SWIFT_SCALER_PATH, "rb") as f:
            scaler_params = pickle.load(f)
            mean_vals = scaler_params['mean']
            std_vals = scaler_params['std']
            X_cont = (X_cont - mean_vals) / (std_vals + 1e-6)
    else:
        print("Warning: SwiFT scaler params not found. Using current data stats.")
        mean_vals = X_cont.mean(axis=0)
        std_vals = X_cont.std(axis=0)
        X_cont = (X_cont - mean_vals) / (std_vals + 1e-6)

    # 5. Load Encoder & Model
    if not os.path.exists(SWIFT_ENCODER_PATH):
        print(f"Encoder not found at {SWIFT_ENCODER_PATH}")
        return

    with open(SWIFT_ENCODER_PATH, "rb") as f:
        encoder = pickle.load(f)
    
    y = encoder.transform(y_labels)
    num_classes = len(encoder.classes_)
    print(f"Classes: {num_classes}")

    # Instantiate Model (New Architecture)
    model = SwiFTModel(
        num_continuous=len(CONTINUOUS_COLS),
        num_categories=[3],
        embedding_dims=[8],
        hidden_layers=[256, 128, 64],
        output_dim=num_classes,
        dropout_rate=0.3
    )
    
    if os.path.exists(SWIFT_MODEL_PATH):
        print("Loading model weights...")
        model.load_state_dict(torch.load(SWIFT_MODEL_PATH))
        model.eval()
        
        # 6. Inference
        with torch.no_grad():
            X_cont_tensor = torch.tensor(X_cont, dtype=torch.float32)
            X_cat_tensor = torch.tensor(X_cat, dtype=torch.long)
            logits = model(X_cont_tensor, X_cat_tensor)
            preds = torch.argmax(logits, dim=1).numpy()
            
        print("Classification Report:")
        target_names = [str(c) for c in encoder.classes_]
        print(classification_report(y, preds, target_names=target_names, zero_division=0))
        print(f"Accuracy: {accuracy_score(y, preds):.4f}")
    else:
        print(f"Model not found at {SWIFT_MODEL_PATH}")

# SwiFT Fertilizer
SWIFT_FERT_MODEL_PATH = os.path.join(MODEL_DIR, "swift_fertilizer_model.pth")
FERT_ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_label_encoder.pkl")
FERT_SCALER_PATH = os.path.join(MODEL_DIR, "swift_fertilizer_scaler.pkl")
SOIL_ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_soil_encoder.pkl")
FERT_CROP_ENCODER_PATH = os.path.join(MODEL_DIR, "fertilizer_crop_encoder.pkl")

def evaluate_swift_fertilizer():
    print("\n" + "="*50)
    print("Evaluating SwiFT (Fertilizer Classification) - Upgrade")
    print("="*50)

    try:
        print("Loading Fertilizer Data (Augmented)...")
        data_path = "backend/data/fertilizer_augmented.csv"
        # If not found, fallback to cache? No, let's assume it exists.
        df = pd.read_csv(data_path)
    except Exception as e:
        print(f"Failed to load fertilizer data: {e}")
        return

    # Clean headers (already clean in augmented csv, but safe to keep)
    df.columns = [c.strip() for c in df.columns]
    
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
    df = df.rename(columns=rename_map)
    
    CONTINUOUS_COLS = ['n', 'p', 'k', 'temperature', 'humidity', 'moisture']
    CATEGORICAL_COLS = ['soil_type', 'crop_type']
    
    X_cont = df[CONTINUOUS_COLS].values.astype(float)
    X_cat_raw = df[CATEGORICAL_COLS].values
    y_labels = df['fertilizer'].values
    
    # Normalization (Standardization)
    if os.path.exists(FERT_SCALER_PATH):
        print("Loading scaler params...")
        with open(FERT_SCALER_PATH, "rb") as f:
            scaler_params = pickle.load(f)
            mean_vals = scaler_params['mean']
            std_vals = scaler_params['std']
            X_cont = (X_cont - mean_vals) / (std_vals + 1e-6)
    else:
        print("Scaler not found, using raw statistics.")
        mean_vals = X_cont.mean(axis=0)
        std_vals = X_cont.std(axis=0)
        X_cont = (X_cont - mean_vals) / (std_vals + 1e-6)

    # Encoders
    if not (os.path.exists(FERT_ENCODER_PATH) and os.path.exists(SOIL_ENCODER_PATH) and os.path.exists(FERT_CROP_ENCODER_PATH)):
        print("Encoders not found.")
        return
        
    with open(FERT_ENCODER_PATH, "rb") as f: target_encoder = pickle.load(f)
    with open(SOIL_ENCODER_PATH, "rb") as f: soil_encoder = pickle.load(f)
    with open(FERT_CROP_ENCODER_PATH, "rb") as f: crop_encoder = pickle.load(f)
    
    y = target_encoder.transform(y_labels)
    
    try:
        soil_encoded = soil_encoder.transform(X_cat_raw[:, 0])
        crop_encoded = crop_encoder.transform(X_cat_raw[:, 1])
    except Exception as e:
        print(f"Encoding error (unseen labels?): {e}")
        return
        
    X_cat = np.stack([soil_encoded, crop_encoded], axis=1)
    
    num_classes = len(target_encoder.classes_)
    num_soil = len(soil_encoder.classes_)
    num_crop = len(crop_encoder.classes_)
    
    # Model
    model = SwiFTModel(
        num_continuous=len(CONTINUOUS_COLS), # 6
        num_categories=[num_soil, num_crop],
        embedding_dims=[4, 8],
        hidden_layers=[128, 64],
        output_dim=num_classes,
        dropout_rate=0.3
    )

    if os.path.exists(SWIFT_FERT_MODEL_PATH):
        print("Loading model...")
        model.load_state_dict(torch.load(SWIFT_FERT_MODEL_PATH))
        model.eval()
        
        with torch.no_grad():
            X_cont_tensor = torch.tensor(X_cont, dtype=torch.float32)
            X_cat_tensor = torch.tensor(X_cat, dtype=torch.long)
            logits = model(X_cont_tensor, X_cat_tensor)
            preds = torch.argmax(logits, dim=1).numpy()
            
        print("Classification Report:")
        target_names = [str(c) for c in target_encoder.classes_]
        print(classification_report(y, preds, target_names=target_names, zero_division=0))
        print(f"Accuracy: {accuracy_score(y, preds):.4f}")
    else:
        print(f"Model not found at {SWIFT_FERT_MODEL_PATH}")

def evaluate_ttl_irrigation():
    print("\n" + "="*50)
    print("Evaluating TTL (Irrigation Status)")
    print("="*50)

    try:
        print("Loading Irrigation Data from Cache...")
        if os.path.exists(IRRI_DATA_PATH):
             df = pd.read_csv(IRRI_DATA_PATH)
        else:
             print("Cache not found, trying download...")
             path = kagglehub.dataset_download("chineduchukwuemeka/smart-irrigation-data-derive-dataset")
             files = [f for f in os.listdir(path) if f.endswith('.csv')]
             df = pd.read_csv(os.path.join(path, files[0]))
    except Exception as e:
        print(f"Failed to load irrigation data: {e}")
        return

    df.columns = [c.lower().strip() for c in df.columns]
    if 'soilmiosture' in df.columns:
        df['moisture'] = df['soilmiosture']
    
    features = ['temperature', 'pressure', 'moisture']
    df = df.dropna(subset=features + ['status']) 
    X = df[features].values
    y_labels = df['status'].values
    
    # Normalization 
    mins = X.min(axis=0)
    maxs = X.max(axis=0)
    X_norm = (X - mins) / (maxs - mins + 1e-6)

    # Encoder
    TTL_ENCODER_PATH = os.path.join(MODEL_DIR, "ttl_label_encoder.pkl")
    if os.path.exists(TTL_ENCODER_PATH):
        print("Loading encoder...")
        with open(TTL_ENCODER_PATH, "rb") as f:
            encoder = pickle.load(f)
        y = encoder.transform(y_labels)
    else:
        print("TTL Encoder not found.")
        return

    num_classes = len(encoder.classes_)
    # Correct input dim is 3
    model = TTLModel(input_dim=3, output_dim=num_classes)
    
    TTL_MODEL_PATH = os.path.join(MODEL_DIR, "ttl_irrigation_model.pth")
    if os.path.exists(TTL_MODEL_PATH):
        print("Loading model...")
        model.load_state_dict(torch.load(TTL_MODEL_PATH))
        model.eval()
        
        with torch.no_grad():
            X_tensor = torch.tensor(X_norm, dtype=torch.float32)
            logits = model(X_tensor)
            preds = torch.argmax(logits, dim=1).numpy()
            
        print("Classification Report:")
        target_names = [str(c) for c in encoder.classes_]
        print(classification_report(y, preds, target_names=target_names, zero_division=0))
        print(f"Accuracy: {accuracy_score(y, preds):.4f}")
    else:
        print(f"TTL Model not found at {TTL_MODEL_PATH}")

if __name__ == "__main__":
    evaluate_swift_crop()
    evaluate_swift_fertilizer()
    evaluate_ttl_irrigation()
