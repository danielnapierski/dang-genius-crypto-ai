import pandas as pd
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn
import torch

# Sample data (replace with your actual DataFrame)
data = {
    'dt': pd.to_datetime(['2024-03-06 04:17:00']),
    'value': [5217],
    'pennies': [6359467],
    'RSI': [53.853586],
    'SMA_15m': [1650.066667],
    'SMA_60m': [849.45],
    'SMA_480m': [165.047917],
    'SMA_1440m': [None],
    'SMA_2880m': [None],
    'MACD': [57.540535],
    'MACDsignal': [50.826376],
    'MACDhist': [6.71416],
    'ATR': [3108.428571],
    'Bollinger_U': [7113.499592],
    'Bollinger_L': [-4401.999592],
    'Fractal_Dimension': [0.694719]
}

df = pd.DataFrame(data)

# Preprocess data (handle missing values, normalization etc.)
# This part needs adjustment based on your data characteristics

# Fill missing values (e.g., with mean or median)
df.fillna(df.mean(), inplace=True)

# Feature scaling (e.g., using StandardScaler)
# ... (implement scaling here)

# Separate features and target
features = df.drop('value', axis=1)
target = df['value']

# Convert data to tensors
features_tensor = torch.tensor(features.values).float()
target_tensor = torch.tensor(target.values).float()

# Define the dataset
dataset = TensorDataset(features_tensor, target_tensor)

# Create a data loader (set batch size as desired)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)


# Define the model (simple MLP example)
class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Define model hyperparameters
input_dim = len(features.columns)
hidden_dim = 64
output_dim = 1  # Predicting a single value

model = MLP(input_dim, hidden_dim, output_dim)

# Define optimizer and loss function
learning_rate = 0.001
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
loss_fn = nn.MSELoss()

# Train the model (adjust epochs and other parameters as needed)
epochs = 100
for epoch in range(epochs):
    for features, targets in dataloader:
        optimizer.zero_grad()
        predictions = model(features)
        loss = loss_fn(predictions, targets)
        loss.backward()
        optimizer.step()

# Prediction function (assumes a single data point)
def predict(data):
    # Preprocess data (same preprocessing as for training)
    # ...

    # Convert data to a tensor
    data_tensor = torch.tensor(data.values).float().unsqueeze(0)

    # Make prediction
    prediction = model(data_tensor)
    return prediction.detach().item()  # Extract predicted value

# Example prediction
new_data = {'pennies': [6398741], 'RSI': [52.145231], ...}  # Replace with actual data
predicted_value = predict(new_data)
print(f"Predicted value: {predicted_value}")

import pandas as pd

# Sample DataFrame (replace with your actual data)
data = {'timestamp': pd.to_datetime(['2024-03-25 09:00:00', '2024-03-25 09:01:00', '2024-03-25 09:02:00', '2024-03-25 09:30:00', '2024-03-25 09:31:00']),
        'value': [100, 102, 98, 105, 101]}
df = pd.DataFrame(data)

# Set the window size in minutes (replace 60 with your desired window)
window_size = 60

# Resample data by minute (assuming 'timestamp' is the index)
resampled_data = df.resample('T')  # Resample to minutes

# Calculate rolling high and low within the window
rolling_high = resampled_data['value'].rolling(window=window_size).max()
rolling_low = resampled_data['value'].rolling(window=window_size).min()

# Calculate delta within the window
delta = rolling_high - rolling_low

# Calculate average delta within the window
average_delta = delta.rolling(window=window_size).mean()

# Drop NaN values introduced by rolling calculations (might occur at the beginning)
average_delta = average_delta.dropna()

print(average_delta)
