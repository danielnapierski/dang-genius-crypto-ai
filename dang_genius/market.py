import sys
from datetime import datetime

import coinbasepro as cbp
import krakenex
import numpy as np
from gemini_api.endpoints.public import Public
from requests.exceptions import HTTPError

import dang_genius.util as util
from dang_genius.coinbaseexchange import CoinbaseExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange

kraken = krakenex.API()
kraken_pair: str = 'XXBTZUSD'
coinbase = cbp.PublicClient()
cb_pair: str = 'BTC-USD'
gemini = Public()
ge_pair: str = 'BTCUSD'
asks: dict = {}
bids: dict = {}


def market_check(fee_estimate: float) -> dict:
    try:
        kraken_public_result = (
            kraken.query_public('Depth', {'pair': kraken_pair, 'count': '10'}).get('result').get(kraken_pair))
        kraken_ask: float = float(kraken_public_result.get('asks')[0][0])
        asks[kraken_ask] = KrakenExchange
        kraken_bid: float = float(kraken_public_result.get('bids')[0][0])
        bids[kraken_bid] = KrakenExchange

        coinbase_order_book = coinbase.get_product_order_book(cb_pair)
        coinbase_ask: float = float(coinbase_order_book.get('asks')[0][0])
        asks[coinbase_ask] = CoinbaseExchange
        coinbase_bid: float = float(coinbase_order_book.get('bids')[0][0])
        bids[coinbase_bid] = CoinbaseExchange

        gemini_ticker = gemini.get_ticker(ge_pair)
        gemini_ask: float = float(gemini_ticker.get('ask'))
        asks[gemini_ask] = GeminiExchange
        gemini_bid: float = float(gemini_ticker.get('bid'))
        bids[gemini_bid] = GeminiExchange

        max_bid = np.max([kraken_bid, coinbase_bid, gemini_bid])
        min_ask = np.min([kraken_ask, coinbase_ask, gemini_ask])
        spread = max_bid - min_ask
        fee = min_ask * fee_estimate
        fee = fee + float(0.02)
        sys.stdout.write(
            f'\r{datetime.now()} min_ask: {min_ask:10.2f}\tmax_bid: {max_bid:10.2f}\t'
            f'Spread: {spread:6.2f}\tFee: {fee:6.2f}\t')
        sys.stdout.flush()

        if spread > fee:
            return {util.BUY_KEY: asks[min_ask], util.SELL_KEY: bids[max_bid], util.SPREAD_KEY: spread,
                    util.MIN_ASK_KEY: min_ask, util.MAX_BID_KEY: max_bid}

        return {util.MSG_KEY: f'spread {spread:.5f} is less than fees {fee:.5f}', util.SPREAD_KEY: spread}

    except HTTPError as e:
        print(f'HTTP_ERROR: {e}')
