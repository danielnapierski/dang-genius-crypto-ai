import base64
import hashlib
import hmac
import json
import time
from typing import List

import requests
import numpy as np
import dang_genius.util as util
from gemini_api.endpoints.public import Public

from dang_genius.exchange import Exchange


class GeminiExchange(Exchange):
    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)
        self.api_url = 'https://api.gemini.com'
        self.order_endpoint = '/v1/order/new'
        self.balances_endpoint = '/v1/balances'
        self.BTC_USD_PAIR = "btcusd"
        self.BTC_SYMBOL = "BTC"
        self.USD_SYMBOL = "USD"
        self.BUY_SIDE = "buy"
        self.SELL_SIDE = "sell"
        self.public_api = Public()
        self.DIP: float = 0.0012
#        self.DIPS_BOUGHT: int = 0
#        self.STRIKES = []
#        self.MAX_STRIKES = 5
#        self.COVER: float = 500.0

    def get_nonce(self) -> str:
        my_num = int(1000 * time.time()) + 11698339415999
        return str(my_num)

    def get_balances(self) -> dict:
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
            if d.get('currency') == self.USD_SYMBOL:
                usd = float(d.get('available'))
            if d.get('currency') == self.BTC_SYMBOL:
                btc = float(d.get('available'))

        return {'BTC': btc, 'USD': usd}

    def buy_btc(self):
        print(f'BUYING {self.btc_amount:.5f} BTC GEMINI...')
        self.trade(self.BTC_USD_PAIR, self.BUY_SIDE)
        print(f'COMPLETED BUY {self.btc_amount:.5f} BTC GEMINI')

    def sell_btc(self):
        print(f'SELLING {self.btc_amount:.5f} BTC GEMINI...')
        self.trade(self.BTC_USD_PAIR, self.SELL_SIDE)
        print(f'COMPLETED SELL {self.btc_amount:.5f} BTC GEMINI')

    def set_limits(self, min_ask: float, max_bid: float) -> None:
        self.min_ask = min_ask
        self.max_bid = max_bid

    def buy_btc_dip(self):
        self.buy_the_dip(self.BTC_USD_PAIR)

    def get_btc_ticker(self):
        return self.get_ticker(self.BTC_USD_PAIR)

    def get_ticker(self, pair:str):
        ticker = self.public_api.get_ticker(pair)
        ask: float = float(ticker.get('ask'))
        bid: float = float(ticker.get('bid'))
        return {util.ASK_KEY: ask, util.BID_KEY: bid}

    def buy_the_dip(self, pair: str):
        # read the market
        # identify when a dip has occurred
        # buy at the market rate
        top_bid = 0.0
        top_ask = 0.0

        while True:
            try:
                ticker = self.public_api.get_ticker(pair)
                ask: float = float(ticker.get('ask'))
                if ask > top_ask:
                    top_ask = ask
                bid: float = float(ticker.get('bid'))

                if bid * 100 > self.strike_price_in_pennies and self.strike_price_in_pennies > 0:
                    print('GEMINI SELL IT ALL')
                    self.set_limits(bid, bid)
                    sell_tx = self.trade(pair, self.SELL_SIDE)
                    if sell_tx:
                        print(f'GEMINI SOLD: {sell_tx}')
                        time.sleep(1)

#            if len(self.STRIKES) > 0:
#                lowest_strike = np.min(self.STRIKES)
#                if lowest_strike and bid > lowest_strike:
#                    self.set_limits(bid, bid)
#                    sell_tx = self.trade(pair, self.SELL_SIDE)
#                    if sell_tx:
#                        print(f'SOLD! {sell_tx}')
#                        self.STRIKES.remove(lowest_strike)
#                        top_ask = 0.0
#                        top_bid = 0.0
#                        time.sleep(10)
                if bid > top_bid:
                    top_bid = bid
                if (ask + bid) * (1 + self.DIP) < (top_ask + top_bid):
# TODO: check funding!    and len(self.STRIKES) < self.MAX_STRIKES:
                    print(f"\nDIP {ask:8.2f} {bid:8.2f} TOP: {top_ask:8.2f} {top_bid:8.2f}")
                    self.set_limits(ask, ask)
                    tx = self.trade(pair, self.BUY_SIDE)
# STOP BUYING
#                tx = None
                    if tx:
