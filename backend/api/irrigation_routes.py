from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from utils.model_loader import get_model
from utils.preprocessing import preprocess_input
from utils.explain import generate_shap_explanation
import torch
import numpy as np

router = APIRouter()

class IrrigationInput(BaseModel):
    location: str
    month: str
    n: float = 0.0
    p: float = 0.0
    k: float = 0.0
    ph: float = 7.0
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    rainfall: Optional[float] = None
    soil_moisture: float = 50.0 # Default if not provided
    pressure: float = 1013.0    # Default atm pressure
    soilType: str = "Loamy"
    cropType: str = "Maize"

@router.post("/predict/irrigation")
async def predict_irrigation(input_data: IrrigationInput):
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
            "status": "Error",
            "irrigation_hours": 0.0,
            "note": "Could not fetch weather data for the specified location and month.",
            "explain": {}
        }
        
    data['temperature'] = weather['temperature']
    data['humidity'] = weather['humidity']
    data['rainfall'] = weather['rainfall']
    
    with open("debug_payload.txt", "w") as f:
        f.write(str(data))
    print(f"DEBUG INCOMING DATA: {data}")
    model = get_model("swift_irri")
    irr_data = get_model("encoder_irrigation")
    
    if not model or not irr_data:
        return {"irrigation_hours": 0.0, "status": "Model not loaded", "confidence": 0.0, "explain": {}}

    try:
        encoders = irr_data["encoders"]
        target_le = irr_data["target_le"]
        scaler = irr_data["scaler"]
        cat_cols = irr_data["cat_cols"] # ['soil_type', 'crop']
        cont_cols = irr_data["cont_cols"] # ['temperature', 'humidity', 'rainfall', 'soil_moisture']
        
        # 1. Process Categorical Inputs
        # Fallback to 0 if the input class was not seen during training
        cat_values = []
        # Soil
        try:
            cat_values.append(encoders['soil_type'].transform([data['soilType']])[0])
        except ValueError:
            cat_values.append(0) 
            
        # Crop
        try:
            cat_values.append(encoders['crop'].transform([data['cropType']])[0])
        except ValueError:
            cat_values.append(0)
            
        # 2. Process Continuous Inputs
        cont_values = [[
            data['temperature'],
            data['humidity'],
            data['rainfall'],
            data['soil_moisture']
        ]]
        
        cont_scaled = scaler.transform(cont_values)
        
        # 3. Create Tensors
        input_cat = torch.tensor([cat_values], dtype=torch.long)
        input_cont = torch.tensor(cont_scaled, dtype=torch.float32)
        
        # 4. Predict
        model.eval()
        with torch.no_grad():
            output = model(input_cont, input_cat) # Logits
            probs = torch.softmax(output, dim=1)
            
        conf, pred_idx = torch.max(probs, dim=1)
        confidence = float(conf.numpy()[0])
        idx = int(pred_idx.numpy()[0])
        
        # Get actual string status
        status_raw = target_le.inverse_transform([idx])[0]
        status = str(status_raw).title() # E.g., 'Low', 'Medium', 'High'
        
        # Map Status to Legacy "Hours" for dashboard compatibility
        hours_map = {
            "High": 4.0,
            "Medium": 2.0,
            "Low": 0.0,
            # Fallbacks just in case
            "Dry": 2.0,
            "Wet": 0.0,
        }
        
        hours = hours_map.get(status, 0.0)
        
        # Nicer Text status for UI
        ui_status = f"{status} Irrigation Needed"
        if status == "Low":
            ui_status = "Sufficient Moisture (Low Need)"
        
        # ---------------------------------------------------------
        # GUARDRAILS / MANUAL OVERRIDES
        # Neural Networks can act unpredictably on edge cases (e.g., 0%)
        # if the dataset didn't contain values that low.
        # Force strict limits to match farmer expectations.
        # ---------------------------------------------------------
        if data['soil_moisture'] <= 15.0:
            status = "High"
            hours = 4.0
            ui_status = "Critical Moisture (High Need)"
        elif data['soil_moisture'] > 15.0 and data['soil_moisture'] <= 45.0:
            status = "Medium"
            hours = 2.0
            ui_status = "Medium Irrigation Needed"
        elif data['soil_moisture'] > 45.0:
            status = "Low"
            hours = 0.0
            ui_status = "Sufficient Moisture (Low Need)"
                
    except Exception as e:
        print(f"SwiFT Irrigation Prediction error: {e}")
        return {"irrigation_hours": 0.0, "status": "Error", "confidence": 0.0}

    # Generative AI rule-based advice
    advice = "Soil moisture is sufficient. Irrigation not required."
    if hours > 0:
        advice = f"Based on the {data['soilType']} soil and your {data['cropType']} crop, we recommend {hours} hours of irrigation to meet the {status.lower()} water requirement."
        if data['temperature'] > 30:
            advice += " Due to high temperatures, water in the early morning or evening to reduce evaporation."
        if data.get('rainfall', 0) > 10:
            advice += f" Note: Recent rainfall of {data['rainfall']}mm may reduce the total water volume needed."
            
    # Include XAI Data
    explanation = generate_shap_explanation(model, (input_cont.numpy(), input_cat.numpy()))

    return {
        "irrigation_hours": round(hours, 2),
        "status": ui_status,
        "confidence": round(confidence, 4),
        "model_used": "SwiFT (Deep Learning)",
        "ai_advice": advice,
        "explain": explanation
    }
