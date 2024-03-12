import pprint
import time
from datetime import datetime
from datetime import timedelta

import coinbasepro as cbp
import requests
from coinbase import jwt_generator
from coinbase.rest import RESTClient

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class CoinbaseAdvancedExchange(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.public_client = cbp.PublicClient()
        self.private_client = RESTClient(key, secret)
        self.BTC_USD_PAIR: str = 'BTC-USD'
        self.ETH_USD_PAIR: str = 'ETH-USD'
        self.ETH_BTC_PAIR: str = 'ETH-BTC'
        self.SHIB_USD_PAIR: str = 'SHIB-USD'
        self.GALA_USD_PAIR: str = 'GALA-USD'
        self.BONK_USD_PAIR: str = 'BONK-USD'
        self.FET_USD_PAIR: str = 'FET-USD'
        self.supported_pairs = {dgu.BTC_USD_PAIR: self.BTC_USD_PAIR,
                                dgu.ETH_USD_PAIR: self.ETH_USD_PAIR,
                                dgu.ETH_BTC_PAIR: self.ETH_BTC_PAIR,
                                dgu.SHIB_USD_PAIR: self.SHIB_USD_PAIR,
                                dgu.BONK_USD_PAIR: self.BONK_USD_PAIR,
                                dgu.FET_USD_PAIR: self.FET_USD_PAIR}

        #https://docs.cloud.coinbase.com/advanced-trade-api/docs/sdk-rest-overview
    def _generate_jwt(self):
        request_method = "GET"
        request_path = "/api/v3/brokerage/accounts"
        jwt_uri = jwt_generator.format_jwt_uri(request_method, request_path)
        jwt_token = jwt_generator.build_rest_jwt(jwt_uri, self._key, self._secret)
        return jwt_token

    @property
    def balances(self) -> dict:
        try:
            response = self.private_client.get_accounts()
            balances = {}
            for account in response['accounts']:
                currency = account['currency']
                if currency in ['USD', 'BTC', 'ETH', 'SHIB']:
                    val = float(account["available_balance"]["value"])
                    if currency == 'USD':
                        balances[currency] = float(f'{val:.2f}')
                    else:
                        if currency == 'SHIB':
                            balances[currency] = float(f'{val:.0f}')
                        else:
                            balances[currency] = float(f'{val:.5f}')
            return balances
        except Exception as e:
            print('CBA balances error: ')
            pprint.pprint(e)
            return {}

    def get_ticker(self, pair: str) -> dict[str, float] | None:
        try:
            time.sleep(0.003)
            order_book = self.public_client.get_product_order_book(pair)
            return {dgu.ASK_KEY: (float(order_book.get('asks')[0][0])),
                    dgu.BID_KEY: (float(order_book.get('bids')[0][0]))}
        except requests.exceptions.ReadTimeout as readtimeout_error:
            print(f'CBA ticker ReadTimeout error: {readtimeout_error}')
            return None
        except Exception as error:
            print(f'CBA ticker Exception error: {error}')
            return None

    @property
    def tickers(self) -> dict[str, dict | None]:
        return {dgu.BTC_USD_PAIR: self.get_ticker(self.BTC_USD_PAIR),
                dgu.ETH_USD_PAIR: self.get_ticker(self.ETH_USD_PAIR),
                dgu.ETH_BTC_PAIR: self.get_ticker(self.ETH_BTC_PAIR),
                dgu.SHIB_USD_PAIR: self.get_ticker(self.SHIB_USD_PAIR)}

    def match_pair(self, dgu_pair: str):
        if dgu_pair in self.supported_pairs.keys():
            return self.supported_pairs[dgu_pair]
        raise Exception(f'Unsupported pair: {dgu_pair}')

    def trade(self, dgu_pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        try:
            client_order_id = dgu.generate_order_id(self)
            product_id = self.match_pair(dgu_pair)
            base_size = f'{amount:.5f}'
            now = datetime.now(tz=dgu.TZ_UTC)
            end_time = now + timedelta(milliseconds=3001)
            order_response = self.private_client.limit_order_gtd(
                client_order_id, product_id, side.upper(), base_size, f'{limit:.5f}', dgu.time_str(end_time))
            if 'error_response' in order_response.keys():
                print('CBA trade error: ')
                pprint.pprint(order_response)
                return

            order_id = order_response["order_id"]
#            print(f'ORDER ID: {order_id}')

            for t in [100, 200, 400, 2600]:
                time.sleep(float(t / 1000.0))
                fills_response = self.private_client.get_fills(order_id=order_id)
                fills = fills_response['fills']
                if fills:
                    for f in fills:
                        if order_id == f['order_id']:
#                            pprint.pprint(f)
                            # {'commission': '0.NNNNN',
                            #  'entry_id': 'HASH...',
                            #  'liquidity_indicator': 'TAKER',
                            #  'order_id': 'HASH...',
                            #  'price': 'NUM_USD_DOLLARS',
                            #  'product_id': 'BTC-USD',
                            #  'sequence_timestamp': '2024-12-29T17:08:21.462918Z',
                            #  'side': 'BUY',
                            #  'size': '0.0001',
                            #  'size_in_quote': False,
                            #  'trade_id': 'HASH...',
                            #  'trade_time': '2024-12-29T17:08:21.459857Z',
                            #  'trade_type': 'FILL',
                            #  'user_id': 'may_be_same_as_principal_in_api_key_json'}
                            return f
        except Exception as e:
            print('CBA trade error: ')
            pprint.pprint(e)
