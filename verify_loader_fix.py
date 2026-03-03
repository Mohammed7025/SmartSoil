
import sys
import os
import pickle

# Add backend to sys path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def verify_fix():
    print("Verifying Model Loader Fix...")
    from utils.model_loader import load_models, get_model
    
    # Trigger model loading
    load_models()
    
    encoder = get_model("encoder_crop")
    
    if encoder:
        print("\n[SUCCESS] Encoder loaded successfully.")
        if hasattr(encoder, 'classes_'):
             print(f"Classes found: {encoder.classes_}")
             
        # Test a transform
        try:
             # Just checking if we can inverse
             label = encoder.inverse_transform([0])[0]
             print(f"Test decode class 0: {label}")
        except Exception as e:
            print(f"[ERROR] Decoder failed inverse_transform: {e}")
    else:
        print("\n[FAIL] Encoder is still None.")

if __name__ == "__main__":
    verify_fix()
