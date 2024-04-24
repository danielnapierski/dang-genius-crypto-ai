#!python3
import sqlite3
import dang_genius.util as dgu
import pandas as pd
import numpy as np
import sqlite3
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from datetime import datetime, timedelta

FEATURES = [
    "RSI",
    "SMA_15m",
    "SMA_60m",
    "SMA_480m",
    "SMA_1440m",
    "SMA_2880m",
    "MACD",
    "MACDsignal",
    "MACDhist",
    "ATR",
    "Bollinger_U",
    "Bollinger_L",
    "Fractal_Dimension",
]
TARGET = "value"


def calculate_rsi(data, period):
    """Calculates Relative Strength Index (RSI)."""
    delta = data.diff().dropna()
    up, down = delta.clip(lower=0), delta.clip(upper=0) * -1
    ema_up = up.ewm(alpha=1 / period, min_periods=period).mean()
    ema_down = down.ewm(alpha=1 / period, min_periods=period).mean().abs()
    rs = ema_up / ema_down
    rsi = 100 - 100 / (1 + rs)
    return rsi


def calculate_sma(data, window):
    """Calculates Simple Moving Average (SMA)."""
    return data.rolling(window=window).mean()


def calculate_macd(data, fast, slow, signal):
    """Calculates Moving Average Convergence Divergence (MACD)."""
    ema_fast = data.ewm(alpha=1 / (fast * 60), min_periods=fast).mean()
    ema_slow = data.ewm(alpha=1 / (slow * 60), min_periods=slow).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(alpha=1 / (signal * 60), min_periods=signal).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist


def calculate_atr(data, window):
    """Calculates Average True Range (ATR)."""
    high_low = data["value"].diff().abs()
    close_prev_diff = data["value"].diff().abs()
    true_range = pd.concat([high_low, close_prev_diff], axis=1).max(axis=1)
    atr = true_range.rolling(window=window).mean()
    return atr


def calculate_fractal_dimension(data, epsilon):
    """Estimates the fractal dimension of a time series using box-counting."""
    n_boxes = 0
    min_val, max_val = np.min(data), np.max(data)
    box_size = max_val - min_val

    # Iterate through different box sizes
    while box_size >= epsilon:
        # Iterate over boxes within the current box size
        for i in range(int((max_val - min_val) / box_size + 1)):
            n_boxes += np.sum(
                (data >= min_val + i * box_size) & (data < min_val + (i + 1) * box_size)
            )
        min_val = min_val + box_size
        box_size /= 2

    # Calculate fractal dimension estimate (replace 2 with actual embedding dimension if known)
    fractal_dim = np.log(n_boxes) / np.log(1 / epsilon) / 2
    return fractal_dim


def calculate_bollinger_bands(data, window, std):
    """Calculates Bollinger Bands (simplified)."""
    sma = data.rolling(window=window).mean()
    std_dev = data.rolling(window=window).std()
    upper_band = sma + std * std_dev
    lower_band = sma - std * std_dev
    return upper_band, lower_band


def prepare_data(data):
    """Prepares data for neural network training.

    Args:
        data: pandas.DataFrame containing the loaded data.

    Returns:
        tuple: A tuple containing training features (X_train), training targets (y_train),
               testing features (X_test), and testing targets (y_test).
    """
    # Split data into training and testing sets (adjust test size as needed)
    test_size = 0.2
    X = data[FEATURES]
    y = data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

    # Standardize features (consider normalization if needed)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, y_train, X_test, y_test


def build_model(input_shape):
    """Builds a simple neural network model.

    Args:
        input_shape: The shape of the input layer.

    Returns:
        keras.Model: The compiled neural network model.
    """
    model = Sequential()
    model.add(Dense(32, activation="relu", input_shape=input_shape))
    model.add(Dense(16, activation="relu"))
    model.add(Dense(1))

    model.compile(loss="mse", optimizer="adam")
    return model


def train_model(model, X_train, y_train, epochs=10):
    """Trains the neural network model.

    Args:
        model: The neural network model to train.
        X_train: Training features.
        y_train: Training targets.
        epochs: Number of training epochs.
    """
    model.fit(X_train, y_train, epochs=epochs, batch_size=32)


def predict_future(model, X_test):
    """Predicts future values using the trained model.

    Args:
        model: The trained neural network model.
        X_test: Testing features for prediction.

    Returns:
        pandas.DataFrame: DataFrame containing predicted values.
    """
    predictions = model.predict(X_test)
    return pd.DataFrame({"predicted_value": predictions.flatten()})


def main():
    connection = sqlite3.connect(dgu.DB_NAME)
    cursor = connection.cursor()
    limit = 600
    sql_query = f"""SELECT datetime(minute_stamp) AS dt, delta AS value, pennies FROM price_history 
            WHERE pair == 'BTC_USD' ORDER BY id LIMIT {limit}"""
    df = pd.read_sql(sql_query, connection)
    rsi = calculate_rsi(df["value"], period=14)
    df["RSI"] = rsi
    window_lengths = [15, 60, 480, 1440, 2880]  # Minutes for each window
    for window in window_lengths:
        sma = calculate_sma(df["value"], window)
        df["SMA_" + str(window) + "m"] = sma
    macd, macdsignal, macdhist = calculate_macd(df["value"], fast=12, slow=26, signal=9)
    df["MACD"] = macd
    df["MACDsignal"] = macdsignal
    df["MACDhist"] = macdhist

    # TODO: fix usage (assuming 'high', 'low', and 'close' columns exist in df):
    atr = calculate_atr(df[["value", "value", "value"]], window=14)
    df["ATR"] = atr
    upper_band, lower_band = calculate_bollinger_bands(df["value"], window=20, std=2)
    df["Bollinger_U"] = upper_band
    df["Bollinger_L"] = lower_band

    epsilon = 0.01  # Minimum box size
    fractal_dim = calculate_fractal_dimension(df["value"], epsilon)
    df["Fractal_Dimension"] = fractal_dim
    print(df.iloc[-1])
    X_train, y_train, X_test, y_test = prepare_data(df)
    input_shape = X_train.shape[1:]

    model = build_model(input_shape)
    train_model(model, X_train, y_train)

    # Predict future values (adjust logic for future timeframe)
    max_time: datetime = df["dt"].max()
    print(f"{max_time}")
    last_dt: datetime = max_time + timedelta(minutes=1)

    future_data = pd.DataFrame({"dt": [last_dt]})
    for col in FEATURES:
        future_data[col] = df[col].iloc[-1]  # Use last value for features

    # Predict using the trained model
    predicted_values = model.predict(future_data[FEATURES])

    # Combine predictions with timestamps for clarity
    future_predictions = pd.DataFrame(
        {"dt": [last_dt], "predicted_value": predicted_values.flatten()}
    )
    print(future_predictions)  # Print predicted values


if __name__ == "__main__":
    main()
