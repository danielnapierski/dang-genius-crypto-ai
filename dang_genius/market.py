import sys
from datetime import datetime
import sqlite3
import numpy as np

import dang_genius.util as util

def market_check(fee_estimate: float) -> dict:
    try:
        asks: dict = {}
        bids: dict = {}
        connection = sqlite3.connect(util.DB_NAME)
        cursor = connection.cursor()

        sqlite_select_query = """SELECT id, exchange, pair, side, MAX(timestamp), pennies FROM market GROUP BY exchange, pair, side ORDER BY id DESC LIMIT 10"""
        # NOTE: we should get 6 records, 3 exchanges, 1 pair, 2 sides (asks and bids)
# TODO: make sure the records are recent.

        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        if len(records) != 6:
            print("UNKNOWN ERROR")

        for r in records:
            exchange = r[1]
            side = r[3]
            price: float = float(int(r[5]) / 100.0)
            if util.BID_KEY == side:
                bids[price] = exchange
            if util.ASK_KEY == side:
                asks[price] = exchange

        max_bid = np.max(list(bids.keys()))
        min_ask = np.min(list(asks.keys()))
        spread = max_bid - min_ask
        fee = min_ask * fee_estimate
        sys.stdout.write(
            f'\r{datetime.now()} min_ask: {min_ask:10.2f}\tmax_bid: {max_bid:10.2f}\t'
            f'Spread: {spread:6.2f}\tFee: {fee:6.2f}\t')
        sys.stdout.flush()

        if spread > fee:
            return {util.BUY_KEY: asks[min_ask], util.SELL_KEY: bids[max_bid], util.SPREAD_KEY: spread,
                    util.MIN_ASK_KEY: min_ask, util.MAX_BID_KEY: max_bid}

        return {util.MSG_KEY: f'spread {spread:.5f} is less than fees {fee:.5f}', util.SPREAD_KEY: spread}
    except sqlite3.Error as sql_error:
        print(f'SQL error: {sql_error}')
    except TypeError as type_error:
        print(f'Type error: {type_error}')
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        if connection:
            connection.close()
