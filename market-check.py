import coinbasepro as cbp
import krakenex
import numpy as np
from gemini_api.endpoints.public import Public
from requests.exceptions import HTTPError

kraken = krakenex.API()
kraken_pair: str = "XXBTZUSD"
coinbase = cbp.PublicClient()
cb_pair: str = "BTC-USD"
gemini = Public()
ge_pair: str = "BTCUSD"
FEE_ESTIMATE: float = 0.00000005
asks: dict = {}
bids: dict = {}


def market_check() -> object:
    try:
        kraken_recent_trades = kraken.query_public("Trades", {"pair": kraken_pair})
        kraken_last_trade = float(
            kraken_recent_trades.get("result").get(kraken_pair)[0][0]
        )
        kraken_public_result = (
            kraken.query_public("Depth", {"pair": kraken_pair, "count": "10"})
            .get("result")
            .get(kraken_pair)
        )
        kraken_ask: float = float(kraken_public_result.get("asks")[0][0])
        asks[kraken_ask] = "kraken"
        kraken_bid: float = float(kraken_public_result.get("bids")[0][0])
        bids[kraken_bid] = "kraken"
        print(
            f"Kr BTC\tLast: {kraken_last_trade:.5f}\tAsk: {kraken_ask:.5f}\tBid: {kraken_bid:.5f}"
        )

        coinbase_last = float("-1000.0")
        coinbase_order_book = coinbase.get_product_order_book(cb_pair)
        coinbase_ask: float = float(coinbase_order_book.get("asks")[0][0])
        asks[coinbase_ask] = "coinbase"
        coinbase_bid: float = float(coinbase_order_book.get("bids")[0][0])
        bids[coinbase_bid] = "coinbase"

        print(
            f"Cb BTC\tLast: {coinbase_last:.5f}\tAsk: {coinbase_ask:.5f}\tBid: {coinbase_bid:.5f}"
        )

        gemini_ticker = gemini.get_ticker(ge_pair)
        gemini_last = float(gemini_ticker.get("last"))
        gemini_ask: float = float(gemini_ticker.get("ask"))
        asks[gemini_ask] = "gemini"
        gemini_bid: float = float(gemini_ticker.get("bid"))
        bids[gemini_bid] = "gemini"
        print(
            f"Ge BTC\tLast: {gemini_last:.5f}\tAsk: {gemini_ask:.5f}\tBid: {gemini_bid:.5f}"
        )

        max_bid = np.max([kraken_bid, coinbase_bid, gemini_bid])
        min_ask = np.min([kraken_ask, coinbase_ask, gemini_ask])
        spread = max_bid - min_ask
        opportunity = spread > (min_ask * FEE_ESTIMATE)
        print()
        print(
            f"max_bid: {max_bid:.5f}\tmin_ask: {min_ask:.5f}\tOpp? {opportunity}\tSpread: {spread:.5f}"
        )

        if opportunity:
            buy_ex = asks[min_ask]
            sell_ex = bids[max_bid]
            print(f"BUY BTC at {buy_ex}\nSELL BTC at {sell_ex}")
        else:
            print(f"spread is less than estimated fees {(FEE_ESTIMATE * min_ask):.5f}")

    except HTTPError as e:
        print(f"HTTP_ERROR: {e}")


market_check()
