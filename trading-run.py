import os
import pprint
import time

from dotenv import load_dotenv

import dang_genius.util as dgu
from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseadvancedexchange import CoinbaseAdvancedExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange

print('Loading...')

load_dotenv()
be = BitstampExchange(os.environ.get('BS-API-KEY'), os.environ.get('BS-API-SECRET'), os.environ.get('BS-CLIENT-ID'))
cbe = CoinbaseAdvancedExchange(os.environ.get('CBA-API-KEY'), os.environ.get('CBA-API-SECRET'))
ge = GeminiExchange(os.environ.get('GE-API-KEY'), os.environ.get('GE-API-SECRET'))
ke = KrakenExchange(os.environ.get('KR-API-KEY'), os.environ.get('KR-API-SECRET'))

for ex in [ke]:
    try:
        print(f'\nExchange: {dgu.alphanumeric(str(type(ex)))}')
        t = ex.trade(dgu.BTC_USD_PAIR, 'BUY', 0.001, 72088.9)
#        t2 = ex.trade(dgu.ETH_USD_PAIR, 'SELL', 0.02, 4038.0)
        print('Trade-check trade: ')
        pprint.pprint(t)
#        pprint.pprint(t2)
    except Exception as e:
        print('Trade-check exception: ')
        pprint.pprint(e)

# Examples:
#        t = ex.trade(dgu.BONK_USD_PAIR, 'BUY', 100000, 0.0000368)
#        t = ex.trade(dgu.SAMO_USD_PAIR, 'BUY', 1200, 0.025)
#        t = ex.trade(dgu.FTM_USD_PAIR, 'BUY', 60, 0.65)
#        t = ex.trade(dgu.SHIB_USD_PAIR, 'BUY', 1200000, 0.0000384)
#        t = ex.trade(dgu.LINK_USD_PAIR, 'BUY', 0.7, 20.25)
#        t = ex.trade(dgu.FET_USD_PAIR, 'BUY', 5.0, 2.15)
