import pickle
import os
import sys

# Add backend to sys path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def check_encoders():
    models_dir = os.path.join("backend", "models")
    
    swift_enc_path = os.path.join(models_dir, "swift_crop_label_encoder.pkl")
    tabnet_enc_path = os.path.join(models_dir, "crop_label_encoder.pkl")
    
    print(f"Checking SwiFT Encoder: {swift_enc_path}")
    if os.path.exists(swift_enc_path):
        try:
            with open(swift_enc_path, "rb") as f:
                enc = pickle.load(f)
            print(f"SwiFT Encoder Classes: {enc.classes_}")
        except Exception as e:
            print(f"Failed to load SwiFT encoder: {e}")
    else:
        print("SwiFT encoder file not found")
        
    print(f"\nChecking TabNet Encoder: {tabnet_enc_path}")
    if os.path.exists(tabnet_enc_path):
        try:
            with open(tabnet_enc_path, "rb") as f:
                enc = pickle.load(f)
            print(f"TabNet Encoder Classes: {enc.classes_}")
        except Exception as e:
            print(f"Failed to load TabNet encoder: {e}")
    else:
        print("TabNet encoder file not found")

if __name__ == "__main__":
    check_encoders()
