import base64
import hashlib
import hmac
import json
import threading
import time
import urllib.parse

import krakenex
import requests
import dang_genius.util as dgu
from dang_genius.exchange import Exchange


# See:
# # Note ['EAccount:Invalid permissions:SAMO trading restricted for US:MA.']
# # The following assets are restricted for US clients:
# # ACA, AGLD, ALICE, ASTR, ATLAS, AUDIO, AVT, BONK, CFG, CSM, C98, GENS, GLMR, HDX, INJ, INTR, JASMY, KIN, LMWR, MC,
# # MV, NMR, NODL, NYM, ORCA, OTP, OXY, PARA, PEPE, PERP, PICA, POL, PSTAKE, PYTH, RAY, REQ, ROOK, SAMO, SDN, STEP, SUI,
# # SXP, TEER, WETH, WIF, WOO, YGG or XRT.
class KrakenExchange(Exchange):

    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.api_url = "https://api.kraken.com"
        self.supported_pairs = {dgu.BTC_USD_PAIR: "XXBTZUSD",
                                dgu.ETH_USD_PAIR: "XETHZUSD",
                                dgu.ETH_BTC_PAIR: "XETHXXBT",
                                dgu.SHIB_USD_PAIR: "SHIBUSD",
                                dgu.FET_USD_PAIR: "FETUSD",
                                dgu.GALA_USD_PAIR: "GALAUSD",
                                dgu.FTM_USD_PAIR: "FTMUSD"}
        self.public_client = krakenex.API()
        self.private_client = krakenex.API(self._key, self._secret)
        self._lock = threading.Lock()


    @property
    def balances(self) -> dict:
        with self._lock:
            b = self.private_client.query_private('Balance')['result']
        xxbt = float(b.get('XXBT'))
        zusd = float(b.get('ZUSD'))
        xeth = float(b.get('XETH'))
        shib = float(b.get('SHIB'))
        return {'BTC': float(f'{xxbt: .5f}'), 'USD': float(f'{zusd: .2f}'),
                'ETH': float(f'{xeth: .5f}'), 'SHIB': (float(f'{shib: .0f}'))}

    @staticmethod
    def _get_kraken_signature(urlpath, data, secret):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def _kraken_request(self, uri_path, data, api_key, api_sec):
        with self._lock:
            headers = {'API-Key': api_key, 'API-Sign': self._get_kraken_signature(uri_path, data, api_sec)}
            return requests.post((self.api_url + uri_path), headers=headers, data=data)

    def get_btc_ticker(self):
        return self.get_ticker(self.BTC_USD_PAIR)

    def get_ticker(self, pair: str):
        with self._lock:
            tic = self.public_client.query_public('Depth',
                                                   {'pair': pair, 'count': '10'}).get('result').get(pair)
            return {dgu.ASK_KEY: (float(tic.get('asks')[0][0])), dgu.BID_KEY: (float(tic.get('bids')[0][0]))}

    @property
    def tickers(self) -> dict[str, dict | None]:
        try:
            return {dgu.BTC_USD_PAIR: self.get_ticker(self.supported_pairs[dgu.BTC_USD_PAIR]),
                    dgu.ETH_USD_PAIR: self.get_ticker(self.supported_pairs[dgu.ETH_USD_PAIR]),
                    dgu.ETH_BTC_PAIR: self.get_ticker(self.supported_pairs[dgu.ETH_BTC_PAIR]),
                    dgu.SHIB_USD_PAIR: self.get_ticker(self.supported_pairs[dgu.SHIB_USD_PAIR])}
        except Exception as e:
            print(f'KRAKEN tickers exception: {e}')
            return {}

    def match_pair(self, dgu_pair: str):
        if dgu_pair in self.supported_pairs.keys():
            return self.supported_pairs[dgu_pair]
        raise Exception(f'Unsupported pair: {dgu_pair}')

    def trade(self, dgu_pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        try:
            price = f'{limit:.1f}' if dgu.BTC_USD_PAIR == dgu_pair else f'{limit:.5f}'
            response = self._kraken_request('/0/private/AddOrder', {
                "nonce": str(int(1000 * time.time())),
                "ordertype": "limit",
                "price": price,
                "type": side.lower(),
                "volume": amount,
                "pair": self.match_pair(dgu_pair),
                "timeinforce": "ioc"
            }, self._key, self._secret)

            json_response = json.loads(getattr(response, 'text'))
            error = json_response.get('error')
            if error:
                raise Exception(f'KRAKEN AddOrder error response: {error}\n{dgu_pair}|{price}|{amount}|{side}')
            result = json_response.get('result')
            #{'txid': [''], 'descr' : {'order': 'buy ...'}}
            txid = result['txid'][0]
            if self._is_trade_closed(txid):
                return result
            print('KRAKEN tx failed.')

        except Exception as e:
            print(f'KRAKEN Exception: {e}')



    def _is_trade_closed(self, txid: str):
        response = self._kraken_request('/0/private/ClosedOrders', {
            "nonce": str(int(1000 * time.time()))
        }, self._key, self._secret).json()
        # status could be 'closed' 'canceled' or something else possibly
        return 'closed' == response['result']['closed'][txid]['status']
