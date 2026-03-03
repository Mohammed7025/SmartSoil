import torch
import torch.nn as nn
import os
import pickle
import joblib
from pytorch_tabnet.tab_model import TabNetClassifier
# Import architecture from centralized definition to ensure weight compatibility
# Import architecture from centralized definition for new models
import sys
# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.architectures import SwiFTModel, TTLModel

# ---------------------------------------------------------
# Loader Logic
# ---------------------------------------------------------

_models = {
    "swift_crop": None,        # SwiFT Classifier for Crops
    "encoder_swift_crop": None, # Label Enc for SwiFT Crops
    "tabnet_crop": None,       # Legacy TabNet
    "encoder_crop": None,      # Legacy TabNet Encoder
    "swift_fert": None,        # REMOVED
    "ttl_irri": None,          # TTL Classifier (Irrigation)
    "encoder_ttl": None,       # Label Enc for TTL
    "tabnet_fert": None,
    "encoder_fert": None
}

def load_models():
    print("Loading REAL models...")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_path, "models")
    
    # 1. Load SwiFT (Crop Prediction) - NEW
    try:
        with open(os.path.join(models_dir, "swift_crop_label_encoder.pkl"), "rb") as f:
            _models["encoder_swift_crop"] = pickle.load(f)
        print("[OK] SwiFT Crop Label Encoder loaded.")

        num_classes = len(_models["encoder_swift_crop"].classes_)
        
        swift_crop = SwiFTModel(
            num_continuous=10, 
            num_categories=[3], 
            embedding_dims=[8], 
            hidden_layers=[64, 32], 
            output_dim=num_classes,
            dropout_rate=0.2
        )
        weights_path = os.path.join(models_dir, "swift_crop_model.pth")
        
        if os.path.exists(weights_path):
            swift_crop.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
            swift_crop.eval()
            _models["swift_crop"] = swift_crop
            print("[OK] SwiFT Crop Model loaded.")
        else:
            print(f"[ERROR] SwiFT Crop weights not found at {weights_path}")
            
    except Exception as e:
        print(f"[ERROR] Failed to load SwiFT Crop Model: {e}")

    # 3. Load TTL (Irrigation) - NEW (Classification)
    try:
        # Load Encoder first
        enc_path = os.path.join(models_dir, "ttl_label_encoder.pkl")
        if os.path.exists(enc_path):
            with open(enc_path, "rb") as f:
                _models["encoder_ttl"] = pickle.load(f)
            print("[OK] TTL Label Encoder loaded.")
            
            num_classes = len(_models["encoder_ttl"].classes_)
            # Input dim = 3 (Temp, Pressure, Moisture)
            ttl = TTLModel(input_dim=3, output_dim=num_classes)
            
            weights_path = os.path.join(models_dir, "ttl_irrigation_model.pth")
            if not os.path.exists(weights_path):
                 # Check legacy path just in case, though structure differs
                 weights_path = os.path.join(models_dir, "ttl_irrigation.pth")
                 
            if os.path.exists(weights_path):
                try:
                    ttl.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
                    ttl.eval()
                    _models["ttl_irri"] = ttl
                    print(f"[OK] TTL loaded from {os.path.basename(weights_path)}.")
                except RuntimeError as re:
                     print(f"[ERROR] TTL Architecture Mismatch (expected): {re}")
            else:
                print(f"[ERROR] TTL weights not found.")
        else:
            print(f"[ERROR] TTL Encoder not found at {enc_path}")
            
    except Exception as e:
        print(f"[ERROR] Failed to load TTL: {e}")
    
    # 4. Load Legacy TabNet (just in case)
    try:
        tabnet = TabNetClassifier()
        tab_path = os.path.join(models_dir, "tabnet_crop_model.zip")
        if os.path.exists(tab_path):
            tabnet.load_model(tab_path)
            _models["tabnet_crop"] = tabnet
            print("[OK] Legacy TabNet loaded.")
            
            # Load Encoder for Legacy TabNet
            enc_path = os.path.join(models_dir, "crop_label_encoder.pkl")
            if os.path.exists(enc_path):
                with open(enc_path, "rb") as f:
                    _models["encoder_crop"] = pickle.load(f)
                print("[OK] Legacy Crop Encoder loaded.")
            else:
                print(f"[WARNING] Legacy Crop Encoder not found at {enc_path}")
                
    except Exception as e:
        print(f"[ERROR] Failed to load Legacy TabNet: {e}")
        pass

    # 5. Load TabNet Fertilizer (NEW)
    try:
        tabnet_fert = TabNetClassifier()
        tab_fert_path = os.path.join(models_dir, "tabnet_fertilizer_prediction.zip")
        if os.path.exists(tab_fert_path):
            tabnet_fert.load_model(tab_fert_path)
            _models["tabnet_fert"] = tabnet_fert
            print("[OK] TabNet Fertilizer loaded.")
        else:
            print(f"[ERROR] TabNet Fertilizer path not found: {tab_fert_path}")
            
        # Encoder
        enc_path = os.path.join(models_dir, "fertilizer_label_encoder.pkl")
        if os.path.exists(enc_path):
            with open(enc_path, "rb") as f:
                _models["encoder_fert"] = pickle.load(f)
            print("[OK] Fertilizer Encoder loaded.")
    except Exception as e:
        print(f"[ERROR] Failed to load TabNet Fertilizer: {e}")

def get_model(name):
    return _models.get(name)
