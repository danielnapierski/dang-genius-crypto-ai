import os
from threading import Thread
from dotenv import load_dotenv
from dang_genius.coinbaseexchange import CoinbaseExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange


class Conductor:
    def __init__(self):
        self.env_loaded = load_dotenv()
        self.fee_estimate = float(os.environ.get('FEE-ESTIMATE'))
        self.btc_amount = float(os.environ.get('BTC-SWAP-AMT'))
        self.usd_amount = float(os.environ.get('USD-SWAP-AMT'))
        self.exchanges = {
            CoinbaseExchange:
                CoinbaseExchange(os.environ.get('CB-API-KEY'), os.environ.get('CB-API-SECRET'), self.btc_amount),
            GeminiExchange:
                GeminiExchange(os.environ.get('GE-API-KEY'), os.environ.get('GE-API-SECRET'), self.btc_amount),
            KrakenExchange:
                KrakenExchange(os.environ.get('KR-API-KEY'), os.environ.get('KR-API-SECRET'), self.btc_amount)}

    def buy_btc_sell_btc(self, exchange_to_buy_btc: type, exchange_to_sell_btc: type,
                         min_ask: float, max_bid: float) -> None:
        be = self.exchanges.get(exchange_to_buy_btc)
        be.set_limits(min_ask, max_bid)
        Thread(target=be.buy_btc).start()

        se = self.exchanges.get(exchange_to_sell_btc)
        se.set_limits(min_ask, max_bid)
        Thread(target=se.sell_btc).start()

    def buy_the_dip(self):
        gemini_ex = self.exchanges.get(GeminiExchange)
        Thread(target=gemini_ex.buy_btc_dip).start()

        coinbase_ex = self.exchanges.get(CoinbaseExchange)
        Thread(target=coinbase_ex.buy_btc_dip).start()
