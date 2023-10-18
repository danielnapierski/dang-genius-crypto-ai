import hashlib
import hmac
import json
import os
import time
from pprint import pprint
from urllib.error import HTTPError
import krakenex
from gemini_api.authentication import Authentication
from gemini_api.authentication import Authentication as GeAuth
from gemini_api.endpoints.fund_management import FundManagement
from gemini_api.endpoints.fund_management import FundManagement as GeFM

# TODO: currently not using import coinbasepro as cbp may need pro api key?

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
    # TODO: kraken USD?
    usd_b = float(-1.0)
    return {'BTC': btc_b, 'USD': usd_b}


def gemini_get_BTC_balance() -> float:
    load_dotenv()
    GE_API_KEY = os.environ.get('GE-API-KEY')
    GE_API_SECRET = os.environ.get('GE-API-SECRET')
    auth = Authentication(public_key=GE_API_KEY, private_key=GE_API_SECRET)
    x = FundManagement.get_notional_balances(auth=auth, currency='USD')
    btc = x[0]
    return float(getattr(btc, 'amount'))


def gemini_get_USD_balance() -> float:
    load_dotenv()
    GE_API_KEY = os.environ.get('GE-API-KEY')
    GE_API_SECRET = os.environ.get('GE-API-SECRET')

    auth = GeAuth(public_key=GE_API_KEY, private_key=GE_API_SECRET)
    ab = GeFM.get_available_balances(auth=auth)
    usd = ab[0]
    return float(getattr(usd, 'amount'))


def wallet_summary(verbose: bool = None) -> dict:
    cb_balances = coinbase_get_balances()
    kr_balances = kraken_get_balances()
    gemini_btc = gemini_get_BTC_balance()
    time.sleep(1)
    gemini_usd = gemini_get_USD_balance()

    if verbose:
        print('Coinbase:')
        pprint(cb_balances)
        print('Kraken:')
        pprint(kr_balances)
        print('Gemini:')
        pprint({'BTC': gemini_btc, 'USD': gemini_usd})

    btc_total = cb_balances.get('BTC') + kr_balances.get('BTC') + gemini_btc
    usd_total = cb_balances.get('USD') + kr_balances.get('USD') + gemini_usd
    result = {'BTC': btc_total, 'USD': usd_total}
    if verbose:
        print('Coinbase:')
        pprint(cb_balances)
        print('Kraken:')
        pprint(kr_balances)
        print('Gemini:')
        pprint({'BTC': gemini_btc, 'USD': gemini_usd})
        print('TOTAL:')
        pprint(result)
    return result

#    load_dotenv()
#    CB_API_KEY = os.environ.get('CB-API-KEY')
#    CB_SECRET_KEY = os.environ.get('CB-API-SECRET')
#    coinbase = cbp.AuthenticatedClient(CB_API_KEY, CB_SECRET_KEY, '')
#    accounts = coinbase.get_accounts()
# TODO: coinbasePro api key?
#    print(accounts)
