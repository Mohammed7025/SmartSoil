import pandas as pd
import numpy as np
import torch
import os
import pickle
import kagglehub
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from models.architectures import SwiFTModel, TTLModel

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "kagglehub", "datasets")

def get_multiclass_metrics(y_true, y_pred, labels):
    cm = confusion_matrix(y_true, y_pred, labels=range(len(labels)))
    metrics = []
    
    for i, label in enumerate(labels):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tn = cm.sum() - (tp + fp + fn)
        
        metrics.append({
            "Class": label,
            "TP": tp,
            "TN": tn,
            "FP": fp,
            "FN": fn,
            "Accuracy": (tp + tn) / (tp + tn + fp + fn),
            "Precision": tp / (tp + fp) if (tp + fp) > 0 else 0,
            "Recall": tp / (tp + fn) if (tp + fn) > 0 else 0,
            "F1-Score": 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        })
    return metrics

def evaluate_crop():
    print("\n--- Evaluating SwiFT Crop Recommendation ---")
    CROP_DATA_PATH = os.path.join(CACHE_DIR, "atharvaingle", "crop-recommendation-dataset", "versions", "1", "Crop_recommendation.csv")
    if not os.path.exists(CROP_DATA_PATH):
        path = kagglehub.dataset_download("atharvaingle/crop-recommendation-dataset")
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        df = pd.read_csv(os.path.join(path, files[0]))
    else:
        df = pd.read_csv(CROP_DATA_PATH)
    
    df = df.rename(columns={"N": "nitrogen", "P": "phosphorus", "K": "potassium", "label": "crop"})
    df['season'] = df.apply(lambda r: 0 if r['rainfall'] > 100 else (1 if r['temperature'] < 25 else 2), axis=1)
    df["npk_ratio"] = (df["nitrogen"] + df["phosphorus"] + df["potassium"]) / 3
    df["heat_index"] = df["temperature"] * df["humidity"]
    df["soil_health"] = df["ph"] + (df["npk_ratio"] / 100.0)

    CONTINUOUS_COLS = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'npk_ratio', 'heat_index', 'soil_health']
    X_cont = df[CONTINUOUS_COLS].values
    X_cat = df[['season']].values
    
    with open(os.path.join(MODEL_DIR, "swift_crop_label_encoder.pkl"), "rb") as f: encoder = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "swift_scaler_params.pkl"), "rb") as f: scaler = pickle.load(f)
    
    X_cont = (X_cont - scaler['mean']) / (scaler['std'] + 1e-6)
    y = encoder.transform(df['crop'].values)
    
    model = SwiFTModel(num_continuous=10, num_categories=[3], embedding_dims=[8], hidden_layers=[256, 128, 64], output_dim=len(encoder.classes_))
    model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "swift_crop_model.pth")))
    model.eval()
    
    with torch.no_grad():
        logits = model(torch.tensor(X_cont, dtype=torch.float32), torch.tensor(X_cat, dtype=torch.long))
        preds = torch.argmax(logits, dim=1).numpy()
    
    return get_multiclass_metrics(y, preds, encoder.classes_)

def evaluate_fertilizer():
    print("\n--- Evaluating SwiFT Fertilizer Prediction ---")
    df = pd.read_csv(os.path.join(DATA_DIR, "fertilizer_augmented.csv"))
    rename_map = {'Temparature': 'temperature', 'Humidity': 'humidity', 'Moisture': 'moisture', 'Nitrogen': 'n', 'Phosphorous': 'p', 'Potassium': 'k', 'Fertilizer Name': 'fertilizer', 'Soil Type': 'soil_type', 'Crop Type': 'crop_type'}
    df = df.rename(columns=rename_map)
    
    CONTINUOUS_COLS = ['n', 'p', 'k', 'temperature', 'humidity', 'moisture']
    X_cont = df[CONTINUOUS_COLS].values
    
    with open(os.path.join(MODEL_DIR, "fertilizer_label_encoder.pkl"), "rb") as f: target_encoder = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "fertilizer_soil_encoder.pkl"), "rb") as f: soil_encoder = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "fertilizer_crop_encoder.pkl"), "rb") as f: crop_encoder = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "swift_fertilizer_scaler.pkl"), "rb") as f: scaler = pickle.load(f)
    
    X_cont = (X_cont - scaler['mean']) / (scaler['std'] + 1e-6)
    soil_enc = soil_encoder.transform(df['soil_type'].values)
    crop_enc = crop_encoder.transform(df['crop_type'].values)
    X_cat = np.stack([soil_enc, crop_enc], axis=1)
    y = target_encoder.transform(df['fertilizer'].values)
    
    model = SwiFTModel(num_continuous=6, num_categories=[len(soil_encoder.classes_), len(crop_encoder.classes_)], embedding_dims=[4, 8], hidden_layers=[128, 64], output_dim=len(target_encoder.classes_))
    model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "swift_fertilizer_model.pth")))
    model.eval()
    
    with torch.no_grad():
        logits = model(torch.tensor(X_cont, dtype=torch.float32), torch.tensor(X_cat, dtype=torch.long))
        preds = torch.argmax(logits, dim=1).numpy()
        
    return get_multiclass_metrics(y, preds, target_encoder.classes_)

def evaluate_irrigation():
    print("\n--- Evaluating TTL Irrigation Status ---")
    IRRI_DATA_PATH = os.path.join(CACHE_DIR, "chineduchukwuemeka", "smart-irrigation-data-derive-dataset", "versions", "2", "data.csv")
    df = pd.read_csv(IRRI_DATA_PATH)
    df.columns = [c.lower().strip() for c in df.columns]
    features = ['temperature', 'pressure', 'soilmiosture' if 'soilmiosture' in df.columns else 'moisture']
    df = df.dropna(subset=features + ['status'])
    X = df[features].values
    X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-6)
    
    with open(os.path.join(MODEL_DIR, "ttl_label_encoder.pkl"), "rb") as f: encoder = pickle.load(f)
    y = encoder.transform(df['status'].values)
    
    model = TTLModel(input_dim=3, output_dim=len(encoder.classes_))
    model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "ttl_irrigation_model.pth")))
    model.eval()
    
    with torch.no_grad():
        logits = model(torch.tensor(X_norm, dtype=torch.float32))
        preds = torch.argmax(logits, dim=1).numpy()
        
    return get_multiclass_metrics(y, preds, encoder.classes_)

if __name__ == "__main__":
    results = {
        "Crop": evaluate_crop(),
        "Fertilizer": evaluate_fertilizer(),
        "Irrigation": evaluate_irrigation()
    }
    
    for name, r_list in results.items():
        print(f"\nResults for {name}:")
        df_res = pd.DataFrame(r_list)
        print(df_res.to_string(index=False))
        avg_acc = df_res['Accuracy'].mean()
        avg_f1 = df_res['F1-Score'].mean()
        print(f"Average Accuracy: {avg_acc:.4f}, Average F1: {avg_f1:.4f}")
