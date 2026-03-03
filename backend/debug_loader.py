import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import load_models, get_model

try:
    load_models()
    
    ttl = get_model("ttl_irri")
    if ttl:
        print("SUCCESS: TTL Model is loaded.")
        print(ttl)
    else:
        print("FAILURE: TTL Model is None.")
        
    enc = get_model("encoder_ttl")
    if enc:
        print("SUCCESS: TTL Encoder is loaded.")
        print(enc.classes_)
    else:
        print("FAILURE: TTL Encoder is None.")
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
