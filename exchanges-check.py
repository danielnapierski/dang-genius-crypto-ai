import math
import os
import pprint
from dotenv import load_dotenv
from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseexchange import CoinbaseExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange
from operator import attrgetter

load_dotenv()
be = BitstampExchange(os.environ.get('BS-API-KEY'), os.environ.get('BS-API-SECRET'), os.environ.get('BS-CLIENT-ID'))
print('Bitstamp')
beb = be.balances
pprint.pprint(beb)
bet = be.tickers
pprint.pprint(bet)

print('Coinbase')
ce = CoinbaseExchange(os.environ.get('CB-API-KEY'), os.environ.get('CB-API-SECRET'))
ceb = ce.balances
pprint.pprint(ceb)
cet = ce.tickers
pprint.pprint(cet)

print('Gemini')
ge = GeminiExchange(os.environ.get('GE-API-KEY'), os.environ.get('GE-API-SECRET'))
geb = ge.balances
pprint.pprint(geb)
get = ge.tickers
pprint.pprint(get)

print('Kraken')
ke = KrakenExchange(os.environ.get('KR-API-KEY'), os.environ.get('KR-API-SECRET'))
keb = ke.balances
pprint.pprint(keb)
ket = ke.tickers
pprint.pprint(ket)

btcs = [beb['BTC'], ceb['BTC'], geb['BTC'], keb['BTC']]
btc_tally = sum(btcs)
print(f'Total BTC: {btc_tally: .5f}')

eths = [beb['ETH'], ceb['ETH'], geb['ETH'], keb['ETH']]
eth_tally = sum(eths)
print(f'Total ETH: {eth_tally: .5f}')

usds = [beb['USD'], ceb['USD'], geb['USD'], keb['USD']]
usd_tally = sum(usds)
print(f'Total USD: {usd_tally: .2f}')


min_btc_bid = min([bet['BTC_USD']['BID'], cet['BTC_USD']['BID'], get['BTC_USD']['BID'], ket['BTC_USD']['BID']])
min_eth_bid = min([bet['ETH_USD']['BID'], cet['ETH_USD']['BID'], get['ETH_USD']['BID'], ket['ETH_USD']['BID']])
total = (min_btc_bid * btc_tally) + (min_eth_bid * eth_tally) + usd_tally
print(f'Estimated Portfolio Value: ${total: .2f}')
