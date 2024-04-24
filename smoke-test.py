#!python3
import http.client
import json
import pprint

import bitstamp.client
import coinbasepro as cbp
import krakenex
from gemini_api.endpoints.public import Public
from requests.exceptions import HTTPError


try:
    # Get a list of the most recent BTC Trades, then Assets, and AssetPairs for each exchange

    print("\nKraken BTC")
    # https://api.kraken.com/0/public/
    kraken = krakenex.API()
    ticker = kraken.query_public("Depth", {"pair": "XXBTZUSD", "count": "10"})
    print(f"Ask: {ticker.get('result').get('XXBTZUSD').get('asks')[0][0]}")
    print(f"Bid: {ticker.get('result').get('XXBTZUSD').get('bids')[0][0]}")
    kr_recentTrades = kraken.query_public("Trades", {"pair": "XXBTZUSD"})
    print(f"Last: {kr_recentTrades.get('result').get('XXBTZUSD')[0][0]}")
    kr_assets = kraken.query_public("Assets")
    #    pprint.pprint(kr_assets.get('result').keys())
    kr_asset_pairs = kraken.query_public("AssetPairs")
    #    pprint.pprint(kr_asset_pairs.get('result').keys())

    print("\nBitStamp BTC")
    bitstamp = bitstamp.client.Public()
    tics = bitstamp.ticker(False, False)
    bs_pairs = []
    for i in tics:
        p = str(i["pair"])
        if p == "BTC/USD":
            btc_ask = float(i["ask"])
            btc_bid = float(i["bid"])
            btc_last = float(i["last"])
            print(f"Ask: {btc_ask:.2f}\nBid: {btc_bid:.2f}\nLast: {btc_last:.2f}")
        if p.startswith("RNDR"):
            print(f"{i}")
        bs_pairs.append(p)
    #    print(bs_pairs)

    print("\nGemini BTC")
    gemini = Public()
    ge_btc = gemini.get_ticker("btcusd")
    pprint.pprint(ge_btc)

    print("\nCoinbase BTC")
    coinbase = cbp.PublicClient()
    pprint.pprint(coinbase.get_product_order_book("BTC-USD"))
    conn = http.client.HTTPSConnection("api.exchange.coinbase.com")
    payload = ""
    headers = {"Content-Type": "application/json"}
    conn.request("GET", "/products", payload, headers)
    data = conn.getresponse().read().decode("utf-8")
    obj = json.loads(data)
    ids = []
    for d in obj:
        if hasattr(d, "get"):
            ids.append(d.get("id"))
            continue
        print(f"Coinbase: {d}")
#    print(ids)

except HTTPError as e:
    print(str(e))
