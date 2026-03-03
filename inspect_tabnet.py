
import sys
import os
import zipfile
import json
from pytorch_tabnet.tab_model import TabNetClassifier

# Add backend to sys path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def inspect_tabnet():
    models_dir = os.path.join("backend", "models")
    tab_path = os.path.join(models_dir, "tabnet_crop_model.zip")
    
    print(f"Loading TabNet from: {tab_path}")
    
    clf = TabNetClassifier()
    clf.load_model(tab_path)
    
    print("\nModel properties:")
    if hasattr(clf, 'classes_'):
        print(f"Classes_: {clf.classes_}")
    else:
        print("No classes_ attribute found")
        
    if hasattr(clf, 'output_dim'):
        print(f"Output Dim: {clf.output_dim}")
        
    if hasattr(clf, 'preds_mapper'):
        print(f"Preds Mapper: {clf.preds_mapper}")

if __name__ == "__main__":
    inspect_tabnet()
