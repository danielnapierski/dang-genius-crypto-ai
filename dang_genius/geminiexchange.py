import base64
import datetime
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

    def get_nonce(self) -> str:
        return str(int(9999999999999 + time.mktime(datetime.datetime.now().timetuple()) * 1000))

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
        self.trade('buy')
        print(f'COMPLETED BUY {self.btc_amount:.5f} BTC GEMINI')

    def sell_btc(self):
        print(f'SELL {self.btc_amount:.5f} BTC GEMINI')
        self.trade('sell')
        print(f'COMPLETED SELL {self.btc_amount:.5f} BTC GEMINI')

    def trade(self, side: str) -> object:
        payload = {
            "request": self.order_endpoint,
            "nonce": self.get_nonce(),
            "symbol": "btcusd",
            "amount": self.btc_amount,
            "side": side,
            "type": "exchange limit",
            # TODO: fix market?
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

# if not payload:

# check_status = new_order['order_id']
# notes below
# import os
# from dotenv import load_dotenv
# from gemini_api.authentication import Authentication
# from gemini_api.endpoints.fund_management import FundManagement
#
# load_dotenv()
#
# auth = Authentication(
#    public_key=GE_API_KEY, private_key=GE_API_SECRET
# )
# if __name__ == "__main__":
#   x = FundManagement.get_notional_balances(
#      auth=auth, currency='USD'
#    )
#    y = x[0]
#    print(getattr(y, 'amount'))
#    print(getattr(y, 'currency'))
