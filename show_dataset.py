
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd

def show_data():
    print("Loading crop recommendation dataset from Kaggle...")
    try:
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "atharvaingle/crop-recommendation-dataset",
            "Crop_recommendation.csv",
        )
        print("\n--- Dataset Info ---")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        print("\n--- First 5 Rows ---")
        print(df.head().to_string())
        
        print("\n--- Unique Crops (Labels) ---")
        crops = df['label'].unique()
        print(f"Total Unique Crops: {len(crops)}")
        print(crops)
        
    except Exception as e:
        print(f"Error loading dataset: {e}")

if __name__ == "__main__":
    show_data()
