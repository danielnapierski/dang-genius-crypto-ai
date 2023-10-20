from dang_genius.exchange import Exchange


class KrakenExchange(Exchange):
    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)

    def buyBtc(self):
        print(f'BUY {self.btc_amount:.5f} BTC KRAKEN')

    def sellBtc(self):
        print(f'SELL {self.btc_amount:.5f} BTC KRAKEN DONT WE HAVE BTCCCCCCC')

    def buyBitcoin(self, amount: float) -> dict:
        print(f'{amount:.5f}')
#        KR_API_KEY = os.environ.get('KR-API-KEY')
#        KR_API_SECRET = os.environ.get('KR-API-SECRET')

#        k = krakenex.API(KR_API_KEY, KR_API_SECRET)
#        b = k.query_private('Balance')['result']
#        btc_b = float(b.get('XXBT'))
#         # TODO: kraken USD?
#        usd_b = float(-1.0)
#        return {'BTC': btc_b, 'USD': usd_b}



        return dict(MSG="Failed")



#import time
#import os
#import requests

# Read Kraken API key and secret stored in environment variables
#api_url = "https://api.kraken.com"
#api_key = os.environ['API_KEY_KRAKEN']
#api_sec = os.environ['API_SEC_KRAKEN']

# Attaches auth headers and returns results of a POST request
#def kraken_request(uri_path, data, api_key, api_sec):
#    headers = {}
#    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
#    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
#    req = requests.post((api_url + uri_path), headers=headers, data=data)
#    return req

# Construct the request and print the result
#resp = kraken_request('/0/private/AddOrder', {
#    "nonce": str(int(1000*time.time())),
#    "ordertype": "limit",
#    "type": "buy",
#    "volume": 1.25,
#    "pair": "XBTUSD",
#    "price": 27500
#}, api_key, api_sec)

#print(resp.json())
