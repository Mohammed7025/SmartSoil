import pandas as pd
import sys

# Force stdout to flush
sys.stdout.reconfigure(encoding='utf-8')

try:
    df = pd.read_csv('smart_soil_dataset.csv')
    target_col = 'label' if 'label' in df.columns else 'crop'
    
    if target_col not in df.columns:
        print(f"COLUMNS: {list(df.columns)}")
    else:
        counts = df[target_col].value_counts()
        print(f"TOTAL: {len(df)}")
        print(f"CLASSES: {len(counts)}")
        print(f"MIN: {counts.min()}")
        print(f"MAX: {counts.max()}")
        print("---")
        # Print top 5 and bottom 5 to verify balance
        print(counts.head(5))
        print("...")
        print(counts.tail(5))
except Exception as e:
    print(f"ERROR: {e}")
