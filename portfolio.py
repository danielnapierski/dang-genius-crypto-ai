#!python3
import os
import threading
import time
from datetime import datetime

from dotenv import load_dotenv

from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseadvancedexchange import CoinbaseAdvancedExchange
from dang_genius.exchange import Exchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange

print("Loading exchanges ...")

load_dotenv()
be = BitstampExchange(
    os.environ.get("BS-API-KEY"),
    os.environ.get("BS-API-SECRET"),
    os.environ.get("BS-CLIENT-ID"),
)
cae = CoinbaseAdvancedExchange(os.environ.get("CBA-API-KEY"), os.environ.get("CBA-API-SECRET"))
ge = GeminiExchange(os.environ.get("GE-API-KEY"), os.environ.get("GE-API-SECRET"))
ke = KrakenExchange(os.environ.get("KR-API-KEY"), os.environ.get("KR-API-SECRET"))

balances = {}
tickers = {}
tallies = {}
bids = {}
completed = {}
lock = threading.Lock()


def record_balances(ex: Exchange) -> None:
    start = time.time()
    with lock:
        balances[ex] = ex.balances
        for currency in balances[ex].keys():
            tallies[currency] = (
                tallies[currency] + balances[ex][currency]
                if currency in tallies.keys()
                else balances[ex][currency]
            )
    with lock:
        tickers[ex] = ex.tickers
    end = time.time()

    with lock:
        for pair in tickers[ex]:
            tic = tickers[ex]
            bids[pair] = (
                min(bids[pair], tic[pair]["BID"])
                if pair in tickers.keys()
                else tic[pair]["BID"]
            )

    with lock:
        print(f"{type(ex)}")
        print(balances[ex])
        print(f"[{(end - start): .2f} seconds]")

    with lock:
        completed[ex] = ex


for ex in [be, cae, ge, ke]:
    threading.Thread(target=record_balances, args=(ex,)).start()

while len(completed.keys()) != 4:
    time.sleep(0.1)

tally_keys = sorted(tallies)
print(f"TALLIES: {tallies}")
print(f'BIDS: {bids}')
bids["USD_USD"] = 1.0
estimates = {}
for t in tally_keys:
    pair_usd = f"{t}_USD"
    estimates[t] = float(f"{float(bids[pair_usd]) * float(tallies[t]): .2f}")
# print(f'ESTIMATED VALUES: {estimates}')
print('')
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(f"\t\t\t\tEstimated Portfolio Value: ${sum(estimates.values()): .2f}")
