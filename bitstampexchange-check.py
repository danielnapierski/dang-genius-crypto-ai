#!python3
import os
import pprint

from dotenv import load_dotenv

from dang_genius.bitstampexchange import BitstampExchange

load_dotenv()

be = BitstampExchange(
    os.environ.get("BS-API-KEY"),
    os.environ.get("BS-API-SECRET"),
    os.environ.get("BS-CLIENT-ID"),
)

print("\nBitstampExchange")
pprint.pprint(be.balances)
pprint.pprint(be.tickers)
