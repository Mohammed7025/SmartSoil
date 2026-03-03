import pandas as pd
import numpy as np
import os
import kagglehub

def augment_data():
    print("--- Augmenting Fertilizer Data ---")
    
    # 1. Load Original Data
    try:
        path = kagglehub.dataset_download("gdabhishek/fertilizer-prediction")
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        df = pd.read_csv(os.path.join(path, files[0]))
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Clean headers
    df.columns = [c.strip() for c in df.columns]
    rename_map = {
        'Temparature': 'temperature', 'Humidity': 'humidity', 'Moisture': 'moisture',
        'Nitrogen': 'n', 'Phosphorous': 'p', 'Potassium': 'k', 
        'Fertilizer Name': 'fertilizer',
        'Soil Type': 'soil_type', 'Crop Type': 'crop_type'
    }
    df = df.rename(columns=rename_map)
    
    print(f"Original Size: {len(df)}")
    
    # 2. Augmentation Strategy
    # We will create 20 copies of each row with slight random noise
    augmented_rows = []
    
    # Numerical columns to perturb
    num_cols = ['temperature', 'humidity', 'moisture', 'n', 'p', 'k']
    
    for _ in range(20): # 20x augmentation -> ~2000 rows
        for index, row in df.iterrows():
            new_row = row.copy()
            
            # Add random noise (+/- 5%) to numerical features
            for col in num_cols:
                val = row[col]
                noise = np.random.uniform(-0.05, 0.05) * val # 5% noise
                new_val = val + noise
                
                # Clip values to realistic ranges
                if col in ['humidity', 'moisture']: new_val = np.clip(new_val, 0, 100)
                if col == 'temperature': new_val = np.clip(new_val, 0, 50) # Assuming C
                if col in ['n', 'p', 'k']: new_val = max(0, new_val)
                
                new_row[col] = round(new_val, 1) # Keep 1 decimal
            
            augmented_rows.append(new_row)
            
    # Combine original + augmented
    df_aug = pd.DataFrame(augmented_rows)
    df_final = pd.concat([df, df_aug], ignore_index=True)
    
    # Shuffle
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"New Size: {len(df_final)}")
    
    # Save to backend/data for training
    os.makedirs("backend/data", exist_ok=True)
    output_path = "backend/data/fertilizer_augmented.csv"
    df_final.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    augment_data()
