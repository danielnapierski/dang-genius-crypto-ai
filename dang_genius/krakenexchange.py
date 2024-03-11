import base64
import hashlib
import hmac
import json
import time
import urllib.parse

import krakenex
import requests
import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class KrakenExchange(Exchange):

    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.api_url = "https://api.kraken.com"
        self.BTC_USD_PAIR: str = "XXBTZUSD"
        self.ETH_USD_PAIR: str = "XETHZUSD"
        self.ETH_BTC_PAIR: str = "XETHXXBT"
        self.SHIB_USD_PAIR: str = "SHIBUSD"
        self.SAMO_USD_PAIR: str = "SAMOUSD"
        self.FET_USD_PAIR: str = "FETUSD"
        self.supported_pairs = {dgu.BTC_USD_PAIR: self.BTC_USD_PAIR,
                                dgu.ETH_USD_PAIR: self.ETH_USD_PAIR,
                                dgu.ETH_BTC_PAIR: self.ETH_BTC_PAIR,
                                dgu.SAMO_USD_PAIR: self.SAMO_USD_PAIR,
                                dgu.SHIB_USD_PAIR: self.SHIB_USD_PAIR,
                                dgu.FET_USD_PAIR: self.FET_USD_PAIR}
#KRAKEN ERROR: ['EAccount:Invalid permissions:SAMO trading restricted for US:MA.']
#        The
#        following
#        assets
#        are
#        restricted
#        for US clients:  ACA, AGLD, ALICE, ASTR, ATLAS, AUDIO, AVT, BONK, CFG, CSM, C98, GENS, GLMR, HDX, INJ, INTR, JASMY, KIN, LMWR, MC, MV, NMR, NODL, NYM, ORCA, OTP, OXY, PARA, PEPE, PERP, PICA, POL, PSTAKE, PYTH, RAY, REQ, ROOK, SAMO, SDN, STEP, SUI, SXP, TEER, WETH, WIF, WOO, YGG or XRT.
        self.GALA_USD_PAIR: str = "GALAUSD"
        self.FTM_USD_PAIR: str = "FTMUSD"
        self.public_client = krakenex.API()
        self.private_client = krakenex.API(self._key, self._secret)

    @property
    def balances(self) -> dict:
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
        headers = {'API-Key': api_key, 'API-Sign': self._get_kraken_signature(uri_path, data, api_sec)}
        return requests.post((self.api_url + uri_path), headers=headers, data=data)

    def get_btc_ticker(self):
        return self.get_ticker(self.BTC_USD_PAIR)

    def get_ticker(self, pair: str):
        tic = self.public_client.query_public('Depth',
                                               {'pair': pair, 'count': '10'}).get('result').get(pair)
        return {dgu.ASK_KEY: (float(tic.get('asks')[0][0])), dgu.BID_KEY: (float(tic.get('bids')[0][0]))}

    @property
    def tickers(self) -> dict[str, dict | None]:
        try:
            time.sleep(0.05)
            return {dgu.BTC_USD_PAIR: self.get_ticker(self.BTC_USD_PAIR),
                    dgu.ETH_USD_PAIR: self.get_ticker(self.ETH_USD_PAIR),
                    dgu.ETH_BTC_PAIR: self.get_ticker(self.ETH_BTC_PAIR),
                    dgu.SHIB_USD_PAIR: self.get_ticker(self.SHIB_USD_PAIR)}
        except Exception as e:
            print(f'Gemini tickers exception: {e}')
            return {}

    def match_pair(self, dgu_pair: str):
        if dgu_pair in self.supported_pairs.keys():
            return self.supported_pairs[dgu_pair]
        raise Exception(f'Unsupported pair: {dgu_pair}')

    def trade(self, dgu_pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        try:
            price = f'{limit:.5f}'
            if dgu.BTC_USD_PAIR == dgu_pair:
                price = f'{limit:.1f}'
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
                print(f'KRAKEN ERROR: {error}')
            else:
                result = json_response.get('result')
                #{'txid': [''], 'descr' : {'order': 'buy ...'}}
                txid = result['txid'][0]
                if self.is_trade_closed(txid):
                    return result
        except Exception as e:
            print(f'KRAKEN Exception: {e}')



    def is_trade_closed(self, txid: str):
        print(f'Kraken TXID {txid}')
        time.sleep(0.01)
        response = self._kraken_request('/0/private/ClosedOrders', {
            "nonce": str(int(1000 * time.time()))
        }, self._key, self._secret).json()
        closed = response['result']['closed']
        tx = closed[txid]
        status = tx['status']
# status could be 'closed' 'canceled' or something else possibly
        return 'closed' == status
