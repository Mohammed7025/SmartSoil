from fastapi import APIRouter
from pydantic import BaseModel
from utils.model_loader import get_model
from utils.preprocessing import preprocess_input
from utils.explain import generate_shap_explanation
import torch
import numpy as np

router = APIRouter()

class IrrigationInput(BaseModel):
    n: float
    p: float
    k: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    soil_moisture: float = 50.0 # Default if not provided
    pressure: float = 1013.0    # Default atm pressure

@router.post("/predict/irrigation")
async def predict_irrigation(data: IrrigationInput):
    model = get_model("ttl_irri")
    encoder = get_model("encoder_ttl")
    
    # Preprocess
    # Trained on: temperature, pressure, moisture
    # Range Assumptions (from dataset): T(0-50), P(900-1100), M(0-100) or similar
    # We apply loose MinMax to keep values in reasonable range for NN
    # T: 0-50, P: 900-1100, M: 0-100
    
    t_norm = (data.temperature - 0) / (50 - 0)
    p_norm = (data.pressure - 900) / (1100 - 900)
    m_norm = (data.soil_moisture - 0) / (100 - 0)
    
    input_vector = np.array([[t_norm, p_norm, m_norm]])
    
    if not model:
        return {"irrigation_hours": 0.0, "status": "Model not loaded", "confidence": 0.0, "explain": {}}

    # Predict
    try:
        model.eval()
        with torch.no_grad():
            input_tensor = torch.tensor(input_vector).float()
            output = model(input_tensor) # Logits
            probs = torch.softmax(output, dim=1)
            
        conf, pred_idx = torch.max(probs, dim=1)
        confidence = float(conf.numpy()[0])
        idx = int(pred_idx.numpy()[0])
        
        status = "Unknown"
        if encoder:
            status = encoder.inverse_transform([idx])[0]
        else:
            status = f"Class {idx}"
            
        status = str(status) # Ensure string for mapping keys
            
        # Map Status to Legacy "Hours" for dashboard compatibility
        # Classes found: [0, 1]. 
        # Logic: 1 (Index 1) for Moist=10 (Dry) -> 1=Dry (Pump On). 
        # 0 -> Wet (Pump Off).
        hours_map = {
            "Very Dry": 4.0,
            "Dry": 2.0,
            "Wet": 0.0,
            "1": 2.0, # Dry/Pump On
            "0": 0.0  # Wet/Pump Off
        }
        
        hours = 0.0
        # Check exact string match (e.g. "1") or partial if text
        if status in hours_map:
            hours = hours_map[status]
        else:
            # Fallback partial match
            for k, v in hours_map.items():
                if k.lower() in status.lower():
                    hours = v
                    break
        
        # Nicer Text status
        if status == "1":
            status = "Irrigation Needed (Dry)"
        elif status == "0":
            status = "Sufficient Moisture (Wet)"
                
    except Exception as e:
        print(f"TTL Prediction error: {e}")
        return {"irrigation_hours": 0.0, "status": "Error", "confidence": 0.0, "explain": {}}

    # Explain
    # We pass the input vector (1, 3) to the explanation (PyTorch gradient logic)
    explanation = generate_shap_explanation(model, input_vector) if model else {} 

    return {
        "irrigation_hours": round(hours, 2),
        "status": status,
        "confidence": round(confidence, 4),
        "model_used": "TTL (Time-series Classification)",
        "explain": explanation
    }
