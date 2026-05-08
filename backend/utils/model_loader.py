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
# (Reload Triggered)
# ---------------------------------------------------------

_models = {
    "swift_crop": None,        # SwiFT Classifier for Crops
    "encoder_swift_crop": None, # Label Enc for SwiFT Crops
    "tabnet_crop": None,       # Legacy TabNet
    "encoder_crop": None,      # Legacy TabNet Encoder
    "swift_fert": None,        # SwiFT Classifier for Fertilizer
    "ttl_irri": None,          # TTL Classifier (Irrigation)
    "encoder_ttl": None,       # Label Enc for TTL
    "tabnet_fert": None,
    "encoder_fert": None,      # Shared Label Encoder for Fertilizer
    "encoder_soil": None,      # Fertilizer Soil Type Encoder
    "encoder_crop_type": None  # Fertilizer Crop Type Encoder
}

def load_models():
    print("Loading REAL models...")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_path, "models")
    
    # 1. Load SwiFT (Crop Prediction)
    try:
        enc_path = os.path.join(models_dir, "swift_crop_label_encoder.pkl")
        if os.path.exists(enc_path):
            with open(enc_path, "rb") as f:
                _models["encoder_swift_crop"] = pickle.load(f)
            print("[OK] SwiFT Crop Label Encoder loaded.")

            num_classes = len(_models["encoder_swift_crop"].classes_)
            
            swift_crop = SwiFTModel(
                num_continuous=10, 
                num_categories=[3], 
                embedding_dims=[8], 
                hidden_layers=[256, 128, 64], 
                output_dim=num_classes,
                dropout_rate=0.3
            )
            weights_path = os.path.join(models_dir, "swift_crop_model.pth")
            
            if os.path.exists(weights_path):
                swift_crop.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
                swift_crop.eval()
                _models["swift_crop"] = swift_crop
                print("[OK] SwiFT Crop Model loaded.")
            else:
                print(f"[ERROR] SwiFT Crop weights not found.")
    except Exception as e:
        print(f"[ERROR] Failed to load SwiFT Crop Model: {e}")

    # 2. Load SwiFT (Fertilizer Prediction)
    try:
        # Load Encoders
        soil_enc_path = os.path.join(models_dir, "fertilizer_soil_encoder.pkl")
        crop_enc_path = os.path.join(models_dir, "fertilizer_crop_encoder.pkl")
        fert_enc_path = os.path.join(models_dir, "fertilizer_label_encoder.pkl")
        
        if all(os.path.exists(p) for p in [soil_enc_path, crop_enc_path, fert_enc_path]):
            with open(soil_enc_path, "rb") as f: _models["encoder_soil"] = pickle.load(f)
            with open(crop_enc_path, "rb") as f: _models["encoder_crop_type"] = pickle.load(f)
            with open(fert_enc_path, "rb") as f: _models["encoder_fert"] = pickle.load(f)
            print("[OK] SwiFT Fertilizer Encoders loaded.")
            
            num_soil = len(_models["encoder_soil"].classes_)
            num_crop = len(_models["encoder_crop_type"].classes_)
            num_classes = len(_models["encoder_fert"].classes_)
            
            swift_fert = SwiFTModel(
                num_continuous=6, 
                num_categories=[num_soil, num_crop], 
                embedding_dims=[4, 8], 
                hidden_layers=[128, 64], 
                output_dim=num_classes,
                dropout_rate=0.3
            )
            weights_path = os.path.join(models_dir, "swift_fertilizer_model.pth")
            if os.path.exists(weights_path):
                swift_fert.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
                swift_fert.eval()
                _models["swift_fert"] = swift_fert
                print("[OK] SwiFT Fertilizer Model loaded.")
            else:
                print("[ERROR] SwiFT Fertilizer weights not found.")
    except Exception as e:
        print(f"[ERROR] Failed to load SwiFT Fertilizer: {e}")

    # 3. Load SwiFT (Irrigation) [Replaces TTL]
    try:
        enc_path = os.path.join(models_dir, "swift_irrigation_encoders.pkl")
        if os.path.exists(enc_path):
            with open(enc_path, "rb") as f:
                irr_data = pickle.load(f)
                _models["encoder_irrigation"] = irr_data
            print("[OK] SwiFT Irrigation Encoders loaded.")
            
            encoders = irr_data["encoders"]
            target_le = irr_data["target_le"]
            num_categories = [len(encoders[col].classes_) for col in irr_data["cat_cols"]]
            num_continuous = len(irr_data["cont_cols"])
            output_dim = len(target_le.classes_)
            
            swift_irri = SwiFTModel(
                num_continuous=num_continuous,
                num_categories=num_categories,
                embedding_dims=[4, 4],
                hidden_layers=[128, 64],
                output_dim=output_dim,
                dropout_rate=0.3
            )
            
            weights_path = os.path.join(models_dir, "swift_irrigation_model.pth")
            if os.path.exists(weights_path):
                swift_irri.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
                swift_irri.eval()
                _models["swift_irri"] = swift_irri
                print(f"[OK] SwiFT Irrigation loaded.")
            else:
                 print(f"[ERROR] SwiFT Irrigation weights not found.")
    except Exception as e:
        print(f"[ERROR] Failed to load SwiFT Irrigation: {e}")
        
    # 4. Load Legacy TabNet Models
    try:
        # Crop TabNet
        tab_path = os.path.join(models_dir, "tabnet_crop_model.zip")
        if os.path.exists(tab_path):
            tabnet = TabNetClassifier()
            tabnet.load_model(tab_path)
            _models["tabnet_crop"] = tabnet
            
            enc_path = os.path.join(models_dir, "crop_label_encoder.pkl")
            if os.path.exists(enc_path):
                with open(enc_path, "rb") as f:
                    _models["encoder_crop"] = pickle.load(f)
            print("[OK] Legacy Crop TabNet loaded.")
                
        # Fertilizer TabNet
        tab_fert_path = os.path.join(models_dir, "tabnet_fertilizer_prediction.zip")
        if os.path.exists(tab_fert_path):
            tabnet_fert = TabNetClassifier()
            tabnet_fert.load_model(tab_fert_path)
            _models["tabnet_fert"] = tabnet_fert
            print("[OK] Fertilizer TabNet loaded.")
    except Exception as e:
        print(f"[ERROR] Failed to load Legacy Models: {e}")

def get_model(name):
    return _models.get(name)

def get_model(name):
    return _models.get(name)
