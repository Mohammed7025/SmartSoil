import pandas as pd

try:
    df = pd.read_csv('smart_soil_dataset.csv')
    # Check for 'label' or 'crop' column
    target_col = 'label' if 'label' in df.columns else 'crop'
    
    if target_col not in df.columns:
        print(f"Error: Could not find target column. Columns: {df.columns}")
    else:
        counts = df[target_col].value_counts()
        print(f"Total Samples: {len(df)}")
        print(f"Unique Crops: {len(counts)}")
        print(f"Min Samples per Crop: {counts.min()}")
        print(f"Max Samples per Crop: {counts.max()}")
        print("\nDistribution:")
        print(counts)
except Exception as e:
    print(f"Error: {e}")
