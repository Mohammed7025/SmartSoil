
import kagglehub
import os

def show_dataset_path():
    try:
        # This will return the path to the cached dataset
        path = kagglehub.dataset_download("atharvaingle/crop-recommendation-dataset")
        print(f"Dataset is stored at: {path}")
        
        # Check files in that directory
        if os.path.exists(path):
            print("\nFiles in directory:")
            for f in os.listdir(path):
                print(f" - {f}")
                
    except Exception as e:
        print(f"Error finding dataset: {e}")

if __name__ == "__main__":
    show_dataset_path()
