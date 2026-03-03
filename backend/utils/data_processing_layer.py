import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Data Processing & Analytics Layer for AI Agriculture System.
    Handles data cleaning, feature engineering, normalization, and preparation 
    for TabNet, SwiFT, and TTL models.
    """

    # Sensor Constraints (Min, Max) to filter noise
    CONSTRAINTS = {
        'n': (0, 500), 'p': (0, 500), 'k': (0, 500),
        'temperature': (-10, 60),
        'humidity': (0, 100),
        'ph': (0, 14),
        'rainfall': (0, 500),
        'moisture': (0, 100) # Soil moisture
    }

    # Normalization Statistics (Derived from training data)
    # TODO: Load these from a file/artifact in a real production env
    STATS = {
        'mean': {
            'n': 50.0, 'p': 50.0, 'k': 50.0,
            'temperature': 25.0, 'humidity': 50.0,
            'ph': 6.5, 'rainfall': 100.0, 'moisture': 50.0,
            'nutrient_avg': 50.0, 'moisture_deficit': 20.0,
            'heat_stress': 0.0
        },
        'std': {
            'n': 20.0, 'p': 20.0, 'k': 20.0,
            'temperature': 5.0, 'humidity': 20.0,
            'ph': 1.0, 'rainfall': 50.0, 'moisture': 20.0,
            'nutrient_avg': 20.0, 'moisture_deficit': 10.0,
            'heat_stress': 1.0
        },
        'min': { # Approximated for Min-Max
             'n': 0, 'p': 0, 'k': 0, 'temperature': 0, 'humidity': 0, 'ph': 0, 'rainfall': 0, 'moisture': 0,
             'nutrient_avg': 0, 'moisture_deficit': 0, 'heat_stress': 0
        },
        'max': {
             'n': 200, 'p': 200, 'k': 200, 'temperature': 50, 'humidity': 100, 'ph': 14, 'rainfall': 300, 'moisture': 100,
             'nutrient_avg': 200, 'moisture_deficit': 100, 'heat_stress': 5
        }
    }

    def __init__(self):
        self._raw_buffer = []
        self.swift_stats = None
        self.swift_fert_stats = None
        self.load_swift_stats()
        self.load_swift_fert_stats()

    def load_swift_stats(self):
        """Loads learned statistics for SwiFT Crop standardization."""
        import pickle
        import os
        model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
        scaler_path = os.path.join(model_dir, "swift_scaler_params.pkl")
        if os.path.exists(scaler_path):
            try:
                with open(scaler_path, "rb") as f:
                    self.swift_stats = pickle.load(f)
                logger.info("Loaded SwiFT Crop scaler params.")
            except Exception as e:
                logger.error(f"Failed to load SwiFT Crop stats: {e}")
        else:
             pass # Already logged warning in previous version or can add here

    def load_swift_fert_stats(self):
        """Loads learned statistics for SwiFT Fertilizer standardization."""
        import pickle
        import os
        model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
        scaler_path = os.path.join(model_dir, "swift_fertilizer_scaler.pkl")
        if os.path.exists(scaler_path):
            try:
                with open(scaler_path, "rb") as f:
                    self.swift_fert_stats = pickle.load(f)
                logger.info("Loaded SwiFT Fertilizer scaler params.")
            except Exception as e:
                logger.error(f"Failed to load SwiFT Fertilizer stats: {e}")
        else:
             pass

    def process_pipeline(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main pipeline execution: Clean -> Engineer -> Normalize -> Format
        """
        # 1. Clean
        clean_data = self.clean_data(raw_data)
        
        # 2. Feature Engineering
        engineered_data = self.engineer_features(clean_data)
        
        # 3. Normalize & Format for Models
        
        # Base vector components in order: [N, P, K, T, H, pH, R]
        vec_std = self.normalize_standard(engineered_data)
        vec_minmax = self.normalize_minmax(engineered_data)
        
        # SwiFT Optimized Crop Vector (Standardized)
        swift_crop_features = self.get_swift_crop_features(engineered_data)
        
        # SwiFT Optimized Fertilizer Vector (Standardized)
        swift_fert_features = self.get_swift_fertilizer_features(engineered_data)
        
        processed_result = {
            "timestamp": datetime.now().isoformat(),
            "raw": raw_data,
            "engineered": engineered_data,
            "vectors": {
                "std": vec_std.tolist(),
                "minmax": vec_minmax.tolist(),
                "swift_crop": swift_crop_features,
                "swift_fertilizer": swift_fert_features
            }
        }
        
        self.log_data(processed_result)
        return processed_result

    def get_swift_crop_features(self, data: Dict[str, float]) -> Dict[str, Any]:
        """
        Prepares features specifically for SwiFT Crop Model (Optimized).
        Returns dictionary with 'continuous' (list) and 'categorical' (list).
        """
        n = data.get('n', 0)
        p = data.get('p', 0)
        k = data.get('k', 0)
        t = data.get('temperature', 0)
        h = data.get('humidity', 0)
        ph = data.get('ph', 0)
        r = data.get('rainfall', 0)
        
        # Derived
        npk_ratio = (n + p + k) / 3.0
        heat_index = t * h
        soil_health = ph + (npk_ratio / 100.0)
        
        # Season Heuristic
        # Kharif=0, Rabi=1, Zaid=2
        if r > 100: season = 0
        elif t < 25: season = 1
        else: season = 2
        
        # Continuous Vector: [N, P, K, T, H, pH, R, Ratio, HI, SH]
        cont_vector = np.array([n, p, k, t, h, ph, r, npk_ratio, heat_index, soil_health], dtype=np.float32)
        
        # Standardization
        if self.swift_stats:
             mean = self.swift_stats['mean']
             std = self.swift_stats['std']
             cont_vector = (cont_vector - mean) / (std + 1e-6)
             
        return {
            "continuous": cont_vector.tolist(),
            "categorical": [season]
        }

    def get_swift_fertilizer_features(self, data: Dict[str, float]) -> Dict[str, Any]:
        """
        Prepares features specifically for SwiFT Fertilizer Model.
        Features: N, P, K, T, H, Moisture
        """
        n = data.get('n', 0)
        p = data.get('p', 0)
        k = data.get('k', 0)
        t = data.get('temperature', 0)
        h = data.get('humidity', 0)
        m = data.get('moisture', 50) # Default to 50 if missing? Or 0?
        # Moisture range is 25-65. 50 is reasonable.
        
        # Vector: [N, P, K, T, H, M]
        vector = np.array([n, p, k, t, h, m], dtype=np.float32)
        
        # Standardization
        if self.swift_fert_stats:
             mean = self.swift_fert_stats['mean']
             std = self.swift_fert_stats['std']
             vector = (vector - mean) / (std + 1e-6)
             
        # Dummy categorical [Soil, Crop]
        # Ideally, we should receive these from the App.
        # But for now, we pass dummies. 
        # The new model expects 2 categorical inputs.
        
        return {
            "continuous": vector.tolist(),
            "categorical": [0, 0] 
        }


    def clean_data(self, data: Dict[str, float]) -> Dict[str, float]:
        """
        Clamps values to realistic ranges and defaults missing values.
        """
        cleaned = {}
        for key, limits in self.CONSTRAINTS.items():
            val = data.get(key)
            if val is None:
                # Fill missing with mean (simple imputation)
                val = self.STATS['mean'].get(key, 0.0)
            else:
                try:
                    val = float(val)
                except ValueError:
                    val = self.STATS['mean'].get(key, 0.0)
            
            # Clamp outliers
            val = max(limits[0], min(limits[1], val))
            cleaned[key] = val
            
        return cleaned

    def engineer_features(self, data: Dict[str, float]) -> Dict[str, float]:
        """
        Derives new features: Nutrient Avg, Moisture Deficit, etc.
        """
        out = data.copy()
        
        # Nutrient Average (NPK Mean)
        out['nutrient_avg'] = (out['n'] + out['p'] + out['k']) / 3.0
        
        # Moisture Deficit (Soil Capacity - Current Moisture) 
        # Assuming field capacity is ~100% for this simplified metric
        out['moisture_deficit'] = max(0.0, 100.0 - out.get('moisture', 50.0))
        
        # Rainfall Indicator (Binary/Threshold)
        out['rainfall_indicator'] = 1.0 if out.get('rainfall', 0) > 0.5 else 0.0
        
        # Heat Stress Indicator (Temp > 35C)
        out['heat_stress'] = max(0.0, out.get('temperature', 25.0) - 35.0)
        
        return out

    def normalize_minmax(self, data: Dict[str, float]) -> np.ndarray:
        """
        Min-Max Scale: (X - Min) / (Max - Min)
        Target: 0 to 1
        """
        # Vector order matching legacy training keys first: 
        # 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall'
        keys = ['n', 'p', 'k', 'temperature', 'humidity', 'ph', 'rainfall']
        vector = []
        for k in keys:
            val = data.get(k, 0.0)
            min_val = self.STATS['min'].get(k, 0.0)
            max_val = self.STATS['max'].get(k, 1.0)
            # Avoid divide by zero
            denom = (max_val - min_val) if (max_val - min_val) != 0 else 1.0
            norm_val = (val - min_val) / denom
            vector.append(norm_val)
        return np.array(vector, dtype=np.float32)

    def normalize_standard(self, data: Dict[str, float]) -> np.ndarray:
        """
        Standard Scale: (X - Mean) / Std
        Target: Mean 0, Std 1
        """
        keys = ['n', 'p', 'k', 'temperature', 'humidity', 'ph', 'rainfall']
        vector = []
        for k in keys:
            val = data.get(k, 0.0)
            mean_val = self.STATS['mean'].get(k, 0.0)
            std_val = self.STATS['std'].get(k, 1.0)
            norm_val = (val - mean_val) / (std_val + 1e-6)
            vector.append(norm_val)
        return np.array(vector, dtype=np.float32)

    def log_data(self, record: Dict):
        """
        Logs processed data for traceability to a JSONL file. 
        """
        import json
        import os
        
        LOG_DIR = "logs"
        os.makedirs(LOG_DIR, exist_ok=True)
        LOG_FILE = os.path.join(LOG_DIR, "data_trace.jsonl")
        
        try:
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Failed to log data: {e}")

# Singleton instance
data_processor = DataProcessor()
