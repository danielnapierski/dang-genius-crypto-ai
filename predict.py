# Import libraries
import dang_genius.util as dgu

import pandas as pd
import sqlite3
from statsmodels.tsa.arima.model import ARIMA

# Define database filepath (replace 'your_database.db' with your actual file path)

# Connect to the database
connection = sqlite3.connect(dgu.DB_NAME)

# Define SQL query to retrieve data
sql_query = "SELECT minute_stamp as timestamp, delta FROM price_history WHERE pair == 'ETH_USD' ORDER BY id ASC"  # Replace with your specific query

# Read data from the database using SQL query
data = pd.read_sql(sql_query, connection)

# Convert timestamp column to datetime format (assuming timestamp is indexed by date)
data.index = pd.to_datetime(data['timestamp'])

# Drop rows with missing timestamps (assuming you've already done this)
data.dropna(inplace=True)

# Set frequency information (assuming data is in minutes)
data.index = data.index.to_period('Min')  # Sets frequency to minutely periods

# Drop the timestamp column (optional, if it's the index)
data.drop('timestamp', axis=1, inplace=True)

# Define ARIMA model parameters (replace with values based on data analysis)
p, d, q = 1, 0, 1

# Create ARIMA model
model = ARIMA(data, order=(p, d, q))

# Fit the model on training data
model_fit = model.fit()
future_minutes = 2
forecast = model_fit.forecast(steps=future_minutes)

print("Predicted values:")
print(forecast)
connection.close()
