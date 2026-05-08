from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from utils.model_loader import get_model
from utils.preprocessing import preprocess_input
from utils.explain import generate_shap_explanation
import torch
import numpy as np

router = APIRouter()

class FertilizerInput(BaseModel):
    location: str
    month: str
    n: float
    p: float
    k: float
    ph: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    soilType: str = "Loamy"
    cropType: str = "Maize"

@router.post("/predict/fertilizer")
async def predict_fertilizer(input_data: FertilizerInput):
    from utils.weather_service import get_monthly_weather
    
    data = input_data.model_dump()
    
    if data.get('temperature') is not None and data.get('humidity') is not None and data.get('rainfall') is not None:
        weather = {
            'temperature': data['temperature'],
            'humidity': data['humidity'],
            'rainfall': data['rainfall']
        }
    else:
        weather = get_monthly_weather(data['location'], data['month'])
    
    if not weather:
        return {
            "prediction": "Error", 
            "confidence": 0.0, 
            "nutrient_data": [],
            "note": "Could not fetch weather data for the specified location and month.",
            "explain": {}
        }
        
    data['temperature'] = weather['temperature']
    data['humidity'] = weather['humidity']
    data['rainfall'] = weather['rainfall']
    
    # Load Models
    swift_model = get_model("swift_fert")
    soil_encoder = get_model("encoder_soil")
    crop_type_encoder = get_model("encoder_crop_type")
    fert_encoder = get_model("encoder_fert")
    
    # ------------------
    # STRATEGY 1: SwiFT Optimized
    # ------------------
    if all([swift_model, soil_encoder, crop_type_encoder, fert_encoder]):
        try:
            import os
            import pickle
            
            # 1. Load Scaler
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            scaler_path = os.path.join(base_path, "models", "swift_fertilizer_scaler.pkl")
            
            if os.path.exists(scaler_path):
                with open(scaler_path, "rb") as f:
                    params = pickle.load(f)
                    means = params['mean']
                    stds = params['std']
            else:
                means = np.array([50, 50, 50, 30, 60, 50])
                stds = np.array([20, 20, 20, 5, 10, 20])

            # 2. Preprocessing & Heuristics
            moisture = min(100, max(0, (data['humidity'] * 0.6) + (data['rainfall'] / 5)))
            
            target_crop = data['cropType'] if data['cropType'] in crop_type_encoder.classes_ else 'Maize'
            target_soil = data['soilType'] if data['soilType'] in soil_encoder.classes_ else 'Loamy'
            
            # Encode Categoricals
            soil_idx = soil_encoder.transform([target_soil])[0]
            crop_idx = crop_type_encoder.transform([target_crop])[0]
            
            # 3. Prepare Inputs
            raw_cont = np.array([data['n'], data['p'], data['k'], data['temperature'], data['humidity'], moisture])
            norm_cont = (raw_cont - means) / (stds + 1e-6)
            
            x_cont = torch.tensor(norm_cont, dtype=torch.float32).unsqueeze(0)
            x_cat = torch.tensor([[soil_idx, crop_idx]], dtype=torch.long)
            
            # 4. Inference
            with torch.no_grad():
                logits = swift_model(x_cont, x_cat)
                probs = torch.softmax(logits, dim=1)
                top_idx = torch.argmax(probs).item()
                confidence = probs[0, top_idx].item()
                predicted_fertilizer = fert_encoder.inverse_transform([top_idx])[0]

            stage_context = "Best for general growth."
            if "Urea" in predicted_fertilizer: stage_context = "Best for Vegetative Growth stage."
            elif "DAP" in predicted_fertilizer: stage_context = "Best for Basal application (Root development)."

            # 5. Nutrient Deficiency Data (Current vs Ideal)
            ideals = {"N": 150, "P": 60, "K": 60} 
            nutrient_gap = [
                {"name": "Nitrogen", "current": data['n'], "ideal": ideals["N"], "status": "Low" if data['n'] < ideals["N"]*0.7 else "Moderate" if data['n'] < ideals["N"]*0.9 else "Sufficient"},
                {"name": "Phosphorus", "current": data['p'], "ideal": ideals["P"], "status": "Low" if data['p'] < ideals["P"]*0.7 else "Moderate" if data['p'] < ideals["P"]*0.9 else "Sufficient"},
                {"name": "Potassium", "current": data['k'], "ideal": ideals["K"], "status": "Low" if data['k'] < ideals["K"]*0.7 else "Moderate" if data['k'] < ideals["K"]*0.9 else "Sufficient"}
            ]

            return {
                "prediction": predicted_fertilizer,
                "confidence": round(confidence, 4),
                "model_used": "SwiFT (Transformer)",
                "note": f"{stage_context} (Soil: {target_soil}, Target: {target_crop})",
                "nutrient_data": nutrient_gap,
                "explain": {
                    "chart_data": [], 
                    "factors": {"Soil Moisture": f"{round(moisture, 1)}% (Estimated)"}
                }
            }
        except Exception as e:
            print(f"SwiFT Fertilizer Error: {e}")
            pass

    # ------------------
    # STRATEGY 2: TabNet (Legacy/Fallback)
    # ------------------
    model = get_model("tabnet_fert")
    encoder = get_model("encoder_fert")
    if not model or not encoder:
        return {"recommendation": "Loading...", "confidence": 0.0, "explain": {}}

    try:
        full_vector = preprocess_input(data, mode='minmax')
        input_vector = full_vector[:, :5]
        probs = model.predict_proba(input_vector)[0]
        top_class_idx = np.argmax(probs)
        confidence = float(probs[top_class_idx])
        predicted_fertilizer = encoder.inverse_transform([top_class_idx])[0]
            
        return {
            "prediction": predicted_fertilizer, 
            "confidence": round(confidence, 4),
            "model_used": "TabNet (Legacy)",
            "explain": {}
        }
    except Exception as e:
        print(f"Legacy Fertilizer Error: {e}")
        return {"prediction": "Error", "confidence": 0.0, "explain": {}}

