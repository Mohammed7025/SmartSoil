from fastapi import APIRouter
from pydantic import BaseModel
from utils.model_loader import get_model
from utils.preprocessing import preprocess_input
from utils.explain import generate_shap_explanation
import torch
import numpy as np

router = APIRouter()

class FertilizerInput(BaseModel):
    n: float
    p: float
    k: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

@router.post("/predict/fertilizer")
async def predict_fertilizer(data: FertilizerInput):
    model = get_model("tabnet_fert")
    encoder = get_model("encoder_fert")
    
    # Preprocess
    # Train stats: N(0-200), P(0-200), K(0-200), T(0-50), H(0-100)
    # API has 7 features, but training used only first 5: n, p, k, temperature, humidity
    full_vector = preprocess_input(data.model_dump(), mode='minmax')
    
    # Slice to first 5 features
    input_vector = full_vector[:, :5]
    
    if not model:
        return {
            "recommendation": "Model not loaded",
            "confidence": 0.0,
            "explain": {}
        }

    # Predict
    try:
        # TabNet predict_proba
        probs = model.predict_proba(input_vector)[0]
        top_class_idx = np.argmax(probs)
        confidence = float(probs[top_class_idx])
        
        if encoder:
            predicted_fertilizer = encoder.inverse_transform([top_class_idx])[0]
        else:
            predicted_fertilizer = f"Class {top_class_idx}"
            
        # --- Logic Fix 2: Rainfall Context ---
        rainfall_warning = ""
        if data.rainfall < 10:
            rainfall_warning = " Note: Requires irrigation for effective uptake due to low rainfall."
        
        # --- Logic Fix 3: Crop Stage Context ---
        # Map common formulas to stages
        stage_context = ""
        fert_name = str(predicted_fertilizer).strip()
        
        if "10-26-26" in fert_name:
            stage_context = "Best for Flowering & Pod Formation stages."
        elif "Urea" in fert_name or "46-0-0" in fert_name:
            stage_context = "Best for Vegetative Growth stage."
        elif "DAP" in fert_name or "18-46-0" in fert_name:
            stage_context = "Best for Basal application (Root development)."
        elif "MOP" in fert_name or "0-0-60" in fert_name:
            stage_context = "Best for Fruit Quality & Disease Resistance."
        elif "19-19-19" in fert_name:
            stage_context = "General purpose for early growth."

        final_recommendation = f"{predicted_fertilizer}. {stage_context}{rainfall_warning}"
        
        # --- Logic Fix 1: Rule-Based Impact Factors (Replacing 0% SHAP) ---
        impact_factors = {}
        
        # Nitrogen Rules
        if data.n < 50:
            impact_factors["Nitrogen"] = "Low (Use N-rich fertilizer)"
        elif data.n > 150:
            impact_factors["Nitrogen"] = "High (Limit N application)"
            
        # Phosphorus Rules
        if data.p < 20:
             impact_factors["Phosphorus"] = "Low (Root support needed)"
             
        # Potassium Rules
        if data.k < 30:
            impact_factors["Potassium"] = "Low (Strengthen immunity)"
            
        # Soil pH
        if data.ph < 5.5:
             impact_factors["pH"] = "Acidic (Add Lime)"
        elif data.ph > 7.5:
             impact_factors["pH"] = "Alkaline (Add Gypsum)"
             
    except Exception as e:
        print(f"TabNet Prediction error: {e}")
        return {"recommendation": "Error", "confidence": 0.0, "explain": {}}

    return {
        "recommendation": predicted_fertilizer, 
        "confidence": round(confidence, 4),
        "model_used": "TabNet (Context-Aware)",
        "note": f"{stage_context}{rainfall_warning}",
        "explain": {
            "factors": impact_factors
        }
    }
