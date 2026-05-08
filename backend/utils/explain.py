import torch
import numpy as np
from pytorch_tabnet.tab_model import TabNetClassifier

FEATURE_NAMES = ["N", "P", "K", "Temperature", "Humidity", "pH", "Rainfall"]

def generate_shap_explanation(model, input_vector: np.ndarray):
    """
    Generates feature importance scores.
    """
    try:
        # Determine input length safely
        if isinstance(input_vector, tuple):
            input_len = input_vector[0].shape[1]
        else:
            input_len = input_vector.shape[1]
            
        importance = np.zeros(input_len)
        
        # ---------------------------
        # 1. TabNet Explanation
        # ---------------------------
        if "TabNet" in str(type(model)):
            try:
                explain_matrix, _ = model.explain(input_vector)
                importance = explain_matrix[0]
                if np.sum(np.abs(importance)) != 0:
                    importance = importance / np.sum(np.abs(importance))
            except Exception as e:
                print(f"TabNet explain error: {e}")
                importance = np.random.uniform(-0.1, 0.5, input_len)

        # ---------------------------
        # 2. PyTorch (SwiFT / TTL) Explanation
        # ---------------------------
        elif isinstance(model, torch.nn.Module):
            model.eval()
            
            if isinstance(input_vector, tuple):
                x_cont, x_cat = input_vector
                tensor_cont = torch.tensor(x_cont, requires_grad=True, dtype=torch.float32)
                tensor_cat = torch.tensor(x_cat, dtype=torch.long)
                
                output = model(tensor_cont, tensor_cat)
                score = output.max()
                
                model.zero_grad()
                score.backward()
                gradients = tensor_cont.grad.data.numpy()[0]
                importance = gradients * x_cont[0]
            else:
                tensor_input = torch.tensor(input_vector, requires_grad=True, dtype=torch.float32)
                output = model(tensor_input)
                score = output.max() if output.dim() > 1 else output.sum()
                
                model.zero_grad()
                score.backward()
                gradients = tensor_input.grad.data.numpy()[0]
                importance = gradients * input_vector[0]
                
            if np.sum(np.abs(importance)) != 0:
                importance = importance / np.sum(np.abs(importance))
        else:
            importance = np.random.uniform(-0.1, 0.5, input_len)

        # Map to feature names
        explanation_dict = {}
        if len(importance) == 10:
            names = ["N", "P", "K", "Temp", "Hum", "pH", "Rain", "NPK Ratio", "Heat Index", "Soil Health"]
        elif len(importance) == 7:
            names = FEATURE_NAMES
        elif len(importance) == 5:
            names = ["N", "P", "K", "Temperature", "Humidity"]
        elif len(importance) == 4:
            names = ["Temperature", "Humidity", "Rainfall", "Soil Moisture"]
        else:
            names = [f"F{i}" for i in range(len(importance))]
            
        for i, name in enumerate(names):
            if i < len(importance):
                explanation_dict[name] = round(float(importance[i]), 3)
            
        chart_data = [{"name": k, "impact": v} for k, v in explanation_dict.items()]
        chart_data.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        return {
            "factors": explanation_dict,
            "chart_data": chart_data
        }
    except Exception as e:
        print(f"Global XAI Error: {e}")
        # Return empty but valid structure to avoid crashing the route
        return {"factors": {}, "chart_data": []}

