import numpy as np

# Statistics for normalization (Mean and Std Dev from training data)
# You should replace these with actual values saved during training (e.g. using a scalar.json)
MEAN = np.array([50.0, 50.0, 50.0, 25.0, 50.0, 6.5, 100.0])
STD = np.array([20.0, 20.0, 20.0, 5.0, 20.0, 1.0, 50.0])

def preprocess_input(data: dict, mode: str = 'standard') -> np.ndarray:
    """
    Converts input dictionary to a normalized numpy array.
    Order: [N, P, K, temperature, humidity, ph, rainfall]
    
    Args:
        data: Input dictionary
        mode: 'standard' (Z-score) for SwiFT, 'minmax' (0-1) for TabNet/TTL
    """
    features = np.array([
        data.get("n", 0),
        data.get("p", 0),
        data.get("k", 0),
        data.get("temperature", 0),
        data.get("humidity", 0),
        data.get("ph", 0),
        data.get("rainfall", 0)
    ], dtype=np.float32)

    if mode == 'standard':
        # SwiFT: (X - Mean) / Std
        normalized_features = (features - MEAN) / (STD + 1e-6)
    elif mode == 'minmax':
        # TabNet & TTL: (X - Min) / (Max - Min)
        # Hardcoded boundaries from training scripts
        MINS = np.array([0, 0, 0, 0, 0, 0, 0])
        MAXS = np.array([200, 200, 200, 50, 100, 14, 300])
        normalized_features = (features - MINS) / (MAXS - MINS + 1e-6)
    else:
        # Default fallback (Standard)
        normalized_features = (features - MEAN) / (STD + 1e-6)
    
    # Return as batch of size 1: (1, 7)
    return np.expand_dims(normalized_features, axis=0)

def inverse_transform_output(output):
    # If needed for regression outputs
    return output
