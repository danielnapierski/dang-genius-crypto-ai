import base64
#import datetime
import hashlib
import hmac
import json
from typing import List

import requests
import time
from dang_genius.exchange import Exchange


class GeminiExchange(Exchange):
    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)
        self.api_url = 'https://api.gemini.com'
        self.order_endpoint = '/v1/order/new'
        self.balances_endpoint = '/v1/balances'
        self.BTC_USD_PAIR = "btcusd"

    def get_nonce(self) -> str:
        my_num = int(1000 * time.time()) + 11698339415999
        return str(my_num)

    def get_balances(self):
        account: List[str] = ["primary"]
        payload = {}
        request_url = self.api_url + self.balances_endpoint
        payload["request"] = self.balances_endpoint
        payload["nonce"] = self.get_nonce()
        encoded_payload = json.dumps(payload).encode("utf-8")
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(
            self.secret.encode("utf-8"), b64, hashlib.sha384
        ).hexdigest()

        request_headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.key,
            "X-GEMINI-PAYLOAD": b64,
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache",
        }

        request = requests.post(
            request_url, data=None, headers=request_headers
        )
        data = request.json()
        btc = 0.0
        usd = 0.0
        for d in data:
            if d.get('currency') == 'USD':
                usd = float(d.get('available'))
            if d.get('currency') == 'BTC':
                btc = float(d.get('available'))

        return {'BTC': btc, 'USD': usd}

    def buy_btc(self):
        print(f'BUY {self.btc_amount:.5f} BTC GEMINI')
        self.trade(self.BTC_USD_PAIR, 'buy')
        print(f'COMPLETED BUY {self.btc_amount:.5f} BTC GEMINI')

    def sell_btc(self):
        print(f'SELL {self.btc_amount:.5f} BTC GEMINI')
        self.trade(self.BTC_USD_PAIR, 'sell')
        print(f'COMPLETED SELL {self.btc_amount:.5f} BTC GEMINI')

    def set_limits(self, min_ask: float, max_bid: float) -> None:
        self.min_ask = min_ask
        self.max_bid = max_bid


    def trade(self, pair:str, side: str) -> object:
        # GEMINI does not directly support market orders because they provide you with no price protection.
        # Instead, use the “immediate-or-cancel” order execution option, coupled with an aggressive limit price
        # (i.e.very high for a buy order or very low for a sell order), to achieve the same result.
        # price = self.max_bid if side == 'buy' else  self.min_ask
        room = float((self.max_bid - self.min_ask) / 4.0)
#        room = 3.0
        price = (self.min_ask + room) if side == 'buy' else (self.max_bid - room)

        payload = {
            "request": self.order_endpoint,
            "nonce": self.get_nonce(),
            "symbol": pair,
            "amount": self.btc_amount,
            "side": side,
            "type": "exchange limit",
            "price": f'{price:.2f}',
            "options": ["immediate-or-cancel"]
        }

        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.secret.encode(), b64, hashlib.sha384).hexdigest()
        request_headers = {'Content-Type': "text/plain",
                           'Content-Length': "0",
                           'X-GEMINI-APIKEY': self.key,
                           'X-GEMINI-PAYLOAD': b64,
                           'X-GEMINI-SIGNATURE': signature,
                           'Cache-Control': "no-cache"}

        try:
            new_order = requests.post(self.api_url + self.order_endpoint,
                                      data=None,
                                      headers=request_headers).json()
            if new_order.get('result') == 'error':
                print(f'GEMINI ERROR: {new_order}')
            else:
                print(f'GEMINI SUCCESS: {new_order}')

        except Exception as e:
            print(f'GEMINI EXCEPTION: {e}')
