import pandas as pd
import numpy as np
import random

# Configuration
NUM_SAMPLES = 2000
CROPS = ["Rice", "Wheat", "Cotton", "Maize", "Sugarcane"]

def generate_entry():
    crop = random.choice(CROPS)
    
    # Base conditions per crop to make data realistic
    if crop == "Rice":
        temp = random.uniform(25, 35)
        humid = random.uniform(70, 90)
        moisture = random.uniform(40, 80) # Rice needs water
        rainfall = random.uniform(20, 50)
    elif crop == "Wheat":
        temp = random.uniform(20, 30)
        humid = random.uniform(40, 60)
        moisture = random.uniform(20, 50)
        rainfall = random.uniform(5, 20)
    elif crop == "Cotton":
        temp = random.uniform(25, 40)
        humid = random.uniform(30, 50)
        moisture = random.uniform(20, 40)
        rainfall = random.uniform(5, 15)
    elif crop == "Maize":
        temp = random.uniform(22, 32)
        humid = random.uniform(50, 70)
        moisture = random.uniform(30, 60)
        rainfall = random.uniform(10, 30)
    else: # Sugarcane
        temp = random.uniform(25, 35)
        humid = random.uniform(60, 85)
        moisture = random.uniform(50, 80)
        rainfall = random.uniform(15, 35)

    ph = random.uniform(4.5, 8.0)
    
    # NPK levels (Randomized within realistic bounds)
    n = random.randint(10, 80)
    p = random.randint(5, 40)
    k = random.randint(10, 80)

    # Derived outputs:
    
    # 1. Irrigation Hours (Simple logic: Lower moisture + High Temp = More water)
    # Target moisture is ~80 for high water crops, ~50 for others.
    moisture_deficit = max(0, 80 - moisture) if crop in ["Rice", "Sugarcane"] else max(0, 50 - moisture)
    irrigation_hours = (moisture_deficit * 0.5) + (temp * 0.2) - (rainfall * 0.1)
    irrigation_hours = max(4, min(72, irrigation_hours)) # Clamp between 4 and 72

    # 2. Fertilizer Need (Target NPK - Current NPK)
    # Simple targets
    target_n = 100 if crop in ["Rice", "Maize"] else 80
    target_p = 50 
    target_k = 50
    
    fert_n = max(0, target_n - n)
    fert_p = max(0, target_p - p)

    return {
        "moisture": round(moisture, 1),
        "temperature": round(temp, 1),
        "humidity": round(humid, 1),
        "ph": round(ph, 1),
        "nitrogen": n,
        "phosphorus": p,
        "potassium": k,
        "rainfall_forecast": round(rainfall, 1),
        "crop": crop,
        "fertilizer_n": round(fert_n, 1),
        "fertilizer_p": round(fert_p, 1),
        "irrigation_hours": round(irrigation_hours, 1)
    }

# Generate Data
data = [generate_entry() for _ in range(NUM_SAMPLES)]
df = pd.DataFrame(data)

# Save to CSV
output_path = "smart_soil_dataset.csv"
df.to_csv(output_path, index=False)
print(f"Dataset generated with {NUM_SAMPLES} rows at {output_path}")
