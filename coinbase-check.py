# Adapted from https://github.com/ni79ls/coinbase-api-auth-playground/blob/main/README.md
import pandas as pd
import json
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
import time
import numpy as np
from urllib.error import HTTPError
from dotenv import load_dotenv
import os
load_dotenv()

CB_API_KEY = os.environ.get('CB-API-KEY')
CB_SECRET_KEY = os.environ.get('CB-API-SECRET')

def cb_connect(url_path, limit=50, cursor=''):
    url_prefix = 'https://coinbase.com'
    url = url_prefix + url_path
    secret_key = CB_SECRET_KEY
    api_key = CB_API_KEY
    timestamp = str(int(time.time()))
    method = 'GET'
    body = ''
    message = timestamp + method + url_path.split('?')[0] + body 
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    headers = {'accept': 'application/json','CB-ACCESS-SIGN':signature.hex(), 'CB-ACCESS-KEY':api_key, 'CB-ACCESS-TIMESTAMP': timestamp}
    url=url+'?limit='+str(limit)
    if cursor!='':
        url=url+'&cursor='+cursor
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f'HTTP connection {url} successful!')
        return response
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def cb_get_all_accounts():
    has_next = True
    cursor = ''
    lst_accounts = []
    while has_next:
        response = cb_connect(url_path='/api/v3/brokerage/accounts',
            limit=50,
            cursor=cursor)
        json_accounts = json.loads(response.text)
        has_next = json_accounts['has_next']
        cursor = json_accounts['cursor']
        tmp_df_accounts = pd.json_normalize(json_accounts, record_path =['accounts'])
        tmp_lst_accounts = tmp_df_accounts.values.tolist() 
        lst_accounts.extend(tmp_lst_accounts)
# Create dataframe from list at the end to improve performance
    df_accounts = pd.DataFrame(lst_accounts)
# Add column names to final dataframe
    df_accounts.columns = tmp_df_accounts.columns.values.tolist()
    return df_accounts

def cb_get_all_orders():
    has_next = True
    cursor = ''
    lst_orders = []
    while has_next:
        response = cb_connect(url_path='/api/v3/brokerage/orders/historical/batch',
            limit=100,
            cursor=cursor)
        json_orders = json.loads(response.text)
        has_next = json_orders['has_next']
        cursor = json_orders['cursor']
        tmp_df_orders = pd.json_normalize(json_orders, record_path =['orders'])
        tmp_lst_orders = tmp_df_orders.values.tolist() 
        lst_orders.extend(tmp_lst_orders)
# Create dataframe from list at the end to improve performance
    df_orders = pd.DataFrame(lst_orders)
# Add column names to final dataframe
    df_orders.columns = tmp_df_orders.columns.values.tolist()
    return df_orders

pd.options.display.float_format = '{:,.2f}'.format

df_accounts = cb_get_all_accounts()
df_accounts.rename(columns={'available_balance.value': 'available_balance','hold.value': 'hold'}, inplace=True)
df_accounts['available_balance'] = df_accounts['available_balance'].astype(float)
df_accounts['hold'] = df_accounts['hold'].astype(float)
df_accounts = df_accounts.query('available_balance > 0 or hold > 0')
df_accounts.drop(['available_balance.currency','hold.currency','default','created_at','updated_at','deleted_at','ready'], axis=1, inplace=True)
print(f"{df_accounts[['currency','available_balance','hold']]}")
