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

for ex in [be]:
    try:
        print(f'\nExchange: {dgu.alphanumeric(str(type(ex)))}')
        t = ex.trade(dgu.ETH_USD_PAIR, 'BUY', 0.004, 3400.9)
        print('Trade-check trade: ')
        pprint.pprint(t)
    except Exception as e:
        print('Trade-check exception: ')
        pprint.pprint(e)

