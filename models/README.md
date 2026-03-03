# Crop Recommendation Model (TabNet)

This directory contains scripts to analyze the dataset, preprocess it, and train a TabNet model for crop recommendation.

## Prerequisites

Install the required Python packages:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn pytorch-tabnet torch joblib
```

## Dataset

Ensure `smart_soil_dataset.csv` is located in the root folder (one level up from this directory).

## How to Run

### 1. Exploratory Data Analysis (EDA)
Generates correlation heatmaps and violin plots to understand the data.
**Output**: Plots saved to `models/plots/`.

```bash
python models/data_analysis.py
```

### 2. Preprocessing
Splits the data into training, validation, and test sets, scales the features, and encodes the target labels.
**Output**: Processed `.npy` and `.pkl` files saved to `models/data/`.

```bash
python models/preprocessing.py
```

### 3. Model Training
Trains the TabNet classifier using the processed data.
**Output**: Trained model saved as `models/data/tabnet_model.zip`.

```bash
python models/train_tabnet.py
```
