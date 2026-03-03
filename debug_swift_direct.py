
import sys
import os
import torch
import numpy as np

# Add backend to sys path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def check_swift_direct():
    print("Checking SwiFT Model DIRECT LOAD...")
    from models.architectures import SwiFTModel
    import pickle
    
    models_dir = os.path.join("backend", "models")
    weights_path = os.path.join(models_dir, "swift_crop_model.pth")
    encoder_path = os.path.join(models_dir, "swift_crop_label_encoder.pkl")
    
    try:
        # Load Encoder
        print(f"Loading encoder from {encoder_path}")
        with open(encoder_path, "rb") as f:
            encoder = pickle.load(f)
        print(f"Encoder classes: {encoder.classes_}")
        
        # Load Model
        num_classes = len(encoder.classes_)
        print(f"Initializing SwiFTModel with output_dim={num_classes}")
        model = SwiFTModel(input_dim=7, hidden_dim=128, output_dim=num_classes)
        
        print(f"Loading weights from {weights_path}")
        state_dict = torch.load(weights_path, map_location=torch.device('cpu'))
        model.load_state_dict(state_dict)
        model.eval()
        print("[SUCCESS] SwiFT Model loaded manually.")
        
        if num_classes == 22:
             print("[SUCCESS] Correctly detected 22 classes.")
        else:
             print(f"[WARNING] Expected 22 classes, found {num_classes}.")
        
    except Exception as e:
        print("\n[ERROR] Direct loading failed:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_swift_direct()
