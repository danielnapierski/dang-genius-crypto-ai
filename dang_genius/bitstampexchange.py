import pprint
import threading

import bitstamp.client

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class BitstampExchange(Exchange):
    def __init__(self, key: str, secret: str, client_id: str):
        super().__init__(key, secret)
        self.public_client = bitstamp.client.Public()
        self.trading_client = bitstamp.client.Trading(client_id, key, secret)
        self._lock = threading.Lock()

    @property
    def balances(self):
        with self._lock:
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
                shib = 0.0
                if 'shib_available' in keys:
                    sa = float(b['shib_available'])
                    shib = float(f'{sa: .0f}')
                return {'BTC': btc, 'USD': usd, 'ETH': eth, 'SHIB': shib}
            except Exception as e:
                print('BS balances exception')
                pprint.pprint(e)
                return None

#    def ticker(self, base:str, quote:str):
#        with self._lock:
#            t = self.public_client.ticker(base, quote)
#            return {dgu.ASK_KEY: float(t['ask']), dgu.BID_KEY: float(t['bid'])}

    @property
    def tickers(self) -> dict[str, dict | None] | None:
        with self._lock:
            try:
                tics = self.public_client.ticker(False, False)
                btc_usd = None
                eth_usd = None
                eth_btc = None
                shib_usd = None
                for i in tics:
                    p = i['pair']
                    if p == 'BTC/USD':
                        btc_usd = {dgu.ASK_KEY: float(i['ask']), dgu.BID_KEY: float(i['bid'])}
                    if p == 'ETH/USD':
                        eth_usd = {dgu.ASK_KEY: float(i['ask']), dgu.BID_KEY: float(i['bid'])}
                    if p == 'ETH/BTC':
                        eth_btc = {dgu.ASK_KEY: float(i['ask']), dgu.BID_KEY: float(i['bid'])}
                    if p == 'SHIB/USD':
                        shib_usd = {dgu.ASK_KEY: float(i['ask']), dgu.BID_KEY: float(i['bid'])}
                    if btc_usd and eth_usd and eth_btc and shib_usd:
                        break
                return {dgu.BTC_USD_PAIR: btc_usd, dgu.ETH_USD_PAIR: eth_usd,
                        dgu.ETH_BTC_PAIR: eth_btc, dgu.SHIB_USD_PAIR: shib_usd}
            except Exception as e:
                print('BS tickers exception')
                pprint.pprint(e)
                return None

    def _decode_dgu_pair(self, dgu_pair: str):
        if dgu_pair == dgu.BTC_USD_PAIR:
            return ['btc', 'usd']
        if dgu_pair == dgu.ETH_USD_PAIR:
            return ['eth', 'usd']
        if dgu_pair == dgu.ETH_BTC_PAIR:
            return ['eth', 'btc']
        if dgu_pair == dgu.FTM_USD_PAIR:
            return ['ftm', 'usd']
        if dgu_pair == dgu.SHIB_USD_PAIR:
            return ['shib', 'usd']
        if dgu_pair == dgu.AVAX_USD_PAIR:
            return ['avax', 'usd']
        if dgu_pair == dgu.LINK_USD_PAIR:
            return ['link', 'usd']
        raise Exception(f'Unsupported pair: {dgu_pair}')

    def trade(self, dgu_pair: str, side: str, amount: float, limit: float, optionality: float | None = None) -> object:
        with self._lock:
            try:
                [base, quote] = self._decode_dgu_pair(dgu_pair)
                limit = float(f'{limit:.0f}')
                response = None
                if side.lower() == 'buy':
                    response = self.trading_client.buy_limit_order(amount, limit, base, quote, ioc_order=True)
                if side.lower() == 'sell':
                    response = self.trading_client.sell_limit_order(amount, limit, base, quote, ioc_order=True)
                if not response:
                    raise Exception(f'BS no response.  {dgu_pair} {side} {amount} {limit} ')
                pprint.pprint(response)
            # {'amount': '0.00020000',
            #  'datetime': '2024-02-29 17:36:45.597000',
            #  'id': '1721930673926146',
            #  'market': 'BTC/USD',
            #  'price': '61799',
            #  'type': '0'}
                order_id = response['id']
                status_response = self.trading_client.order_status(order_id)
                pprint.pprint(status_response)
            # {'status': 'Finished',
            #  'transactions': [{'datetime': '2024-02-29 23:09:22',
            #                    'eth': '0.00500000',
            #                    'fee': '0.06675000',
            #                    'price': '3337.60000000',
            #                    'tid': 322837345,
            #                    'type': 2,
            #                    'usd': '16.68800000'}]}
                if status_response['status'] == 'Finished':
                    transaction = status_response['transactions'][0]
                # {'btc': '0.00050000',
                #  'datetime': '2024-02-29 23:21:05',
                #  'fee': '0.12282000',
                #  'price': '61410.00000000',
                #  'tid': 322838502,
                #  'type': 2,
                #  'usd': '30.70500000'}
                    return transaction
                raise Exception(f'Order Failed: {status_response}')
            except Exception as e:
                print('BS trade exception:')
                pprint.pprint(e)
                return None
