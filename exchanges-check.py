import os
import pprint
import time

from dotenv import load_dotenv

from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseadvancedexchange import CoinbaseAdvancedExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange

print('Loading exchanges ...')

load_dotenv()
be = BitstampExchange(os.environ.get('BS-API-KEY'), os.environ.get('BS-API-SECRET'), os.environ.get('BS-CLIENT-ID'))
cae = CoinbaseAdvancedExchange(os.environ.get('CBA-API-KEY'), os.environ.get('CBA-API-SECRET'))
ge = GeminiExchange(os.environ.get('GE-API-KEY'), os.environ.get('GE-API-SECRET'))
ke = KrakenExchange(os.environ.get('KR-API-KEY'), os.environ.get('KR-API-SECRET'))

for ex in [be, cae, ge, ke]:
    ex.balances
    ex.tickers

btcs = []
eths = []
usds = []
shibs = []
btc_bids = []
eth_bids = []
shib_bids = []

for ex in [be, cae, ge, ke]:
    print(f'{type(ex)}')
    start = time.time()
    exb = ex.balances
    end = time.time()
    print(f'[{(end - start): .2f} seconds]')
    start = time.time()
    ext = ex.tickers
    end = time.time()
    print(exb)
    print(ext)
    print(f'[{(end - start): .2f} seconds]')
    btcs.append(exb['BTC'])
    eths.append(exb['ETH'])
    usds.append(exb['USD'])
    shibs.append(exb['SHIB'])
    btc_bids.append(ext['BTC_USD']['BID'])
    eth_bids.append(ext['ETH_USD']['BID'])
    shib_bids.append(ext['SHIB_USD']['BID'])

btc_tally = sum(btcs)
eth_tally = sum(eths)
usd_tally = sum(usds)
shib_tally = sum(shibs)
min_btc_bid = min(btc_bids)
min_eth_bid = min(eth_bids)
min_shib_bid = min(shib_bids)
total = (min_btc_bid * btc_tally) + (min_eth_bid * eth_tally) + (min_shib_bid * shib_tally) + usd_tally
print(f'\nBTC: {btc_tally: .5f}\tETH: {eth_tally: .5f}\tSHIB: {shib_tally: .0f}\t   USD: {usd_tally: .2f}')
print(f'\t\t\t\tEstimated Portfolio Value: ${total: .2f}')
