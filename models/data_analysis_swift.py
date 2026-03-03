
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create plots directory if it doesn't exist
if not os.path.exists('models/plots'):
    os.makedirs('models/plots')

# Load dataset (Robust path check)
file_path = 'smart_soil_dataset.csv'
if not os.path.exists(file_path):
    file_path = os.path.join('..', 'smart_soil_dataset.csv')
    
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

df = pd.read_csv(file_path)

print("--- Fertilizer Target Analysis ---")
print(df[['fertilizer_n', 'fertilizer_p']].describe())

# 1. Distributions of Targets
plt.figure(figsize=(10, 5))
sns.histplot(df['fertilizer_n'], kde=True, color='green', label='Fertilizer N')
sns.histplot(df['fertilizer_p'], kde=True, color='orange', label='Fertilizer P')
plt.title('Distribution of Fertilizer Requirements')
plt.legend()
plt.savefig('models/plots/fertilizer_dist.png')
print("Saved fertilizer_dist.png")

# 2. Correlation with Soil Nutrients
# Does low soil Nitrogen imply high Fertilizer N?
soil_vs_fert = df[['nitrogen', 'phosphorus', 'potassium', 'fertilizer_n', 'fertilizer_p']]
plt.figure(figsize=(8, 6))
sns.heatmap(soil_vs_fert.corr(), annot=True, cmap='RdYlGn')
plt.title('Correlation: Soil vs Fertilizer')
plt.savefig('models/plots/fertilizer_soil_corr.png')
print("Saved fertilizer_soil_corr.png")

# 3. Fertilizer Needs by Crop (Boxplot)
plt.figure(figsize=(15, 6))
sns.boxplot(x='crop', y='fertilizer_n', data=df)
plt.xticks(rotation=45)
plt.title('Fertilizer N Requirement by Crop')
plt.tight_layout()
plt.savefig('models/plots/fertilizer_n_by_crop.png')
print("Saved fertilizer_n_by_crop.png")

print("Fertilizer Data Analysis Complete.")
