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

    def get_kraken_signature(self, urlpath, data, secret):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def kraken_request(self, uri_path, data, api_key, api_sec):
        headers = {'API-Key': api_key, 'API-Sign': self.get_kraken_signature(uri_path, data, api_sec)}
        # get_kraken_signature() as defined in the 'Authentication' section
        req = requests.post((self.api_url + uri_path), headers=headers, data=data)
        return req

    def buy_btc(self):
        print(f'BUY {self.btc_amount:.5f} BTC KRAKEN ...')
        # Construct the request and print the result
        resp = self.kraken_request('/0/private/AddOrder', {
            "nonce": str(int(1000 * time.time())),
            "ordertype": "market",
            "type": "buy",
            "volume": self.btc_amount,
            "pair": "XBTUSD",
        }, self.key, self.secret)
        print(f'STARTED BUY {self.btc_amount:.5f} BTC KRAKEN')
        text_resp = getattr(resp, 'text')
        j = json.loads(text_resp)
        error = j.get('error')
        if error:
            print(f'KRAKEN ERROR: {error}')
        else:
            print(f'KRAKEN SUCCESS: {j}')
        print('</KRAKEN>')

    def sell_btc(self):
        print(f'SELL {self.btc_amount:.5f} BTC KRAKEN DONT WE HAVE BTCCCCCCC')

# TODO: Delete NOTES
#    data = {
#        "nonce": "1616492376594",
#        "ordertype": "limit",
#        "pair": "XBTUSD",
#        "price": 37500,
#        "type": "buy",
#        "volume": 1.25
#    }
#    signature = get_kraken_signature("/0/private/AddOrder", data, self.secret)
#    print("API-Sign: {}".format(signature))
#    def buyBitcoin(self, amount: float) -> dict:
#        print(f'{amount:.5f}')
#        KR_API_KEY = os.environ.get('KR-API-KEY')
#        KR_API_SECRET = os.environ.get('KR-API-SECRET')
#        k = krakenex.API(KR_API_KEY, KR_API_SECRET)
#        b = k.query_private('Balance')['result']
#        btc_b = float(b.get('XXBT'))
# TODO: kraken USD?
#        usd_b = float(-1.0)
#        return {'BTC': btc_b, 'USD': usd_b}
#        return dict(MSG="Failed")
# Read Kraken API key and secret stored in environment variables
# api_key = os.environ['API_KEY_KRAKEN']
# api_sec = os.environ['API_SEC_KRAKEN']
# Attaches auth headers and returns results of a POST request
# def kraken_request(uri_path, data, api_key, api_sec):
#    headers = {}
#    headers['API-Key'] = api_key
# get_kraken_signature() as defined in the 'Authentication' section
#    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
#    req = requests.post((api_url + uri_path), headers=headers, data=data)
#    return req
# Construct the request and print the result
# resp = kraken_request('/0/private/AddOrder', {
#    "nonce": str(int(1000*time.time())),
#    "ordertype": "limit",
#    "type": "buy",
#    "volume": 1.25,
#    "pair": "XBTUSD",
#    "price": 27500
# }, api_key, api_sec)
# print(resp.json())
