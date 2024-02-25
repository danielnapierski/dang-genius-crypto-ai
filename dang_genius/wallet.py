import hashlib
import hmac
import json
import os
import time
from urllib.error import HTTPError
import krakenex
import sqlite3
#import numpy as np

import dang_genius.util as util

#from dang_genius.coinbaseexchange import CoinbaseExchange
from dang_genius.geminiexchange import GeminiExchange
#from dang_genius.krakenexchange import KrakenExchange

import pandas as pd
import requests
from dotenv import load_dotenv


def coinbase_connect(url_path, limit=50, cursor=''):
    load_dotenv()
    CB_API_KEY = os.environ.get('CB-API-KEY')
    CB_SECRET_KEY = os.environ.get('CB-API-SECRET')
    url_prefix = 'https://coinbase.com'
    url = url_prefix + url_path
    secret_key = CB_SECRET_KEY
    api_key = CB_API_KEY
    timestamp = str(int(time.time()))
    method = 'GET'
    body = ''
    message = timestamp + method + url_path.split('?')[0] + body
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    headers = {'accept': 'application/json', 'CB-ACCESS-SIGN': signature.hex(), 'CB-ACCESS-KEY': api_key,
               'CB-ACCESS-TIMESTAMP': timestamp}
    url = url + '?limit=' + str(limit)
    if cursor != '':
        url = url + '&cursor=' + cursor
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')


def coinbase_get_balances() -> dict:
    global tmp_df_accounts
    has_next = True
    cursor = ''
    lst_accounts = []
    while has_next:
        response = coinbase_connect(url_path='/api/v3/brokerage/accounts',
                                    limit=50,
                                    cursor=cursor)
        json_accounts = json.loads(response.text)
        has_next = json_accounts['has_next']
        cursor = json_accounts['cursor']
        tmp_df_accounts = pd.json_normalize(json_accounts, record_path=['accounts'])
        tmp_lst_accounts = tmp_df_accounts.values.tolist()
        lst_accounts.extend(tmp_lst_accounts)
    # Create dataframe from list at the end to improve performance
    df_accounts = pd.DataFrame(lst_accounts)
    # Add column names to final dataframe
    df_accounts.columns = tmp_df_accounts.columns.values.tolist()
    av_index = len(df_accounts.columns)
    df_accounts['available_balance'] = df_accounts['available_balance.value'].astype(float)
    btc_av = df_accounts.query('name == "BTC Wallet"').values[0, av_index]
    usd_av = df_accounts.query('name == "USD Wallet"').values[0, av_index]
    return {'BTC': btc_av, 'USD': usd_av}


def kraken_get_balances() -> dict:
    load_dotenv()

    KR_API_KEY = os.environ.get('KR-API-KEY')
    KR_API_SECRET = os.environ.get('KR-API-SECRET')

    k = krakenex.API(KR_API_KEY, KR_API_SECRET)
    b = k.query_private('Balance')['result']
    btc_b = float(b.get('XXBT'))
    usd_b = float(b.get('ZUSD'))
    return {'BTC': btc_b, 'USD': usd_b}


def gemini_get_balances() -> dict:
    load_dotenv()
    GE_API_KEY = os.environ.get('GE-API-KEY')
    GE_API_SECRET = os.environ.get('GE-API-SECRET')
    BTC_SWAP_AMT = float(os.environ.get('BTC-SWAP-AMT'))
    return GeminiExchange(GE_API_KEY, GE_API_SECRET, BTC_SWAP_AMT).get_balances()

def get_balances() -> dict:
    try:
        connection = sqlite3.connect(util.DB_NAME)
        cursor = connection.cursor()

        wallet_query = """SELECT id, exchange, symbol, MAX(timestamp), available FROM wallet GROUP BY exchange, symbol 
                            ORDER BY id DESC"""
        # NOTE: we should get 6 records, 3 exchanges, 2 symbols
        cursor.execute(wallet_query)
        records = cursor.fetchall()
        if len(records) != 6:
            print("UNKNOWN ERROR")

        result = {}
        for r in records:
            exchange = r[1]
            symbol = r[2]
            available = r[4]
            vallet_values = result[exchange] if exchange in result else {}
            vallet_values[symbol] = available
            result[exchange] = vallet_values
        return result
    except sqlite3.Error as error:
        print("Failed to read sqlite table", error)
        return {}
    finally:
        if connection:
            connection.close()



def wallet_summary() -> dict:
    results = get_balances()
    btc_total: float = 0.0
    usd_total: float = 0.0
    for v in results.values():
        btc_total = btc_total + float(v.get('BTC'))
        usd_total = usd_total + float(v.get('USD'))

    results['total'] = {'BTC': btc_total, 'USD': usd_total}

    return results


def check_swap_funding(exchange_a: str, symbol_a: str, amount_a: float,
                       exchange_b: str, symbol_b: str, amount_b: float) -> bool:
    balances = wallet_summary()
    return balances[exchange_a].get(symbol_a) > amount_a and balances[exchange_b].get(symbol_b) > amount_b
