import base64
import hashlib
import json
import hmac
import time
import urllib.parse
import requests
from dang_genius.exchange import Exchange


class KrakenExchange(Exchange):

    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)
        self.api_url = "https://api.kraken.com"
        self.BTC_USD_PAIR: str = "XBTUSD"

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

    def trade(self, pair: str, side: str):
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
