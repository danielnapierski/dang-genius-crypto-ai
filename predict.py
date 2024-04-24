#!python3
import sqlite3
import warnings
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

import dang_genius.util as dgu

connection = sqlite3.connect(dgu.DB_NAME)

for limit in range(6000, 8000, 1):
    sql_query = f"""SELECT datetime(minute_stamp) AS timestamp, delta AS value, pennies FROM price_history 
                WHERE pair == 'BTC_USD' ORDER BY id LIMIT {limit}"""

    df = pd.read_sql(sql_query, connection)

    current = df["pennies"].iloc[-6] / 100.0
    target = df["pennies"].iloc[-1] / 100.0
    print(f"CURRENT: {current:.2f} \tTARGET: {target:.2f}")

    next_five = df.iloc[-5:]["value"].sum() / 100.0
    print(f"Next five sum: \t\t\t{next_five:+.2f}")
    df = df.iloc[:-5]  # Select all rows except the last five
    y = df["value"]
    p = 0
    d = 0
    q = 0
    model = ARIMA(y, order=(p, d, q))
    model_fit = model.fit()
    forecast_steps = 5
    forecast = model_fit.forecast(steps=forecast_steps)
    deltas = []
    for i in forecast:
        deltas.append(i)

    tally = sum(deltas) / 100.0
    #    print(f'PREDICTION: {limit:8d}\t{tally:+.2f}')

    warnings.filterwarnings("ignore")

    model = ExponentialSmoothing(
        df["value"], trend="add", seasonal=None
    )  # No seasonality assumed here
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=forecast_steps)
    print(f"EXPO: \t\t\t\t{sum(forecast) / 100.0:+.2f}")
    print()
