import hashlib
import hmac

import json
import time

import requests

from dang_genius.exchange import Exchange


class CoinbaseExchange(Exchange):
    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)
        self.api_url = 'https://coinbase.com'
        self.order_endpoint = "/api/v3/brokerage/orders"
        self.BTC_USD_PAIR: str = 'BTC-USD'



    def buy_btc(self):
        print(f'BUY {self.btc_amount:.5f} BTC COINBASE')
        self.trade(self.BTC_USD_PAIR, 'BUY')

    def sell_btc(self):
        print(f'SELL {self.btc_amount:.5f} BTC COINBASE')
        self.trade(self.BTC_USD_PAIR, 'SELL')

    def set_limits(self, min_ask: float, max_bid: float) -> None:
        self.min_ask = min_ask
        self.max_bid = max_bid

#    https: // docs.cloud.coinbase.com / advanced - trade - api / reference / retailbrokerageapi_postorder
    def trade(self, pair: str, side: str):
        # market orders set size [optional]* Desired amount in BTC
        # time_in_force = 'FOK' not for market
        # client_order_id can be added later must be UNIQ

        quote_size = f'{self.btc_amount * self.min_ask:.2f}'
        print(quote_size)
        mm = {"quote_size":quote_size} if side == "BUY" else {"base_size": self.btc_amount}

        timestamp = str(int(time.time()))

        payload = {
            "side": side,
            "client_order_id": f'CB-order-{timestamp}',
            "product_id": self.BTC_USD_PAIR,
            "order_configuration": {
                "market_market_ioc": mm
                }
        }

        message = timestamp + "POST" + self.order_endpoint + json.dumps(payload)
        signature = hmac.new(self.secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
        headers = {
            'CB-ACCESS-SIGN': signature.hex(),
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.key,
            'User-Agent': 'my-user-agent',
            'accept': "application/json",
            'Content-Type': 'application/json'
        }
#        conn.request("POST", self.order_endpoint, json.dumps(payload), headers)

        try:
            new_order = requests.post(self.api_url + self.order_endpoint,
                                      data=json.dumps(payload),headers=headers).json()
            if new_order.get('result') == 'error':
                print(f'CB ERROR: {new_order}')
            else:
                print(f'CB SUCCESS: {new_order}')

        except Exception as e:
            print(f'CB EXCEPTION: {e}')


#        res = conn.getresponse()
#        data = res.read()
#        print(data.decode("utf-8"))
