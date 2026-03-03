
import numpy as np
import torch
import joblib
import os
from pytorch_tabnet.tab_model import TabNetClassifier
from train_swift import SwiFTModel
from train_ttl import TTLModel

print("--- Verifying Models ---")

# 1. Crop Model (TabNet)
try:
    print("Loading Crop Model (TabNet)...")
    crop_clf = TabNetClassifier()
    # Path assuming execution from root
    crop_clf.load_model('models/data/tabnet_model.zip')
    # Dummy input (8 features)
    dummy_input_crop = np.random.rand(1, 8)
    crop_pred = crop_clf.predict(dummy_input_crop)
    print(f"Crop Prediction: {crop_pred}")
    print("Crop Model Loaded Successfully.")
except Exception as e:
    print(f"FAILED to load Crop Model: {e}")

# 2. Fertilizer Model (SwiFT)
try:
    print("\nLoading Fertilizer Model (SwiFT)...")
    # Determine input dim from data or encoded pkl
    scaler_X = joblib.load('models/data/swift/scaler_X.pkl')
    input_dim = scaler_X.n_features_in_
    # Output dim is 2 (N, P)
    swift_model = SwiFTModel(input_dim, 2)
    swift_model.load_state_dict(torch.load('models/data/swift/swift_model.pth'))
    swift_model.eval()
    
    dummy_input_swift = torch.rand(1, input_dim)
    swift_pred = swift_model(dummy_input_swift)
    print(f"Fertilizer Prediction (Scaled): {swift_pred.detach().numpy()}")
    print("Fertilizer Model Loaded Successfully.")
except Exception as e:
    print(f"FAILED to load Fertilizer Model: {e}")

# 3. Irrigation Model (TTL)
try:
    print("\nLoading Irrigation Model (TTL)...")
    scaler_X_ttl = joblib.load('models/data/ttl/scaler_X.pkl')
    input_dim_ttl = scaler_X_ttl.n_features_in_
    ttl_model = TTLModel(input_dim_ttl)
    ttl_model.load_state_dict(torch.load('models/data/ttl/ttl_model.pth'))
    ttl_model.eval()
    
    dummy_input_ttl = torch.rand(1, input_dim_ttl)
    ttl_pred = ttl_model(dummy_input_ttl)
    print(f"Irrigation Prediction (Scaled): {ttl_pred.detach().numpy()}")
    print("Irrigation Model Loaded Successfully.")
except Exception as e:
    print(f"FAILED to load Irrigation Model: {e}")

print("\n--- Verification Complete ---")
