
import numpy as np
import torch
from pytorch_tabnet.tab_model import TabNetClassifier
import os
import joblib

# Load Data
data_dir = 'models/data'
if not os.path.exists(data_dir):
    print(f"Error: {data_dir} not found. Run preprocessing first.")
    exit(1)

X_train = np.load(os.path.join(data_dir, 'X_train.npy'))
y_train = np.load(os.path.join(data_dir, 'y_train.npy'))
X_val = np.load(os.path.join(data_dir, 'X_val.npy'))
y_val = np.load(os.path.join(data_dir, 'y_val.npy'))
X_test = np.load(os.path.join(data_dir, 'X_test.npy'))
y_test = np.load(os.path.join(data_dir, 'y_test.npy'))

print(f"Loaded training data: {X_train.shape}")

# Define TabNet Model
# Using default parameters for initial train, can be tuned later
clf = TabNetClassifier(
    optimizer_fn=torch.optim.Adam,
    optimizer_params=dict(lr=2e-2),
    scheduler_params={"step_size":10, "gamma":0.9},
    scheduler_fn=torch.optim.lr_scheduler.StepLR,
    mask_type='entmax' # "sparsemax"
)

# Train
max_epochs = 100 if torch.cuda.is_available() else 50 # Reduce epochs for CPU to be faster for demo
print(f"Starting training for {max_epochs} epochs...")

clf.fit(
    X_train=X_train, y_train=y_train,
    eval_set=[(X_train, y_train), (X_val, y_val)],
    eval_name=['train', 'valid'],
    eval_metric=['accuracy', 'logloss'],
    max_epochs=max_epochs,
    patience=20,
    batch_size=256,
    virtual_batch_size=128,
    num_workers=0,
    drop_last=False
)

# Evaluate
preds = clf.predict(X_test)
test_acc = np.mean(preds == y_test)
print(f"FINAL TEST ACCURACY: {test_acc}")

# Save Model
model_path = os.path.join(data_dir, 'tabnet_model')
saved_filepath = clf.save_model(model_path)
print(f"Model saved to {saved_filepath}")
