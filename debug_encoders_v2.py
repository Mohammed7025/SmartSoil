import pickle
import os
import sys
import numpy as np

sys.path.append(os.path.join(os.getcwd(), 'backend'))

def check_encoders():
    models_dir = os.path.join("backend", "models")
    tabnet_enc_path = os.path.join(models_dir, "crop_label_encoder.pkl")
    
    print(f"\nChecking TabNet Encoder: {tabnet_enc_path}")
    if os.path.exists(tabnet_enc_path):
        try:
            with open(tabnet_enc_path, "rb") as f:
                enc = pickle.load(f)
            
            if hasattr(enc, 'classes_'):
                print(f"TabNet Encoder Classes ({len(enc.classes_)}): {enc.classes_}")
            else:
                print("Encoder has no 'classes_' attribute.")
                print(f"Encoder type: {type(enc)}")
                print(f"Encoder dict: {enc.__dict__}")
                
        except Exception as e:
            print(f"Failed to load TabNet encoder: {e}")
    else:
        print("TabNet encoder file not found")

if __name__ == "__main__":
    check_encoders()
