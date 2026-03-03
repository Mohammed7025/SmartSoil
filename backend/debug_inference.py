import sys
import os
import torch
import numpy as np

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import load_models, get_model

try:
    load_models()
    
    model = get_model("ttl_irri")
    encoder = get_model("encoder_ttl")
    
    if not model:
        print("Model failed to load.")
        exit()

    print(f"Model: {model}")
    print(f"Encoder Classes: {encoder.classes_ if encoder else 'None'}")
    
    # Simulate Route Logic
    # T=30, P=1010, M=10
    t_norm = (30 - 0) / (50 - 0)
    p_norm = (1010 - 900) / (1100 - 900)
    m_norm = (10.0 - 0) / (100 - 0)
    
    input_vector = np.array([[t_norm, p_norm, m_norm]])
    print(f"Input Vector: {input_vector}")
    print(f"Input Shape: {input_vector.shape}")
    
    model.eval()
    with torch.no_grad():
        input_tensor = torch.tensor(input_vector).float()
        print(f"Tensor Shape: {input_tensor.shape}")
        
        output = model(input_tensor) # Logits
        print(f"Raw Output: {output}")
        
        probs = torch.softmax(output, dim=1)
        print(f"Probs: {probs}")
        
        conf, pred_idx = torch.max(probs, dim=1)
        idx = int(pred_idx.numpy()[0])
        print(f"Predicted Index: {idx}")
        
        if encoder:
            status = encoder.inverse_transform([idx])[0]
            print(f"Status: {status}")
            
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
