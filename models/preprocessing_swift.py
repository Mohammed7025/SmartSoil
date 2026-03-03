
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# Create processed data directory
swift_data_dir = 'models/data/swift'
if not os.path.exists(swift_data_dir):
    os.makedirs(swift_data_dir)

# Load data (Robust check)
file_path = 'smart_soil_dataset.csv'
if not os.path.exists(file_path):
    file_path = os.path.join('..', 'smart_soil_dataset.csv')
    
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

df = pd.read_csv(file_path)

# --- Define Features and Targets ---
# Inputs: N, P, K, pH, Moisture, Rainfall, Crop (Target input for context)
# We want to predict: How much ADDED N and P is needed? (fertilizer_n, fertilizer_p)
X = df[['nitrogen', 'phosphorus', 'potassium', 'ph', 'moisture', 'rainfall_forecast', 'crop']]
y = df[['fertilizer_n', 'fertilizer_p']]

print(f"Features: {X.columns.tolist()}")
print(f"Targets: {y.columns.tolist()}")

# --- Feature Encoding ---
# We need to encode 'crop' because it's categorical input
le_crop = LabelEncoder()
X['crop_encoded'] = le_crop.fit_transform(X['crop'])
# Save encoder to reuse for inference
joblib.dump(le_crop, os.path.join(swift_data_dir, 'label_encoder_crop.pkl'))

# Drop original crop column
X = X.drop('crop', axis=1)

# --- Split Data ---
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

print(f"Train shapes: X={X_train.shape}, y={y_train.shape}")

# --- Scaling ---
# Scale Input Features
scaler_X = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_val_scaled = scaler_X.transform(X_val)
X_test_scaled = scaler_X.transform(X_test)
joblib.dump(scaler_X, os.path.join(swift_data_dir, 'scaler_X.pkl'))

# Scale Targets (Regression targets) - Optional but good for NN convergence
scaler_y = StandardScaler()
y_train_scaled = scaler_y.fit_transform(y_train)
y_val_scaled = scaler_y.transform(y_val)
y_test_scaled = scaler_y.transform(y_test)
joblib.dump(scaler_y, os.path.join(swift_data_dir, 'scaler_y.pkl'))

# --- Save Data ---
np.save(os.path.join(swift_data_dir, 'X_train.npy'), X_train_scaled)
np.save(os.path.join(swift_data_dir, 'y_train.npy'), y_train_scaled)
np.save(os.path.join(swift_data_dir, 'X_val.npy'), X_val_scaled)
np.save(os.path.join(swift_data_dir, 'y_val.npy'), y_val_scaled)
np.save(os.path.join(swift_data_dir, 'X_test.npy'), X_test_scaled)
np.save(os.path.join(swift_data_dir, 'y_test.npy'), y_test_scaled)

print(f"SwiFT Preprocessing Complete. Data saved to {swift_data_dir}")
