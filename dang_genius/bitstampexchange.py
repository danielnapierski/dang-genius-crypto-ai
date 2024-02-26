import pprint

import bitstamp.client

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class BitstampExchange(Exchange):
    def __init__(self, key: str, secret: str, client_id: str):
        super().__init__(key, secret)
        self.public_client = bitstamp.client.Public()
        self.trading_client = bitstamp.client.Trading(client_id, key, secret)


    @property
    def balances(self):
        try:
            b = self.trading_client.account_balance(False,False)
            btc = 0.0
            if 'btc_available' in b.keys():
                ba = float(b['btc_available'])
                btc = float(f'{ba: .5f}')
            usd = 0.0
            if 'usd_available' in b.keys():
                ua = float(b['usd_available'])
                usd = float(f'{ua: .2f}')
            eth = 0.0
            if 'eth_available' in b.keys():
                ea = float(b['eth_available'])
                eth = float(f'{ea: .5f}')
            return {'BTC': btc, 'USD': usd, 'ETH': eth}
        except Exception as e:
            print('BS balances exception')
            pprint.pprint(e)
            return {}

    def ticker(self, base:str, quote:str):
        t = self.public_client.ticker(base, quote)
        return {dgu.ASK_KEY: float(t['ask']), dgu.BID_KEY: float(t['bid'])}

    @property
    def tickers(self) -> dict[str, dict | None] | None:
        try:
            return {dgu.BTC_USD_PAIR: (self.ticker("btc", "usd")),
                    dgu.ETH_USD_PAIR: (self.ticker("eth", "usd")),
                    dgu.ETH_BTC_PAIR: (self.ticker("eth", "btc"))}
        except Exception as e:
            print('BS tickers exception')
            pprint.pprint(e)
            return None


    def trade(self, pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        raise NotImplementedError("Exchanges should implement trading.")
