import base64
import hashlib
import hmac
import json
import time

import requests
from gemini_api.endpoints.public import Public

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class GeminiExchange(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.api_url = 'https://api.gemini.com'
        self.order_endpoint = '/v1/order/new'
        self.balances_endpoint = '/v1/balances'
        self.BTC_USD_PAIR = "btcusd"
        self.ETH_USD_PAIR = "ethusd"
        self.ETH_BTC_PAIR = "ethbtc"
        self.BTC_SYMBOL = "BTC"
        self.USD_SYMBOL = "USD"
        self.ETH_SYMBOL = "ETH"
        self.BUY_SIDE = "buy"
        self.SELL_SIDE = "sell"
        self.public_api = Public()

    @staticmethod
    def _get_nonce() -> str:
        return str(int(1000 * time.time()) + 11698339415999)

    def _make_headers(self, request_endpoint: str):
        b64 = base64.b64encode(json.dumps({"request": request_endpoint, "nonce": self._get_nonce()}).encode("utf-8"))
        signature = hmac.new(self._secret.encode("utf-8"), b64, hashlib.sha384).hexdigest()

        return {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self._key,
            "X-GEMINI-PAYLOAD": b64,
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache",
        }

    @property
    def balances(self) -> dict:
        try:
            request_headers = self._make_headers(self.balances_endpoint)
            request = requests.post(self.api_url + self.balances_endpoint, data=None, headers=request_headers)
            data = request.json()
            btc = 0.0
            usd = 0.0
            eth = 0.0
            for d in data:
                currency = d.get('currency')
                if currency == self.BTC_SYMBOL:
                    ba = float(d.get('available'))
                    btc = float(f'{ba: .5f}')
                if currency == self.USD_SYMBOL:
                    ua = float(d.get('available'))
                    usd = float(f'{ua: .2f}')
                if currency == self.ETH_SYMBOL:
                    ea = float(d.get('available'))
                    eth = float(f'{ea: .5f}')
            return {'BTC': btc, 'USD': usd, 'ETH': eth}
        except Exception as e:
            print(f'Gemini balances exception: {e}')
            return {}

    def get_btc_ticker(self):
        return self.get_ticker(self.BTC_USD_PAIR)

    def get_ticker(self, pair: str):
        ticker = self.public_api.get_ticker(pair)
        return {dgu.ASK_KEY: (float(ticker.get('ask'))), dgu.BID_KEY: (float(ticker.get('bid')))}

    @property
    def tickers(self) -> dict[str, dict | None]:
        try:
            return {dgu.BTC_USD_PAIR: self.get_ticker(self.BTC_USD_PAIR),
                    dgu.ETH_USD_PAIR: self.get_ticker(self.ETH_USD_PAIR),
                    dgu.ETH_BTC_PAIR: self.get_ticker(self.ETH_BTC_PAIR)}
        except Exception as e:
            print(f'Gemini tickers exception: {e}')
            return {}

    def trade(self, pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        # https://docs.gemini.com/rest-api/#new-order
        payload = {
            "request": self.order_endpoint,
            "nonce": self._get_nonce(),
            "symbol": pair,
            "amount": f'{amount: 0.5f}',
            "side": side,
            "type": "exchange limit",
            "price": f'{limit: .2f}',
            "options": ["immediate-or-cancel"]
        }

        b64 = base64.b64encode(json.dumps(payload).encode())
        request_headers = {'Content-Type': "text/plain",
                           'Content-Length': "0",
                           'X-GEMINI-APIKEY': self._key,
                           'X-GEMINI-PAYLOAD': b64,
                           'X-GEMINI-SIGNATURE': (hmac.new(self._secret.encode(), b64, hashlib.sha384).hexdigest()),
                           'Cache-Control': "no-cache"}

        try:
            new_order = requests.post(self.api_url + self.order_endpoint, data=None, headers=request_headers).json()
            if new_order.get('result') == 'error':
                print(f'GEMINI ERROR: {new_order}')
            else:
                if new_order.get('remaining_amount') == '0':
                    print(f'GEMINI SUCCESS: {new_order}')
                    tx_price = new_order.get('avg_execution_price')
                    order_id = new_order.get('order_id')
                    timestamp = new_order.get('timestamp')
                    timestampms = new_order.get('timestampms')
                    # TODO: Add PAIR
                    return {"price": tx_price, "order_id": order_id, "timestamp": timestamp, "timestampms": timestampms}
                else:
                    print(f'GEMINI FAIL: {new_order}')
                    # success can be a cancelled order
        except Exception as e:
            print(f'GEMINI trade exception: {e}')
