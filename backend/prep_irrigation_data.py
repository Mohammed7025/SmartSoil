import pandas as pd
import numpy as np
import kagglehub
import os

# Download and load the latest version
path = kagglehub.dataset_download("miadul/irrigation-water-requirement-prediction-dataset")
csv_path = None
for file in os.listdir(path):
    if file.endswith('.csv'):
        csv_path = os.path.join(path, file)
        break

if not csv_path:
    raise Exception("No CSV file found in dataset directory!")

# Read the full dataset
df = pd.read_csv(csv_path)

# Clean column names (strip whitespace)
df.columns = df.columns.str.strip()

# 1. Filter the requested columns plus the target
requested_cols = [
    'Soil_Type', 
    'Crop_Type', 
    'Temperature_C', 
    'Humidity', 
    'Rainfall_mm', 
    'Soil_Moisture',
    'Irrigation_Need' # This is our target
]

df_filtered = df[requested_cols].copy()

# 2. Rename columns to be more standard/code-friendly
df_filtered.rename(columns={
    'Soil_Type': 'soil_type',
    'Crop_Type': 'crop',
    'Temperature_C': 'temperature',
    'Humidity': 'humidity',
    'Rainfall_mm': 'rainfall',
    'Soil_Moisture': 'soil_moisture',
    'Irrigation_Need': 'irrigation_needed'
}, inplace=True)

# 3. Handle 'Medium' by mapping to Low or High based on your request: "predict irrigation needed into low or ,medium and high irrigation needed"
# Actually the dataset has 'Low', 'Medium', 'High' already.
print("Target classes found:", df_filtered['irrigation_needed'].unique())
print("\nFirst 5 rows:\n", df_filtered.head())
print("\nDataset info:")
df_filtered.info()

# Save the filtered dataset for training our new model
output_path = "dataset_irri_new.csv"
df_filtered.to_csv(output_path, index=False)
print(f"\nSaved filtered dataset to {output_path}")
