from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from utils.model_loader import get_model
from utils.preprocessing import preprocess_input
from utils.explain import generate_shap_explanation
import numpy as np

router = APIRouter()

class CropInput(BaseModel):
    location: str
    month: str
    n: float
    p: float
    k: float
    ph: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None

@router.post("/predict/crop")
async def predict_crop(input_data: CropInput):
    from utils.weather_service import get_monthly_weather
    swift_model = get_model("swift_crop")
    swift_encoder = get_model("encoder_swift_crop")
    
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
            "note": "Could not fetch weather data for the specified location and month.",
            "explain": {}
        }
        
    data['temperature'] = weather['temperature']
    data['humidity'] = weather['humidity']
    data['rainfall'] = weather['rainfall']
    
    # ------------------
    # STRATEGY 1: SwiFT Optimized
    # ------------------
    if swift_model and swift_encoder:
        try:
            import torch
            import torch.nn.functional as F
            import pickle
            import os
            
            # 1. Load Scaler Params
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            scaler_path = os.path.join(base_path, "models", "swift_scaler_params.pkl")
            
            if not os.path.exists(scaler_path):
                print("Scaler params not found, using default normalization (0-1 approx)")
                means = np.array([50.0, 50.0, 50.0, 25.0, 50.0, 6.5, 100.0, 50.0, 1500.0, 7.0])
                stds = np.array([20.0, 20.0, 20.0, 5.0, 20.0, 1.0, 50.0, 20.0, 500.0, 2.0])
            else:
                with open(scaler_path, "rb") as f:
                    params = pickle.load(f)
                    means = params['mean']
                    stds = params['std']

            # 2. Feature Engineering & Sanity Check
            # data has already been populated with temperature, humidity, rainfall
            
            # Fix 1: Rainfall Sanity Check (Seasonal Minimum)
            if data['rainfall'] < 5:
                print("Sanity Check: Rainfall adjusted from", data['rainfall'], "to 60 (Seasonal Min)")
                data['rainfall'] = 60.0
            
            # Derived
            npk_ratio = (data['n'] + data['p'] + data['k']) / 3.0
            heat_index = data['temperature'] * data['humidity']
            soil_health = data['ph'] + (npk_ratio / 100.0)
            
            # Season Heuristic (Confirmed identical to training)
            if data['rainfall'] > 100:
                season = 0
            elif data['temperature'] < 25:
                season = 1
            else:
                season = 2
                
            # 3. Prepare Inputs
            raw_cont = np.array([
                data['n'], data['p'], data['k'], 
                data['temperature'], data['humidity'], data['ph'], data['rainfall'],
                npk_ratio, heat_index, soil_health
            ])
            
            # Normalize (Standardization: X - mean / std)
            norm_cont = (raw_cont - means) / (stds + 1e-6)
            
            # Tensors
            x_cont = torch.tensor(norm_cont, dtype=torch.float32).unsqueeze(0) # (1, 10)
            x_cat = torch.tensor([season], dtype=torch.long).unsqueeze(0)      # (1, 1)
            
            # 4. Inference with Pre-filtering (Masking)
            with torch.no_grad():
                logits = swift_model(x_cont, x_cat) # (1, num_classes)
                
                # --- Pre-filtering Rules ---
                blocked_crops = []
                
                # Rule 1: High Temp (>35) -> No Wheat, Barley
                if data['temperature'] > 35:
                    blocked_crops.extend(['wheat', 'barley'])
                    
                # Rule 2: Low Rainfall (<100) -> No Rice
                if data['rainfall'] < 100:
                    blocked_crops.append('rice')
                    
                # Rule 3: Low Humidity (<30) -> No Banana, Mango
                if data['humidity'] < 30:
                    blocked_crops.extend(['banana', 'mango'])
                
                # Apply Mask
                if blocked_crops:
                    print(f"Blocking crops: {blocked_crops}")
                    for crop in blocked_crops:
                        if crop in swift_encoder.classes_:
                            idx = np.where(swift_encoder.classes_ == crop)[0][0]
                            logits[0, idx] = -float('inf')

                # Softmax & Top-K
                probs = F.softmax(logits, dim=1)
                
                # Get Top 3
                top3_probs, top3_indices = torch.topk(probs, 3)
                
                top_class_idx = top3_indices[0][0].item()
                confidence = top3_probs[0][0].item()
                
                predicted_crop = swift_encoder.inverse_transform([top_class_idx])[0]
                
                # Get all top 3 names
                top3_names = swift_encoder.inverse_transform(top3_indices[0].numpy())
                print(f"Top 3 Predictions: {list(zip(top3_names, top3_probs[0].numpy()))}")

            # Fix 2: Confidence Interpretation
            note = ""
            if confidence < 0.5:
                note = "Moderate suitability – irrigation required"
                
            # --- Modern SHAP Explanation ---
            # input_vector for SwiFT is a tuple of (cont, cat)
            explanation = generate_shap_explanation(swift_model, (x_cont.numpy(), x_cat.numpy()))

            return {
                "prediction": predicted_crop,
                "confidence": round(confidence, 4),
                "model_used": "SwiFT (XAI Enabled)",
                "note": note,
                "explain": {
                    "top_3": [
                        {"crop": name, "prob": round(float(prob), 4)} 
                        for name, prob in zip(top3_names, top3_probs[0].numpy())
                    ],
                    **explanation
                }
            }
        except Exception as e:
            import traceback
            print(f"SwiFT Prediction Error: {e}")
            traceback.print_exc()
            # Fallthrough to TabNet (Legacy)
            pass

    # ------------------
    # STRATEGY 2: TabNet (Legacy/Fallback)
    # ------------------
    model = get_model("tabnet_crop")
    encoder = get_model("encoder_crop")
    
    if not model:
        return {
           "prediction": "Model loading...",
           "confidence": 0.0,
           "explain": {}
        }
        
    try:
        input_vector = preprocess_input(data, mode='minmax')
        probs = model.predict_proba(input_vector)[0]
        top_class_idx = np.argmax(probs)
        confidence = float(probs[top_class_idx])
        
        predicted_crop = encoder.inverse_transform([top_class_idx])[0] if encoder else f"Class {top_class_idx}"
            
        explanation = generate_shap_explanation(model, input_vector)

        return {
            "prediction": predicted_crop,
            "confidence": round(confidence, 4),
            "model_used": "TabNet (Fallback XAI)",
            "explain": explanation
        }
    except Exception as e:
        print(f"Legacy Prediction Error: {e}")
        return {"prediction": "Error", "confidence": 0.0, "explain": {}}

