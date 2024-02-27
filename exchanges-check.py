import os
import pprint
import time

from dotenv import load_dotenv

from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseexchange import CoinbaseExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange

print('Loading...')

load_dotenv()
be = BitstampExchange(os.environ.get('BS-API-KEY'), os.environ.get('BS-API-SECRET'), os.environ.get('BS-CLIENT-ID'))
ce = CoinbaseExchange(os.environ.get('CB-API-KEY'), os.environ.get('CB-API-SECRET'))
ge = GeminiExchange(os.environ.get('GE-API-KEY'), os.environ.get('GE-API-SECRET'))
ke = KrakenExchange(os.environ.get('KR-API-KEY'), os.environ.get('KR-API-SECRET'))

for ex in [be, ce, ge, ke]:
    ex.balances
    ex.tickers

print('\nBitstamp')
start = time.time()
beb = be.balances
end = time.time()
print(f'[{(end - start): .2f} seconds]')
start = time.time()
bet = be.tickers
end = time.time()
pprint.pprint(beb)
pprint.pprint(bet)
print(f'[{(end - start): .2f} seconds]')

print('\nCoinbase')
start = time.time()
ceb = ce.balances
end = time.time()
print(f'[{(end - start): .2f} seconds]')
start = time.time()
cet = ce.tickers
end = time.time()
pprint.pprint(ceb)
pprint.pprint(cet)
print(f'[{(end - start): .2f} seconds]')

print('\nGemini')
start = time.time()
geb = ge.balances
end = time.time()
print(f'[{(end - start): .2f} seconds]')
start = time.time()
get = ge.tickers
end = time.time()
pprint.pprint(get)
pprint.pprint(geb)
print(f'[{(end - start): .2f} seconds]')

print('\nKraken')
start = time.time()
keb = ke.balances
end = time.time()
print(f'[{(end - start): .2f} seconds]')
start = time.time()
ket = ke.tickers
end = time.time()
pprint.pprint(keb)
pprint.pprint(ket)
print(f'[{(end - start): .2f} seconds]')

btc_tally = sum([beb['BTC'], ceb['BTC'], geb['BTC'], keb['BTC']])
eth_tally = sum([beb['ETH'], ceb['ETH'], geb['ETH'], keb['ETH']])
usd_tally = sum([beb['USD'], ceb['USD'], geb['USD'], keb['USD']])
min_btc_bid = min([bet['BTC_USD']['BID'], cet['BTC_USD']['BID'], get['BTC_USD']['BID'], ket['BTC_USD']['BID']])
min_eth_bid = min([bet['ETH_USD']['BID'], cet['ETH_USD']['BID'], get['ETH_USD']['BID'], ket['ETH_USD']['BID']])
total = (min_btc_bid * btc_tally) + (min_eth_bid * eth_tally) + usd_tally
print(f'\nTotal BTC: {btc_tally: .5f}\tTotal ETH: {eth_tally: .5f}\tTotal USD: {usd_tally: .2f}')
print(f'\t\t\t\tEstimated Portfolio Value: ${total: .2f}')
