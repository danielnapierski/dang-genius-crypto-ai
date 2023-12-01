import base64
import hashlib
import hmac
import json
import time
import urllib.parse

import krakenex
import requests
import dang_genius.util as util
from dang_genius.exchange import Exchange


class KrakenExchange(Exchange):

    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)
        self.api_url = "https://api.kraken.com"
        self.BTC_USD_PAIR: str = "XBTUSD"
        self.public_client = krakenex.API()
        self.public_pair: str = 'XXBTZUSD'
        self.private_client = krakenex.API(self.key, self.secret)

    def get_balances(self) -> dict:
        b = self.private_client.query_private('Balance')['result']
        btc_b = float(b.get('XXBT'))
        usd_b = float(b.get('ZUSD'))
        return {'BTC': btc_b, 'USD': usd_b}

    def get_kraken_signature(self, urlpath, data, secret):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def kraken_request(self, uri_path, data, api_key, api_sec):
        headers = {'API-Key': api_key, 'API-Sign': self.get_kraken_signature(uri_path, data, api_sec)}
        req = requests.post((self.api_url + uri_path), headers=headers, data=data)
        return req

    def buy_btc(self):
        self.trade(self.BTC_USD_PAIR, "buy")

    def sell_btc(self):
        print('KRAKEN SELLING')
        self.trade(self.BTC_USD_PAIR, "sell")

    def set_limits(self, min_ask: float, max_bid: float) -> None:
        self.min_ask = min_ask
        self.max_bid = max_bid

    def get_btc_ticker(self):
        return self.get_ticker(self.BTC_USD_PAIR)

    def get_ticker(self, pair: str):
        kraken_public_result = (
            self.public_client.query_public('Depth', {'pair': self.public_pair, 'count': '10'}).get('result').get(self.public_pair))
        ask: float = float(kraken_public_result.get('asks')[0][0])
        bid: float = float(kraken_public_result.get('bids')[0][0])
        return {util.ASK_KEY: ask, util.BID_KEY: bid}

        # $ ./krakenapi AddOrder pair=xdgusd type=buy ordertype=limit price=1.00 volume=50
        # timeinforce=ioc{"error":[],"result":{"txid":["OZS2KT-JVN2E-J2XM7Z"],"descr":{"order":"buy 50.00000000 XDGUSD @ limit 1.0000000"}}}

    def trade(self, pair: str, side: str):
        print(f'TRADE {side} {self.btc_amount:.5f} {pair} KRAKEN ...')
        room = float((self.max_bid - self.min_ask) / 3.0)
        price = (self.min_ask + room) if side == 'buy' else (self.max_bid - room)
        resp = self.kraken_request('/0/private/AddOrder', {
            "nonce": str(int(1000 * time.time())),
            "ordertype": "limit",
            "price": f'{price:.1f}',
            "type": side,
            "volume": self.btc_amount,
            "pair": pair,
            "timeinforce": "ioc"
        }, self.key, self.secret)

        print(f'STARTED {side} {self.btc_amount:.5f} {pair} KRAKEN')
        text_resp = getattr(resp, 'text')
        j = json.loads(text_resp)
        error = j.get('error')
        if error:
            print(f'KRAKEN ERROR: {error}')
        else:
            print(f'KRAKEN SUCCESS: {j}')
        print('</KRAKEN>')

    def market_trade(self, pair: str, side: str):
        print(f'TRADE {side} {self.btc_amount:.5f} {pair} KRAKEN ...')
        # Construct the request and print the result
        resp = self.kraken_request('/0/private/AddOrder', {
            "nonce": str(int(1000 * time.time())),
            "ordertype": "market",
            "type": side,
            "volume": self.btc_amount,
            "pair": pair,
        }, self.key, self.secret)

        print(f'STARTED {side} {self.btc_amount:.5f} {pair} KRAKEN')
        text_resp = getattr(resp, 'text')
        j = json.loads(text_resp)
        error = j.get('error')
        if error:
            print(f'KRAKEN ERROR: {error}')
        else:
            print(f'KRAKEN SUCCESS: {j}')
        print('</KRAKEN>')

# KRAKEN SUCCESS: {'error': [], 'result': {'txid': ['O6R2WB-HQXUF-HIF7VC'], 'descr': {'order': 'buy 0.00010000 XBTUSD @ limit 33706.4'}}}
# KRAKEN SUCCESS: {'error': [], 'result': {'txid': ['OJV7EF-ETEL6-PBIJFF'], 'descr': {'order': 'buy 0.00010000 XBTUSD @ limit 33706.4'}}}
