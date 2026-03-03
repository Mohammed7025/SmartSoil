
import sys
import os
import torch
import numpy as np

# Add backend to sys path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def check_swift():
    print("Checking SwiFT Model...")
    from utils.model_loader import load_models, get_model
    from utils.preprocessing import preprocess_input
    
    # Trigger model loading
    load_models()
    
    swift_model = get_model("swift_crop")
    swift_encoder = get_model("encoder_swift_crop")
    
    if not swift_model:
        print("[FAIL] SwiFT model not loaded.")
        return
        
    if not swift_encoder:
        print("[FAIL] SwiFT encoder not loaded.")
        return
        
    print("[OK] Models loaded.")
    
    # Test Inference
    try:
        # Sample input
        input_data = {
            "n": 45, "p": 26, "k": 33,
            "temperature": 30.58, "humidity": 44,
            "ph": 6.5, "rainfall": 0.13
        }
        
        input_vector = preprocess_input(input_data, mode='minmax')
        print(f"Input Vector Shape: {input_vector.shape}")
        
        input_tensor = torch.tensor(input_vector, dtype=torch.float32)
        
        # Inference
        print("Running inference...")
        with torch.no_grad():
            output = swift_model(input_tensor) # This might be where it fails
            print(f"Raw Output: {output}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Inference failed: {e}")

if __name__ == "__main__":
    check_swift()
