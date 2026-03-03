import kagglehub
import pandas as pd
import os

def inspect_dataset():
    print("Downloading 'gdabhishek/fertilizer-prediction'...")
    try:
        path = kagglehub.dataset_download("gdabhishek/fertilizer-prediction")
        print(f"Dataset downloaded to: {path}")
        
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if not files:
            print("No CSV files found.")
            return

        csv_path = os.path.join(path, files[0])
        print(f"Reading {csv_path}...")
        df = pd.read_csv(csv_path)
        
        print("\nColumns:")
        print(df.columns.tolist())
        
        print("\nFirst 5 rows:")
        print(df.head())
        
        print("\nInfo:")
        print(df.info())
        
        print("\nTarget Distribution:")
        if 'Fertilizer Name' in df.columns:
            print(df['Fertilizer Name'].value_counts())
        elif 'fertilizer' in df.columns:
             print(df['fertilizer'].value_counts())
             
        # Check for Moisture
        if 'Moisture' in df.columns:
            print("\nMoisture Stats:")
            print(df['Moisture'].describe())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_dataset()
