import joblib
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    encoder_path = os.path.join('backend', 'models', 'fertilizer_label_encoder.pkl')
    if os.path.exists(encoder_path):
        encoder = joblib.load(encoder_path)
        print("Fertilizer Classes:", encoder.classes_)
    else:
        print(f"Encoder not found at {encoder_path}")
except Exception as e:
    print(f"Error loading encoder: {e}")
