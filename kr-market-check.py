#!python3
import pprint

import krakenex
from requests.exceptions import HTTPError

kraken = krakenex.API()

try:
    # Get a list of the most recent Trades, Ticker, Assets, and AssetPairs for each Exchange
    recentTrades = kraken.query_public("Trades", {"pair": "XXBTZUSD"})
    dir(recentTrades)
    print(f"Kraken BTC\nLast: {recentTrades.get('result').get('XXBTZUSD')[0][0]}")

    response = kraken.query_public("Depth", {"pair": "XXBTZUSD", "count": "10"})
    print(f"Ask: {response.get('result').get('XXBTZUSD').get('asks')[0][0]}")
    print(f"Bid: {response.get('result').get('XXBTZUSD').get('bids')[0][0]}")

    # https://api.kraken.com/0/public/Assets
    assets = kraken.query_public("Assets")
    pprint.pprint(assets.get("result").keys())

    asset_pairs = kraken.query_public("AssetPairs")
    pprint.pprint(asset_pairs.get("result").keys())


except HTTPError as e:
    print(str(e))