#                    strike = float(tx.get("price")) + self.COVER
#                    print(f'SHOULD SELL FOR {strike}')
#                    self.DIPS_BOUGHT = self.DIPS_BOUGHT + 1
#                    self.STRIKES.append(strike)
                        top_ask = 0.0
                        top_bid = 0.0
                        time.sleep(10)
                time.sleep(1)
            except Exception as e:
                print(f'Gemini Exception: {e}')

    def trade(self, pair: str, side: str) -> dict:
        # https://docs.gemini.com/rest-api/#new-order
        # GEMINI does not directly support market orders because they provide you with no price protection.
        # Instead, use the “immediate-or-cancel” order execution option, coupled with an aggressive limit price
        # (i.e.very high for a buy order or very low for a sell order), to achieve the same result.
        # price = self.max_bid if side == 'buy' else  self.min_ask
        room = float((self.max_bid - self.min_ask) / 3.0)
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
                if new_order.get('remaining_amount') == '0':
                    print(f'GEMINI SUCCESS: {new_order}')
                    tx_price = new_order.get('avg_execution_price')
                    order_id = new_order.get('order_id')
                    timestamp = new_order.get('timestamp')
                    timestampms = new_order.get('timestampms')
                    return { "price": tx_price, "order_id": order_id, "timestamp": timestamp, "timestampms": timestampms}
                else:
                    print(f'GEMINI FAIL: {new_order}')
# success can be a cancelled order
# DIP 34205.19 34202.30 TOP: 34215.82 34215.81
# 2023-10-28 11:45:31.675378 min_ask:   34199.00  max_bid:   34202.30     Spread:   3.30  Fee:  33.88     GEMINI SUCCESS: {'order_id': '199089183428', 'id': '199089183428', 'symbol': 'btcusd', 'exchange': 'gemini', 'avg_execution_price': '0.00', 'side': 'buy', 'type': 'exchange limit', 'timestamp': '1698507931', 'timestampms': 1698507931799, 'is_live': False, 'is_cancelled': True, 'is_hidden': False, 'was_forced': False, 'executed_amount': '0', 'reason': 'ImmediateOrCancelWouldPost', 'options': ['immediate-or-cancel'], 'price': '34205.19', 'original_amount': '0.0001', 'remaining_amount': '0.0001'}
# 2023-10-28 11:45:55.782185 min_ask:   34189.99  max_bid:   34193.30     Spread:   3.31  Fee:  33.87     DIP 34186.96 34183.34 TOP: 34198.93 34196.61
# 2023-10-28 11:45:56.278588 min_ask:   34182.83  max_bid:   34193.30     Spread:  10.47  Fee:  33.86     GEMINI SUCCESS: {'order_id': '199089200231', 'id': '199089200231', 'symbol': 'btcusd', 'exchange': 'gemini', 'avg_execution_price': '34186.96', 'side': 'buy', 'type': 'exchange limit', 'timestamp': '1698507956', 'timestampms': 1698507956457, 'is_live': False, 'is_cancelled': False, 'is_hidden': False, 'was_forced': False, 'executed_amount': '0.0001', 'options': ['immediate-or-cancel'], 'price': '34186.96', 'original_amount': '0.0001', 'remaining_amount': '0'}

        except Exception as e:
            print(f'GEMINI EXCEPTION: {e}')

# GEMINI SUCCESS: {'order_id': '199042859145', 'id': '199042859145', 'symbol': 'btcusd', 'exchange': 'gemini', 'avg_execution_price': '0.00', 'side': 'sell', 'type': 'exchange limit', 'timestamp': '1698437764', 'timestampms': 1698437764058, 'is_live': False, 'is_cancelled': True, 'is_hidden': False, 'was_forced': False, 'executed_amount': '0', 'reason': 'ImmediateOrCancelWouldPost', 'options': ['immediate-or-cancel'], 'price': '33725.59', 'original_amount': '0.0001', 'remaining_amount': '0.0001'}
# COMPLETED SELL 0.00010 BTC GEMINI
# GEMINI SUCCESS: {'order_id': '199042855211', 'id': '199042855211', 'symbol': 'btcusd', 'exchange': 'gemini', 'avg_execution_price': '33731.99', 'side': 'sell', 'type': 'exchange limit', 'timestamp': '1698437761', 'timestampms': 1698437761686, 'is_live': False, 'is_cancelled': False, 'is_hidden': False, 'was_forced': False, 'executed_amount': '0.0001', 'options': ['immediate-or-cancel'], 'price': '33725.59', 'original_amount': '0.0001', 'remaining_amount': '0'}
