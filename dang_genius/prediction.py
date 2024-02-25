import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime


def arima():
    # Sample data with precise timestamps and float values
    data = [
        (datetime(2023, 1, 1, 12, 30, 0), 10.5),
        (datetime(2023, 1, 1, 12, 30, 15), 11.2),
        (datetime(2023, 1, 1, 12, 30, 30), 9.8),
        # ... more data with precise timestamps and float values
    ]

    # Create pandas DataFrame with timestamps as index and values as column
    df = pd.DataFrame(data, columns=["timestamp", "value"])
    df.set_index("timestamp", inplace=True)

    # Extract time series data
    series = df["value"]

    # Define ARIMA parameters (adjust based on your data analysis)
    p = 1  # Autoregressive order
    d = 0  # Differencing order (since data is stationary)
    q = 1  # Moving average order

    # Create and fit ARIMA model
    model = ARIMA(series, order=(p, d, q))
    model_fit = model.fit()

    # Forecast future values for a few seconds (adjust forecast_length as needed)
    forecast_length = 5  # Forecast for 5 seconds into the future
    forecast = model_fit.forecast(steps=forecast_length)

    # Print the forecasted values
    print("Forecasted values:")
    for i in range(forecast_length):
        print(f"{forecast[i]}")


def exponential_smoothing(timestamps, values, future_time, alpha):
    """
  Performs exponential smoothing on a time series and predicts future value.

  Args:
      timestamps: List of timestamps as datetime objects.
      values: List of corresponding values at each timestamp.
      future_time: Future timestamp as a datetime object.
      alpha: Smoothing parameter (0 < alpha < 1).

  Returns:
      Predicted value at the future time.
  """

    smoothed_values = [values[0]]  # Initialize with the first value

    for i in range(1, len(timestamps)):
        v_i = values[i]
        s_t_i = alpha * v_i + (1 - alpha) * smoothed_values[-1]
        smoothed_values.append(s_t_i)

    delta_t = (future_time - timestamps[-1]).total_seconds()  # Convert to seconds
    prediction = smoothed_values[-1] * (1 - alpha) ** delta_t  # Use the last smoothed value

    return prediction
