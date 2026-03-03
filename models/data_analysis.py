
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create plots directory if it doesn't exist
if not os.path.exists('models/plots'):
    os.makedirs('models/plots')

# Load dataset
file_path = 'smart_soil_dataset.csv'
if not os.path.exists(file_path):
    # Try looking in parent directory
    file_path = os.path.join('..', 'smart_soil_dataset.csv')
    
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

df = pd.read_csv(file_path)

# 1. Basic Introspection
print("--- DataFrame Head ---")
print(df.head())
print("\n--- DataFrame Info ---")
print(df.info())
print("\n--- DataFrame Description ---")
print(df.describe())
print("\n--- Missing Values ---")
print(df.isnull().sum())

# 2. Correlation Analysis
# Filter numeric columns for correlation matrix
numeric_df = df.select_dtypes(include=['float64', 'int64'])
if not numeric_df.empty:
    plt.figure(figsize=(12, 10))
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    plt.savefig('models/plots/correlation_heatmap.png')
    plt.close()
    print("\nSaved correlation_heatmap.png")

# 3. Distributions (Violin/Box plots)
# Focusing on features vs Crop
features = ['moisture', 'temperature', 'humidity', 'ph', 'nitrogen', 'phosphorus', 'potassium', 'rainfall_forecast']

if 'crop' in df.columns:
    for feature in features:
        if feature in df.columns:
            plt.figure(figsize=(15, 6))
            sns.violinplot(x='crop', y=feature, data=df)
            plt.title(f'{feature} Distribution by Crop')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'models/plots/violin_{feature}.png')
            plt.close()
            print(f"Saved violin_{feature}.png")
else:
    print("Column 'crop' not found for violin plots.")

print("EDA Analysis Complete.")
