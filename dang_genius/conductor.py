import os
import sqlite3
import time
from threading import Thread
from datetime import datetime

from dotenv import load_dotenv
import dang_genius.util as dgu
from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseadvancedexchange import CoinbaseAdvancedExchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange


class Conductor:
    def __init__(self):
        self.env_loaded = load_dotenv()
        self.fee_estimate = float(os.environ.get('FEE-ESTIMATE'))
        self.btc_amount = float(os.environ.get('BTC-SWAP-AMT'))
        self.usd_amount = float(os.environ.get('USD-SWAP-AMT'))
        connection = sqlite3.connect(dgu.DB_NAME)
        cursor = connection.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS ask 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, pair TEXT, timestamp TEXT, pennies INTEGER)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS bid
            (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, pair TEXT, timestamp TEXT, pennies INTEGER)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS trade
            (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, pair TEXT, timestamp TEXT, pennies INTEGER)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS wallet
            (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, symbol TEXT, timestamp TEXT, available FLOAT)""")

        connection.commit()
        cursor.close()

        self.exchanges = {
            str(BitstampExchange):
                BitstampExchange(os.environ.get('BS-API-KEY'), os.environ.get('BS-API-SECRET'),
                                 os.environ.get('BS-CLIENT-ID')),
            str(CoinbaseAdvancedExchange):
                CoinbaseAdvancedExchange(os.environ.get('CBA-API-KEY'), os.environ.get('CBA-API-SECRET')),
            str(GeminiExchange):
                GeminiExchange(os.environ.get('GE-API-KEY'), os.environ.get('GE-API-SECRET')),
            str(KrakenExchange):
                KrakenExchange(os.environ.get('KR-API-KEY'), os.environ.get('KR-API-SECRET'))}

        self.follow_market()
        self.follow_wallet()

    def buy_btc_sell_btc(self, exchange_to_buy_btc: str, exchange_to_sell_btc: str,
                         min_ask: float, max_bid: float) -> None:
        be = self.exchanges.get(exchange_to_buy_btc)
        be.set_limits(min_ask, max_bid)
        Thread(target=be.buy_btc).start()

        se = self.exchanges.get(exchange_to_sell_btc)
        se.set_limits(min_ask, max_bid)
        Thread(target=se.sell_btc).start()

    def buy_the_dip(self, pair: str):
#        gemini_ex = self.exchanges.get(str(GeminiExchange))
#        Thread(target=gemini_ex.buy_btc_dip).start()
#        coinbase_ex = self.exchanges.get(str(CoinbaseAdvancedExchange))
#        Thread(target=coinbase_ex.buy_btc_dip).start()
        # look at market by polling the database
    # buy wherever I have cash to spend and the price is right
        # double down, again at any exchange that is available+funded
        # create a database entry for the next purchase
        # poll db

    def follow_wallet(self):
        Thread(target=self.follow_wallet_thread).start()

    def follow_wallet_thread(self):
        while True:
            for ex in self.exchanges.values():
                exchange: str = dgu.alphanumeric(str(type(ex)))
                try:
                    balances: dict = ex.balances()
                    now = datetime.now(tz=dgu.TZ_UTC)
                    timestamp = now.strftime(dgu.DATETIME_FORMAT)
                    connection = sqlite3.connect(dgu.DB_NAME)
                    cursor = connection.cursor()
                    delete_query = f"DELETE FROM wallet WHERE exchange='{exchange}'"
                    cursor.execute(delete_query)

                    insert_query = """INSERT INTO wallet
                                      (exchange, symbol, timestamp, available) 
                                      VALUES (?, ?, ?, ?);"""
                    records = [(exchange, 'BTC', timestamp, float(balances.get('BTC'))),
                               (exchange, 'USD', timestamp, float(balances.get('USD')))]
#TODO: Add ETH
                    cursor.executemany(insert_query, records)
                    connection.commit()
                    cursor.close()
                except KeyError as key_error:
                    print(f'Failed to get balances from {ex}\n{key_error}')
                except sqlite3.Error as sql_error:
                    print(f'CW SQL error: {sql_error}')
                except Exception as ex:
                    print(f'CW Exception: {ex}')
                finally:
                    if connection:
                        connection.close()

            time.sleep(10)


    def follow_market(self):
        Thread(target=self.follow_market_thread).start()


    def follow_market_thread(self):
        while True:
            for ex in self.exchanges.values():
                exchange: str = dgu.alphanumeric(str(type(ex)))
                try:
                    ticker: dict = ex.tickers
                    now = datetime.now(tz=dgu.TZ_UTC)
                    timestamp = now.strftime(dgu.DATETIME_FORMAT)
                    ask = ticker.get(dgu.ASK_KEY)
                    bid = ticker.get(dgu.BID_KEY)
                    connection = sqlite3.connect(dgu.DB_NAME)
                    cursor = connection.cursor()
                    if not ask or not bid:
                        raise Exception('Did not get values from ticker')

                    cursor.execute(f"DELETE FROM ask WHERE exchange='{exchange}'")
                    cursor.execute("""INSERT INTO ask
                                      (exchange, pair, timestamp, pennies) 
                                      VALUES (?, ?, ?, ?);""", (exchange, dgu.BTC_USD_PAIR,
                                                                timestamp, int(ask * 100)))
                    cursor.execute(f"DELETE FROM bid WHERE exchange='{exchange}'")
                    cursor.execute("""INSERT INTO bid
                                      (exchange, pair, timestamp, pennies) 
                                      VALUES (?, ?, ?, ?);""", (exchange, dgu.BTC_USD_PAIR,
                                                                timestamp, int(bid * 100)))


#TODO: ETH
#TODO: last trade?
                    connection.commit()
                    cursor.close()
                except TimeoutError as timeout_error:
                    print(f'FM Timeout error: {timeout_error} {exchange}')
                except ValueError as value_error:
                    print(f'FM Value error: {value_error} {exchange}')
                except ConnectionError as connection_error:
                    print(f'FM Connection error: {connection_error} {exchange}')
                except sqlite3.Error as sqlite3_error:
                    print(f'FM SQLite3 error: {sqlite3_error} {exchange}')
                except Exception as e:
                    print(f'FM Exception: {e} {exchange}')
                finally:
                    if connection:
                        connection.close()

    # each transaction we must know the total dollars spent

    # work in pennies to avoid floats
    def take_the_win(self):
# poll the database lookint at BIDS
# get the current bids for each exchange
# when bids go up by 1% at any exchange, SELL IT ALL
        try:
            connection = sqlite3.connect(dgu.DB_NAME)
            cursor = connection.cursor()
            sqlite_select_bid_query = """SELECT id, exchange, pair, side, MAX(timestamp), pennies FROM bid 
                                        WHERE pair=? GROUP BY exchange, pair, side ORDER BY id DESC LIMIT 10"""
            # NOTE: we should get 3 records, 3 exchanges, 1 pair
            # TODO: make sure the records are recent.

            cursor.execute(sqlite_select_bid_query, dgu.BTC_USD_PAIR)
            records = cursor.fetchall()
            if len(records) != 3:
                print(f'UNKNOWN ERROR: {records}')
            print(records)
            exit()

            for r in records:
                exchange = r[1]
                ex = self.exchanges.get(exchange)
                strike_price_in_pennies = int(r[5]) + int(int(r[5]) / 200)
                ex.strike_price_in_pennies = strike_price_in_pennies

            return None
        except sqlite3.Error as sql_error:
            print(f'WIN SQL error: {sql_error}')
        except TypeError as type_error:
            print(f'WIN Type error: {type_error}')
        except Exception as e:
            print(f'WIN Exception: {e}')
        finally:
            if connection:
                connection.close()

#    def buy_btc_dip(self):
    # poll the database
    # only need to look at asks
    # provide liquitidy in dollars

    # buy_the_dip
    # dip is the amount lower than recent high
    # set sell price to be recent high + premium
    # when dip reaches threshold, buy
    # buy double each time it dips again
    # if it returns to the preset sell price, sell almost all of it,
    # sell enough to return all cash spent, keep remaining coin

    # read the market
    # identify when a dip has occurred
    # buy at the market rate
#    top_bid = 0.0
#    top_ask = 0.0

#    while True:
#        try:
#            ticker = self.get_ticker(self.BTC_USD_PAIR)
#            ask: float = float(ticker.get(util.ASK_KEY))
#            if ask > top_ask:
#                top_ask = ask
#            bid: float = float(ticker.get(util.BID_KEY))

#            if len(self.STRIKES) > 0:
#                lowest_strike = np.min(self.STRIKES)
#                if lowest_strike and bid > lowest_strike:
#                    self.set_limits(bid, bid)
#                    sell_tx = self.trade(pair, self.SELL_SIDE)
#                    if sell_tx:
#                        print(f'SOLD! {sell_tx}')
#                        self.STRIKES.remove(lowest_strike)
#            if bid > top_bid:
#                top_bid = bid
#            if (ask + bid) * (1 + self.DIP) < (top_ask + top_bid) and len(self.STRIKES) < self.MAX_STRIKES:
#                print(f"DIP {ask:8.2f} {bid:8.2f} TOP: {top_ask:8.2f} {top_bid:8.2f}")
#                self.set_limits(ask, ask)
#                tx = self.trade(pair, self.BUY_SIDE)
#                if tx:
#                    strike = float(tx.get("price")) + self.COVER
#                    print(f'CB COVER PRICE: {strike}')
#                    self.STRIKES.append(strike)
#                    top_ask = 0.0
#                    top_bid = 0.0
#                    time.sleep(10)
#        except requests.exceptions.ReadTimeout as read_error:
#            print(f'CB Read error: {read_error}')
#        except ConnectionError as connection_error:
#            print(f'CB ERROR: {connection_error}')
#            time.sleep(1.0)
#        time.sleep(0.5)


# TAKE THE WIN
# SELL THE CLIMB
# follow the bids
# when bids rise by 1%, sell a bit NO SELL ALL OF IT!!!
# double down on each climb (nope, already took the win)
# (buy back at low point using other mechanism)
