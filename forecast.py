#!python3
import sqlite3
from datetime import timedelta
from prophet import Prophet
import pandas as pd
import dang_genius.util as dgu

from datetime import datetime
import matplotlib.pyplot as plt

# Sample data (replace with your actual financial data)
sample_data = [
    ("2023-01-01T00:00:00Z", 10.5),
    ("2023-01-15T00:00:00Z", 12.1),
    ("2023-02-01T00:00:00Z", 11.8),
    ("2023-02-15T00:00:00Z", 13.2),
    ("2023-03-01T00:00:00Z", 14.0),
]

x = """       datetime(minute_stamp) AS parsed_datetime,
       delta AS value FROM price_history
       WHERE pair == 'BTC_USD'
       ORDER BY id LIMIT 10
"""
# sql_query = ("""SELECT minute_stamp AS ds, delta AS y FROM price_history
#                WHERE pair == 'BTC_USD' ORDER BY id""")


connection_path = dgu.DB_NAME

# Define SQL query to fetch data
sql = """
SELECT minute_stamp as datetime, delta as value
FROM price_history
WHERE pair == 'BTC_USD' ORDER BY id ASC;
"""

# Read data into a pandas DataFrame
connection = sqlite3.connect(connection_path)
data_df = pd.read_sql_query(sql, connection)

# Ensure datetime is a datetime object (assuming it's stored as a string)
data_df["datetime"] = pd.to_datetime(data_df["datetime"])

# **Check for missing values (optional):**
# You might want to check for missing values in 'datetime' or 'value' columns
# and handle them appropriately (e.g., impute or remove rows).
# For example:
# print(data_df.isnull().sum())  # Check for missing values

# Copy the DataFrame to avoid modifying the original
data_df_prophet = data_df.copy()

# Rename columns as Prophet expects (without setting index yet)
data_df_prophet.columns = ["ds", "y"]

# **Print DataFrame structure (optional):**
# You can print the DataFrame structure to visually confirm the column names
# and data types. For example:
# print(data_df_prophet.info())

# Set datetime (now 'ds') as the index
data_df_prophet.set_index("ds", inplace=True)

# Create a Prophet model
model = Prophet()

# **Check DataFrame contents before fitting (optional):**
# You can print a few rows of the DataFrame to ensure it has the expected
# structure for Prophet. For example:
# print(data_df_prophet.head())  # Print the first few rows

# Train the model on your historical data (using the modified DataFrame)
model.fit(data_df_prophet)

# Define the future date for prediction (replace with your desired date)
future_date = data_df_prophet.index[-1] + timedelta(days=30)  # 30 days in the future

# Create a dataframe specifying the future date for prediction
future_data = model.make_future_dataframe(periods=30, freq="D", include_history=False)

# Generate predictions for the future dates
forecast = model.predict(future_data)

# Extract the predicted value for the future date
predicted_value = forecast[forecast.index == future_date]["yhat"].iloc[0]

# Print the predicted value
print(f"Predicted value for {future_date}: {predicted_value:.2f}")

# Close the connection (optional, recommended practice)
connection.close()
