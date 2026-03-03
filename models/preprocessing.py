
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# Create processed data directory
if not os.path.exists('models/data'):
    os.makedirs('models/data')

# Load data
file_path = 'smart_soil_dataset.csv'
if not os.path.exists(file_path):
    # Try looking in parent directory
    file_path = os.path.join('..', 'smart_soil_dataset.csv')

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

df = pd.read_csv(file_path)

# Define Features and Target
# Based on inspection: moisture, temperature, humidity, ph, nitrogen, phosphorus, potassium, rainfall_forecast
# Target: crop
X = df[['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall_forecast', 'moisture']]
y = df['crop']

print(f"Features: {X.columns.tolist()}")
print(f"Target: crop")

# Encode Target
le = LabelEncoder()
y_encoded = le.fit_transform(y)
joblib.dump(le, 'models/data/label_encoder.pkl')
print("LabelEncoder saved.")

# Split Data (Train: 70%, Val: 15%, Test: 15%)
X_train, X_temp, y_train, y_temp = train_test_split(X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

print(f"Train shapes: X={X_train.shape}, y={y_train.shape}")
print(f"Val shapes:   X={X_val.shape}, y={y_val.shape}")
print(f"Test shapes:  X={X_test.shape}, y={y_test.shape}")

# Normalize Features (StandardScaler)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, 'models/data/scaler.pkl')
print("StandardScaler saved.")

# Save Processed Data
np.save('models/data/X_train.npy', X_train_scaled)
np.save('models/data/y_train.npy', y_train)
np.save('models/data/X_val.npy', X_val_scaled)
np.save('models/data/y_val.npy', y_val)
np.save('models/data/X_test.npy', X_test_scaled)
np.save('models/data/y_test.npy', y_test)

print("Preprocessing Complete. Data saved to models/data/")
