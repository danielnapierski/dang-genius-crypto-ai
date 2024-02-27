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
            keys = b.keys()
            if 'btc_available' in keys:
                ba = float(b['btc_available'])
                btc = float(f'{ba: .5f}')
            eth = 0.0
            if 'eth_available' in keys:
                ea = float(b['eth_available'])
                eth = float(f'{ea: .5f}')
            usd = 0.0
            if 'usd_available' in keys:
                ua = float(b['usd_available'])
                usd = float(f'{ua: .2f}')
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
            tics = self.public_client.ticker(False, False)
            btc_usd = None
            eth_usd = None
            eth_btc = None
            for i in tics:
                p = i['pair']
                if p == 'BTC/USD':
                    btc_usd = {dgu.ASK_KEY: float(i['ask']), dgu.BID_KEY: float(i['bid'])}
                if p == 'ETH/USD':
                    eth_usd = {dgu.ASK_KEY: float(i['ask']), dgu.BID_KEY: float(i['bid'])}
                if p == 'ETH/BTC':
                    eth_btc = {dgu.ASK_KEY: float(i['ask']), dgu.BID_KEY: float(i['bid'])}
                if btc_usd and eth_usd and eth_btc:
                    break

            return {dgu.BTC_USD_PAIR: btc_usd, dgu.ETH_USD_PAIR: eth_usd, dgu.ETH_BTC_PAIR: btc_usd}
        except Exception as e:
            print('BS tickers exception')
            pprint.pprint(e)
            return None


    def trade(self, pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        raise NotImplementedError("Exchanges should implement trading.")
