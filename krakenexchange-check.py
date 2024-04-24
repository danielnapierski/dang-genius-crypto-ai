#!python3
import os
import pprint

import krakenex
from dotenv import load_dotenv

import dang_genius.krakenexchange

load_dotenv()

KR_API_KEY = os.environ.get("KR-API-KEY")
KR_API_SECRET = os.environ.get("KR-API-SECRET")

k = krakenex.API(KR_API_KEY, KR_API_SECRET)

print('Kraken balances:')
b = k.query_private("Balance")["result"]
pprint.pprint(b)

print('Kraken ticker:')
ke = dang_genius.krakenexchange.KrakenExchange(KR_API_KEY, KR_API_SECRET)
pprint.pprint(ke.tickers)
