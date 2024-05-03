#!python3
import os
import pprint

from dotenv import load_dotenv

import dang_genius.util as dgu
from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseadvancedexchange import CoinbaseAdvancedExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange

print("Loading...")

load_dotenv()
be = BitstampExchange(
    os.environ.get("BS-API-KEY"),
    os.environ.get("BS-API-SECRET"),
    os.environ.get("BS-CLIENT-ID"),
)
cbe = CoinbaseAdvancedExchange(
    os.environ.get("CBA-API-KEY"), os.environ.get("CBA-API-SECRET")
)
ge = GeminiExchange(os.environ.get("GE-API-KEY"), os.environ.get("GE-API-SECRET"))
ke = KrakenExchange(os.environ.get("KR-API-KEY"), os.environ.get("KR-API-SECRET"))

for ex in [be]:
    try:
        print(f"\nExchange: {dgu.alphanumeric(str(type(ex)))}")
        #        t = ex.trade(dgu.FET_USD_PAIR, 'BUY', 10, 2.64)
        #        t = ex.trade(dgu.GALA_USD_PAIR, 'BUY', 300, 0.072)
        #        t = ex.trade(dgu.RNDR_USD_PAIR, 'BUY', 5, 11.21)

        t = ex.trade(dgu.BTC_USD_PAIR, "BUY", 0.0005, 65000.00)
        #t = ex.trade(dgu.ETH_USD_PAIR, 'BUY', 0.01, 3109.9)
        print("Trading: ")
        pprint.pprint(t)
    #        pprint.pprint(t2)
    except Exception as e:
        print("Trading exception: ")
        pprint.pprint(e)

# Examples:
#        t = ex.trade(dgu.BONK_USD_PAIR, 'BUY', 100000, 0.0000368)
#        t = ex.trade(dgu.SAMO_USD_PAIR, 'BUY', 1200, 0.025)
#        t = ex.trade(dgu.FTM_USD_PAIR, 'BUY', 60, 0.65)
#        t = ex.trade(dgu.SHIB_USD_PAIR, 'BUY', 1200000, 0.0000384)
#        t = ex.trade(dgu.LINK_USD_PAIR, 'BUY', 0.7, 20.25)
#        t = ex.trade(dgu.FET_USD_PAIR, 'BUY', 5.0, 2.15)
