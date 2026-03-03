
import pickle
import os
import sys

def check_enc():
    path = os.path.join("backend", "models", "swift_crop_label_encoder.pkl")
    print(f"Checking {path}")
    if os.path.exists(path):
        with open(path, "rb") as f:
            enc = pickle.load(f)
        print(f"Classes ({len(enc.classes_)}): {enc.classes_}")
    else:
        print("File not found")

if __name__ == "__main__":
    check_enc()
