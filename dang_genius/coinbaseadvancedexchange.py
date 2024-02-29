import hashlib
import hmac
import json
import pprint
import time
from datetime import datetime
from datetime import timedelta

import coinbasepro as cbp
from coinbase.rest import RESTClient
from coinbase import jwt_generator
import requests

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class CoinbaseAdvancedExchange(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.api_url = 'https://coinbase.com'
        self.order_endpoint = "/api/v3/brokerage/orders"
        self.public_client = cbp.PublicClient()
        self.private_client = RESTClient(key, secret)
        self.BTC_USD_PAIR: str = 'BTC-USD'
        self.ETH_USD_PAIR: str = 'ETH-USD'
        self.ETH_BTC_PAIR: str = 'ETH-BTC'
        self.BUY_SIDE: str = 'BUY'
        self.SELL_SIDE: str = 'SELL'
        self.DIP: float = 0.0012

    #https: // docs.cloud.coinbase.com / advanced - trade - api / docs / rest - api - overview
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
                if currency in ['USD', 'BTC', 'ETH']:
                    val = float(account["available_balance"]["value"])
                    if currency == 'USD':
                        balances[currency] = float(f'{val:.2f}')
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
                dgu.ETH_BTC_PAIR: self.get_ticker(self.ETH_BTC_PAIR)}


    def match_pair(self, dgu_pair: str):
        if dgu_pair == dgu.BTC_USD_PAIR:
            return self.BTC_USD_PAIR
        if dgu_pair == dgu.ETH_USD_PAIR:
            return self.ETH_USD_PAIR
        if dgu_pair == dgu.ETH_BTC_PAIR:
            return self.ETH_BTC_PAIR
        raise Exception(f'Unsupported pair: {dgu_pair}')

    #    https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder
    def trade(self, dgu_pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        try:
            now = datetime.now(tz=dgu.TZ_UTC)
            client_order_id = 'CB-order-' + now.strftime(dgu.DATETIME_FORMAT)
            end_time = now + timedelta(milliseconds=2001)
            ets = end_time.strftime(dgu.DATETIME_FORMAT)
            timestamp = str(int(time.time()))
            payload = {
                "side": side,
                "client_order_id": client_order_id,
                "product_id": self.match_pair(dgu_pair),
                "order_configuration": {
                    "limit_limit_gtd": {
                        "base_size": f'{amount:0.5f}',
                        "limit_price": f'{limit:0.2f}',
                        "end_time": ets,
                        "post_only": False
                    }
                }
            }
            message = timestamp + "POST" + self.order_endpoint + json.dumps(payload)
            signature = hmac.new(self._secret.encode('utf-8'), message.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
            headers = {
                'CB-ACCESS-SIGN': signature.hex(),
                'CB-ACCESS-TIMESTAMP': timestamp,
                'CB-ACCESS-KEY': self._key,
                'User-Agent': 'my-user-agent',
                'accept': "application/json",
                'Content-Type': 'application/json'
            }

            new_order = requests.post(self.api_url + self.order_endpoint,
                                      data=json.dumps(payload), headers=headers).json()
            if new_order.get('result') == 'error':
                # TODO: retry??
                print(f'CBA ERROR: {new_order}')
            else:
                if new_order.get('error') == 'unknown':
                    print(f'CBA UNKNOWN ERROR {new_order}')
                else:
                    if (new_order.get('success') and new_order.get('success_response')
                            and new_order.get('order_configuration')
                            and new_order.get('order_configuration').get('limit_limit_gtd')):
                        response = new_order.get('success_response')
                        print(f'CB SUCCESS: {response}')
                        order_id = new_order.get('order_id')
                        product_id = new_order.get('product_id')
                        side = new_order.get('side')
                        client_order_id = new_order.get('client_order_id')
                        # TODO: get actual execution price and amount
                        config = new_order.get('order_configuration').get('limit_limit_gtd')
                        print("ORDER:")
                        print(new_order)
                        # example: {'success': True, 'failure_reason': 'UNKNOWN_FAILURE_REASON',
                        # 'order_id': '65dba34e-0796-493c-a422-bda3a928b881',
                        # 'success_response': {'order_id': '65dba34e-0796-493c-a422-bda3a928b881',
                        # 'product_id': 'BTC-USD', 'side': 'BUY', 'client_order_id':
                        # 'CB-order-2024-02-27T15:23:54.162218Z'}, 'order_configuration': {'limit_limit_gtd':
                        # {'base_size': '0.00010', 'limit_price': '57450.00',
                        # 'end_time': '2024-02-27T15:23:56.163218Z', 'post_only': False}}}
                        tx_price = config.get('limit_price')
                        # TODO: timestampms
                        # TODO: add KEYS to self
                        # TODO: ADD PAIR
                        return {"price": tx_price, "order_id": order_id, "timestamp": timestamp,
                                "timestampms": timestamp}
                print(f'CBA ERROR {new_order}')

        except Exception as e:
            print(f'CBA EXCEPTION: {e}')

