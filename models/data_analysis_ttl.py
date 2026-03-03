
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

if not os.path.exists('models/plots'):
    os.makedirs('models/plots')

file_path = 'smart_soil_dataset.csv'
if not os.path.exists(file_path):
    file_path = os.path.join('..', 'smart_soil_dataset.csv')
    
if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

df = pd.read_csv(file_path)

print("--- Irrigation Target Analysis ---")
print(df['irrigation_hours'].describe())

# 1. Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df['irrigation_hours'], kde=True, color='blue')
plt.title('Distribution of Irrigation Hours Needed')
plt.xlabel('Hours')
plt.savefig('models/plots/irrigation_dist.png')
print("Saved irrigation_dist.png")

# 2. Moisture vs Irrigation (Expect negative correlation)
plt.figure(figsize=(8, 6))
sns.scatterplot(x='moisture', y='irrigation_hours', hue='crop', data=df, alpha=0.6)
plt.title('Soil Moisture vs Irrigation Hours')
plt.savefig('models/plots/moisture_vs_irrigation.png')
print("Saved moisture_vs_irrigation.png")

# 3. Crop vs Irrigation
plt.figure(figsize=(12, 6))
sns.boxplot(x='crop', y='irrigation_hours', data=df)
plt.xticks(rotation=45)
plt.title('Irrigation Requirements by Crop')
plt.tight_layout()
plt.savefig('models/plots/irrigation_by_crop.png')
print("Saved irrigation_by_crop.png")

print("Irrigation Data Analysis Complete.")
