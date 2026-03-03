
try:
    import kagglehub
    from kagglehub import KaggleDatasetAdapter
    import pandas as pd

    print("Attempting to load dataset...")
    # Download raw files
    path = kagglehub.dataset_download("chineduchukwuemeka/smart-irrigation-data-derive-dataset")
    print(f"Dataset downloaded to: {path}")
    
    import os
    print("Files in dataset:")
    files = os.listdir(path)
    for f in files:
        print(f" - {f}")
        
    # Attempt to load CSV if one exists
    csv_files = [f for f in files if f.endswith('.csv')]
    if csv_files:
        print(f"Loading {csv_files[0]}...")
        df = pd.read_csv(os.path.join(path, csv_files[0]))
        print("COLUMNS_START")
        for c in df.columns:
            print(c)
        print("Unique Status:", df['status'].unique())
        print("Unique Class:", df['class'].unique())
        print("Shape:", df.shape)
    else:
        print("No CSV file found.")
        exit()

except ImportError as e:
    print(f"Error: {e}. Please install requirements.")
except Exception as e:
    print(f"Error accessing dataset: {e}")
