
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import joblib

# --- SwiFT Model Architecture (Feed-Forward) ---
class SwiFTModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(SwiFTModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(64, 32)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(32, output_dim) # Output: Fertilizer N, Fertilizer P

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

# --- Training Script ---
def train_swift():
    swift_data_dir = 'models/data/swift'
    if not os.path.exists(swift_data_dir):
        print("Data directory not found. Run preprocessing_swift.py first.")
        return

    # Load Data
    X_train = np.load(os.path.join(swift_data_dir, 'X_train.npy'))
    y_train = np.load(os.path.join(swift_data_dir, 'y_train.npy'))
    
    X_val = np.load(os.path.join(swift_data_dir, 'X_val.npy'))
    y_val = np.load(os.path.join(swift_data_dir, 'y_val.npy'))
    
    X_test = np.load(os.path.join(swift_data_dir, 'X_test.npy'))
    y_test = np.load(os.path.join(swift_data_dir, 'y_test.npy'))

    # Convert to Tensors
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32)
    X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
    y_val_tensor = torch.tensor(y_val, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)

    # Initialize Model
    input_dim = X_train.shape[1]
    output_dim = y_train.shape[1]
    
    model = SwiFTModel(input_dim, output_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    print("Starting SwiFT Model Training...")

    epochs = 100
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 10 == 0:
            model.eval()
            with torch.no_grad():
                val_outputs = model(X_val_tensor)
                val_loss = criterion(val_outputs, y_val_tensor)
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}')

    # Save Model
    torch.save(model.state_dict(), os.path.join(swift_data_dir, 'swift_model.pth'))
    print(f"SwiFT Model saved to {os.path.join(swift_data_dir, 'swift_model.pth')}")

    # Evaluate on Test Set
    model.eval()
    with torch.no_grad():
        test_predictions = model(X_test_tensor)
        # Inverse transform to get actual nutrient values
        scaler_y = joblib.load(os.path.join(swift_data_dir, 'scaler_y.pkl'))
        actual_preds = scaler_y.inverse_transform(test_predictions.numpy())
        actual_targets = scaler_y.inverse_transform(y_test)
        
        # Calculate MAE
        mae = np.mean(np.abs(actual_preds - actual_targets))
        print(f"Final Test MAE (Mean Absolute Error): {mae:.2f}")

if __name__ == "__main__":
    train_swift()

