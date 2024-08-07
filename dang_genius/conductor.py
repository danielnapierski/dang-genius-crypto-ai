import os
import pprint
import random
import sqlite3
import sys
import threading
import time
from sqlite3 import OperationalError
from threading import Thread
from datetime import datetime, timedelta

import numpy as np
from dotenv import load_dotenv

import dang_genius.util as dgu
from dang_genius.bitstampexchange import BitstampExchange
from dang_genius.coinbaseadvancedexchange import CoinbaseAdvancedExchange
from dang_genius.exchange import Exchange
from dang_genius.geminiexchange import GeminiExchange
from dang_genius.krakenexchange import KrakenExchange


class Conductor:
    def __init__(self):
        self.env_loaded = load_dotenv()
        self.fee_estimate = float(os.environ.get("FEE-ESTIMATE"))
        self.btc_amount = float(os.environ.get("BTC-SWAP-AMT"))
        self.usd_amount = float(os.environ.get("USD-SWAP-AMT"))
        self.buy_pennies = int(os.environ.get("BUY-PENNIES"))
        self._next_buy_time = datetime.now(tz=dgu.TZ_UTC) + timedelta(seconds=180)
        with threading.Lock():
            with sqlite3.connect(dgu.DB_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("""PRAGMA lock_timeout = 500;""")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS ask 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, pair TEXT, timestamp TEXT, pennies INTEGER)"""
                )
                cursor.execute("""DELETE FROM ask""")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS bid
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, pair TEXT, timestamp TEXT, pennies INTEGER)"""
                )
                cursor.execute("""DELETE FROM bid""")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS trade
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, pair TEXT, timestamp TEXT, pennies INTEGER)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS wallet
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, exchange TEXT, symbol TEXT, timestamp TEXT, available FLOAT)"""
                )
                cursor.execute("""DELETE FROM wallet""")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS price_history
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, minute_stamp TEXT, pennies INTEGER, delta INTEGER)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS intent
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, exchange TEXT, order_desc TEXT, 
                    date_expires TEXT, amount FLOAT, limit_pennies INTEGER, 
                    completed BIT, failed BIT, in_progress BIT, check_price BIT, keep BIT)"""
                )
                cursor.execute("""UPDATE intent SET in_progress=1""")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS win
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, order_locator TEXT, amount FLOAT, limit_pennies INTEGER, 
                    completed BIT, in_progress BIT)"""
                )
                connection.commit()
                cursor.close()

        self.exchanges = {
            dgu.alphanumeric(str(BitstampExchange)): BitstampExchange(
                os.environ.get("BS-API-KEY"),
                os.environ.get("BS-API-SECRET"),
                os.environ.get("BS-CLIENT-ID"),
            ),
            dgu.alphanumeric(str(CoinbaseAdvancedExchange)): CoinbaseAdvancedExchange(
                os.environ.get("CBA-API-KEY"), os.environ.get("CBA-API-SECRET")
            ),
            dgu.alphanumeric(str(GeminiExchange)): GeminiExchange(
                os.environ.get("GE-API-KEY"), os.environ.get("GE-API-SECRET")
            ),
            dgu.alphanumeric(str(KrakenExchange)): KrakenExchange(
                os.environ.get("KR-API-KEY"), os.environ.get("KR-API-SECRET")
            ),
        }

        self.follow_market()
        self.follow_wallet()
        time.sleep(15)
        #        self.find_opportunities()
        self.grind()

    #        self.execute_trades()

    def buy_btc_sell_btc(
        self,
        exchange_to_buy_btc: str,
        exchange_to_sell_btc: str,
        min_ask: float,
        max_bid: float,
    ) -> None:
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
        return

    def follow_wallet(self):
        Thread(target=self.follow_wallet_thread).start()

    def follow_wallet_thread(self):
        while True:
            keys = list(self.exchanges.keys())
            random.shuffle(keys)

            for k in keys:
                time.sleep(20)
                ex = self.exchanges[k]
                exchange: str = dgu.alphanumeric(str(type(ex)))
                try:
                    balances: dict = ex.balances
                    now = datetime.now(tz=dgu.TZ_UTC)
                    timestamp = now.strftime(dgu.DATETIME_FORMAT)
                    with threading.Lock():
                        for _ in range(10):
                            with sqlite3.connect(dgu.DB_NAME) as connection:
                                cursor = connection.cursor()
                                try:
                                    self.record_wallet_balances(
                                        balances, connection, cursor, exchange, timestamp
                                    )
                                    break
                                except OperationalError:
                                    pass
                except KeyError as key_error:
                    print(f"FW Failed to get balances from {ex}\n{key_error}")
                except TimeoutError as timeout_error:
                    print(f"FW Timeout error: {timeout_error} {exchange}")
                except ValueError as value_error:
                    print(f"FW Value error: {value_error} {exchange}")
                except ConnectionError as connection_error:
                    print(
                        f"Follow Wallet Connection error: {connection_error} {exchange}"
                    )
                except sqlite3.Error as sql_error:
                    print(f"Follow Wallet SQL error: {sql_error} {exchange}")
                except Exception as e:
                    print(f"FW Exception: {e} {exchange}")
                finally:
                    time.sleep(10)

    def record_wallet_balances(self, balances, connection, cursor, exchange, timestamp):
        delete_query = f"DELETE FROM wallet WHERE exchange='{exchange}'"
        cursor.execute(delete_query)
        insert_query = """INSERT INTO wallet
                                              (exchange, symbol, timestamp, available) 
                                              VALUES (?, ?, ?, ?);"""
        records = []
        for b in balances:
            val = float(balances.get(b))
            if val > 0.0:
                records.append((exchange, str(b).upper(), timestamp, val))
        cursor.executemany(insert_query, records)
        connection.commit()
        cursor.close()
        print(f"Wallet updated {exchange}")

    def follow_market(self):
        Thread(target=self.follow_market_thread).start()

    def follow_market_thread(self):
        prior_exchange = ""
        prior_pennies = 0
        while True:
            with threading.Lock():
                with sqlite3.connect(dgu.DB_NAME) as connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        f"""SELECT DISTINCT COALESCE(win.pair, wallet.symbol || '_USD') AS c
    FROM win FULL JOIN wallet ON wallet.symbol = REPLACE(win.pair, '_USD', '')
    WHERE wallet.symbol != 'USD'
    ORDER BY c"""
                    )
                    winning_pairs = cursor.fetchall()
                    keys = list(self.exchanges.keys())
                    random.shuffle(keys)
                    for k in keys:
                        ex = self.exchanges[k]
                        exchange: str = dgu.alphanumeric(str(type(ex)))
                        if prior_exchange == exchange and len(keys) > 1:
                            continue
                        try:
                            tickers: dict = ex.tickers
                            now = datetime.now(tz=dgu.TZ_UTC)
                            timestamp = dgu.time_str(now)
                            minute_stamp = dgu.time_str_to_the_minute(now)
                            for p_row in winning_pairs:
                                pair = p_row[0]
                                if pair not in tickers.keys():
                                    # not all products are available at all exchanges
                                    continue

                                ticker: dict = tickers[pair]
                                ask = ticker.get(dgu.ASK_KEY)
                                bid = ticker.get(dgu.BID_KEY)
                                if not ask or not bid:
                                    raise Exception(
                                        f"Did not get values from ticker {exchange} {pair}"
                                    )

                                cursor.execute(
                                    f"DELETE FROM ask WHERE exchange='{exchange}' AND pair='{pair}'"
                                )
                                cursor.execute(
                                    """INSERT INTO ask (exchange, pair, timestamp, pennies) 
                                    VALUES (?, ?, ?, ?);""",
                                    (exchange, pair, timestamp, int(ask * 100)),
                                )
                                cursor.execute(
                                    f"DELETE FROM bid WHERE exchange='{exchange}' AND pair='{pair}'"
                                )
                                cursor.execute(
                                    """INSERT INTO bid (exchange, pair, timestamp, pennies) 
                                    VALUES (?, ?, ?, ?);""",
                                    (exchange, pair, timestamp, int(bid * 100)),
                                )

                                select_latest_price_query = f"""SELECT id, pair, MAX(minute_stamp), pennies, delta 
                                                                FROM price_history WHERE pair='{pair}' 
                                                                GROUP BY pair ORDER BY id DESC LIMIT 1"""
                                cursor.execute(select_latest_price_query)
                                records = cursor.fetchall()
                                db_has_current = False

                                if len(records) == 1:
                                    r_datetime = records[0][2]
                                    prior_pennies = records[0][3]
                                    db_has_current = minute_stamp == r_datetime

                                if not db_has_current:
                                    pennies = int((bid * 50) + (ask * 50))
                                    cursor.execute(
                                        """INSERT INTO price_history (pair, minute_stamp, pennies, delta) 
                                        VALUES (?, ?, ?, ?);""",
                                        (
                                            pair,
                                            minute_stamp,
                                            pennies,
                                            (pennies - prior_pennies),
                                        ),
                                    )
                                # TODO: make sure the records are recent.
                                # TODO: last trade?
                                connection.commit()
                                prior_exchange = exchange
                        except TimeoutError as timeout_error:
                            print(f"FM Timeout error: {timeout_error} {exchange}")
                        except ValueError as value_error:
                            print(f"FM Value error: {value_error} {exchange}")
                        except ConnectionError as connection_error:
                            print(f"FM Connection error: {connection_error} {exchange}")
                        except sqlite3.Error as sqlite3_error:
                            print(f"FM SQLite3 error: {sqlite3_error} {exchange}")
                        except Exception as e:
                            print(f"FM Exception: {e} {exchange}")

                    try:
                        cursor.close()
                    except Exception as e:
                        print(f"FM cursor exception: {e} {exchange}")

    # TODO: each transaction we must know the total dollars spent
    def find_opportunities(self):
        Thread(target=self.find_opportunities_thread).start()

    def find_opportunities_thread(self):
        while True:
            try:
                asks: dict = {}
                bids: dict = {}
                min_asks: dict = {}
                max_bids: dict = {}
                # TODO:         with sqlite3.connect(dgu.DB_NAME) as connection:
                connection = sqlite3.connect(dgu.DB_NAME)
                cursor = connection.cursor()
                ask_query = """SELECT id, exchange, pair, MAX(timestamp), pennies FROM ask 
                            GROUP BY exchange, pair ORDER BY id DESC LIMIT 20"""
                cursor.execute(ask_query)
                records = cursor.fetchall()

                for r in records:
                    exchange = r[1]
                    pair = r[2]
                    #                    ts = dgu.get_datetime(r[3])
                    #                    now = datetime.now(tz=dgu.TZ_UTC)
                    #                    if ts < (now + timedelta(seconds=5)):
                    #                        print(f'Outdated ask: {ts} {exchange} {pair}')
                    #                        continue

                    x = {} if pair not in asks.keys() else asks[pair]
                    x.setdefault(float(int(r[4]) / 100.0), exchange)
                    asks[pair] = x

                for pair in asks.keys():
                    pair_asks = asks[pair].keys()
                    min_asks[pair] = np.min(list(pair_asks))

                bid_query = """SELECT id, exchange, pair, MAX(timestamp), pennies FROM bid 
                                GROUP BY exchange, pair ORDER BY id DESC LIMIT 5"""
                cursor.execute(bid_query)
                records = cursor.fetchall()

                for r in records:
                    exchange = r[1]
                    pair = r[2]
                    #                    ts = dgu.get_datetime(r[3])
                    #                    now = datetime.now(tz=dgu.TZ_UTC)
                    #                    if ts < (now + timedelta(seconds=5)):
                    #                        print(f'Outdated bid: {ts} {exchange} {pair}')
                    #                        continue

                    x = {} if pair not in bids.keys() else bids[pair]
                    x.setdefault(float(int(r[4]) / 100.0), exchange)
                    bids[pair] = x

                for pair in bids.keys():
                    pair_bids = bids[pair].keys()
                    max_bids[pair] = np.max(list(pair_bids))

                for pair in bids.keys() & asks.keys():
                    max_bid = max_bids[pair]
                    min_ask = min_asks[pair]
                    spread = max_bid - min_ask
                    fee = min_ask * self.fee_estimate
                    sys.stdout.write(
                        f"\r{datetime.now()} min_ask: {min_ask:10.2f}\tmax_bid: {max_bid:10.2f}\t"
                        f"Spread: {spread:6.2f}\tFee: {fee:6.2f}\t"
                    )
                    sys.stdout.flush()

                    if spread > fee:
                        # return {dgu.BUY_KEY: asks[min_ask], dgu.SELL_KEY: bids[max_bid], dgu.SPREAD_KEY: spread,
                        # dgu.MIN_ASK_KEY: min_ask, dgu.MAX_BID_KEY: max_bid}
                        # pair TEXT, side TEXT, exchange TEXT, amount FLOAT,
                        # date_expires TEXT, limit_pennies INTEGER
                        amount = -1.0
                        if pair == dgu.BTC_USD_PAIR:
                            amount = 0.001
                        if pair == dgu.ETH_USD_PAIR or pair == dgu.ETH_BTC_PAIR:
                            amount = 0.01
                        if pair == dgu.SHIB_USD_PAIR:
                            amount = 1000000
                        if amount < 0.0:
                            raise Exception(f"Unsupported pair: {pair}")

                        now = datetime.now(tz=dgu.TZ_UTC)
                        expires = dgu.time_str_to_the_minute(now)
                        sell_exchange = bids[pair][max_bid]
                        buy_exchange = asks[pair][min_ask]
                        weight_max = 70
                        weight_min = 30
                        pennies = int((max_bid * weight_max) + (min_ask * weight_min))
                        sell_limit = int(float(pennies) * 1.000200)
                        buy_limit = int(float(pennies) * 0.999899)

                        cursor.execute(
                            """INSERT INTO intent (pair, side, exchange, amount, date_expires, limit_pennies) 
                        VALUES (?, ?, ?, ?, ?, ?);""",
                            (pair, "SELL", sell_exchange, amount, expires, sell_limit),
                        )
                        cursor.execute(
                            """INSERT INTO intent (pair, side, exchange, amount, date_expires, limit_pennies) 
                        VALUES (?, ?, ?, ?, ?, ?);""",
                            (pair, "BUY", buy_exchange, amount, expires, buy_limit),
                        )

                # if spread > fee:
                # return {dgu.BUY_KEY: asks[min_ask], dgu.SELL_KEY: bids[max_bid], dgu.SPREAD_KEY: spread,
                #                      dgu.MIN_ASK_KEY: min_ask, dgu.MAX_BID_KEY: max_bid}
                # return {dgu.MSG_KEY: f'spread {spread:.5f} is less than fees {fee:.5f}', dgu.SPREAD_KEY: spread}
                connection.commit()
                cursor.close()
                time.sleep(0.3)
            except sqlite3.Error as sql_error:
                print(f"MC SQL error: {sql_error}")
            except TypeError as type_error:
                print(f"MC Type error: {type_error}")
            except Exception as e:
                print(f"MC Exception: {e}")

    #            finally:
    #                if connection:
    #                    connection.close()

    def execute_trades(self):
        Thread(target=self.execute_trades_thread, args=("BUY",)).start()
        Thread(target=self.execute_trades_thread, args=("SELL",)).start()

    def check_funding(
        self, side: str, pair: str, exchange: str, amount: float, limit_pennies: int
    ) -> bool:
        if "BUY" == side.upper():
            try:
                required_pennies = int(limit_pennies * amount)
                symbol = "USD"
                if not pair.upper().endswith("USD"):
                    raise Exception("Not implemented for non USD")

                with threading.Lock():
                    with sqlite3.connect(dgu.DB_NAME) as connection:
                        cursor = connection.cursor()
                        available_query = f"""SELECT available FROM wallet 
                                                WHERE exchange == '{exchange}' AND symbol == '{symbol}' LIMIT 2"""
                        cursor.execute(available_query)
                        records = cursor.fetchall()
                        if len(records) == 1:
                            available_pennies = int(records[0][0] * 100)
                            return available_pennies > required_pennies
                        else:
                            raise Exception(
                                f"Buy DB error.  Multiple|missing wallet records for {symbol} @ {exchange} \n{records}"
                            )
            except sqlite3.Error as sql_error:
                print(f"Buy CheckFunding SQL error: {sql_error}")
            except TypeError as type_error:
                print(f"Buy CheckFunding type error: {type_error}")
            except Exception as e:
                print(f"Buy CheckFunding exception: {e}")
        #            finally:
        #                if connection:
        #                    connection.close()
        else:
            if "SELL" == side.upper():
                try:
                    symbol = pair.split("_")[0]
                    with threading.Lock():
                        with sqlite3.connect(dgu.DB_NAME) as connection:
                            cursor = connection.cursor()
                            available_query = f"""SELECT available FROM wallet 
                                                WHERE exchange == '{exchange}' AND symbol == '{symbol}' LIMIT 2"""
                            cursor.execute(available_query)
                            records = cursor.fetchall()
                            if len(records) == 0:
                                print(f"None found {symbol} {exchange} ")
                                return False
                            if len(records) > 1:
                                raise Exception(
                                    f"Sell DB error.  Multiple|missing wallet records for {symbol} @ {exchange} \n{records}"
                                )
                            available = records[0][0]
                            return available > amount
                except sqlite3.Error as sql_error:
                    print(f"Sell CheckFunding SQL error: {sql_error}")
                except TypeError as type_error:
                    print(f"Sell CheckFunding type error: {type_error}")
                except Exception as e:
                    print(f"Sell CheckFunding exception: {e}")
        raise Exception(f"Unsupported side: {side}")

    def check_funding_and_trade(self, intent_id: int):
        try:
            connection = sqlite3.connect(dgu.DB_NAME)
            cursor = connection.cursor()
            intent_by_id = f"""SELECT id, pair, side, exchange, amount, limit_pennies, completed, failed, in_progress 
                    FROM intent WHERE id == {intent_id}"""
            cursor.execute(intent_by_id)
            records = cursor.fetchall()
            if len(records) == 0:
                raise Exception(f"Unknown intent ID: {intent_id}")
            if len(records) > 1:
                raise Exception(f"INVESTIGATE DATABASE!: {intent_id} {records}")

            record = records[0]
            if record[6] or record[7] or record[8]:
                print(f"DONE? {record}")
                return

            in_progress_intent_query = (
                f"UPDATE intent SET in_progress = 1 WHERE id == {intent_id}"
            )
            cursor.execute(in_progress_intent_query)
            connection.commit()
            cursor.close()

            intent_id = record[0]
            pair = record[1]
            side = record[2]
            exchange = record[3]
            amount = record[4]
            limit_pennies = record[5]
            funded = self.check_funding(side, pair, exchange, amount, limit_pennies)
            if not funded:
                print(f"Not funded. {side} {pair} {exchange} {amount}")
                return

            limit = float(f"{float(limit_pennies / 100.0):0.2f}")
            ex = self.exchanges[exchange]
            trade_result = ex.trade(pair, side, amount, limit)
            print(f"Trade: {trade_result}")
            completed = trade_result is not None
            print(f"COMPLETED? {completed}")
            failed = False if completed else bool(random.getrandbits(1))
            connection = sqlite3.connect(dgu.DB_NAME)
            cursor = connection.cursor()
            order_text = dgu.alphanumeric(f"{trade_result}")
            print(f"ORDERTEXT: {order_text}")
            if completed:
                update_intent_query = f"""UPDATE intent SET order_id = '{order_text}' 
                                        AND completed = 1 AND in_progress = 0 AND failed = 0
                                        WHERE id == {intent_id}"""
                cursor.execute(update_intent_query)
            else:
                failed_query = f"""UPDATE intent SET completed=0 AND failed={failed} 
                                        WHERE id == {intent_id}"""
                cursor.execute(failed_query)
            connection.commit()
            cursor.close()
        except sqlite3.Error as sql_error:
            print(f"ExBuy SQL error: {sql_error}")
        except TypeError as type_error:
            print(f"ExBuy type error: {type_error}")
        except Exception as e:
            print(f"ExBuy exception: {e}")

    #        finally:
    #            if connection:
    #                connection.close()

    def execute_trades_thread(self, side: str):
        while True:
            try:
                connection = sqlite3.connect(dgu.DB_NAME)
                cursor = connection.cursor()
                # TODO: FIX ALL INTENTS!
                select_intent_query = f"""SELECT id FROM intent 
                                            WHERE (completed IS NULL OR NOT completed) 
                                            AND (failed IS NULL OR NOT failed)
                                            AND (in_progress IS NULL OR NOT in_progress)
                                            AND side == '{side.upper()}' 
                                            ORDER BY id DESC"""
                cursor.execute(select_intent_query)
                records = cursor.fetchall()
                for r in records:
                    thread = threading.Thread(
                        target=self.check_funding_and_trade, args=(r[0],)
                    )
                    thread.start()
                    time.sleep(0.02)
                time.sleep(0.15)
            except sqlite3.Error as sql_error:
                print(f"Execute trade SQL error: {sql_error}")
            except TypeError as type_error:
                print(f"Execute trade type error: {type_error}")
            except Exception as e:
                print(f"Execute trade exception: {e}")

    #            finally:
    #                if connection:
    #                    connection.close()

    def grind(self):
        Thread(target=self.grind_thread).start()

    def grind_thread(self):
        while True:
            try:
                print(f"GRINDING...{dgu.time_str(datetime.now(tz=dgu.TZ_UTC))}")
                # take any wins that are available
                self.win()
                # pprint.pprint('S...')
                # stay liquid
                # self.sell_for_cash()
                pprint.pprint('B...')
                self.buy_smart()
                pprint.pprint('...')

                # make intents for current purchase and future sale expecting fees 0.5% ($5/$1000)
                # make intents long-lived

            except Exception as e:
                print(f"Grind exception: {e}")
            finally:
                time.sleep(0.3)

    def win(self):
        with threading.Lock():
            with sqlite3.connect(dgu.DB_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f"""SELECT pair FROM win WHERE completed IS NULL AND in_progress IS NULL GROUP BY pair ORDER BY RANDOM()"""
                )
                winning_pairs = cursor.fetchall()
                for p_row in winning_pairs:
                    pair = p_row[0]
                    win_query = f"""SELECT id, pair, order_locator, amount, limit_pennies FROM win 
                                    WHERE pair='{pair}' AND (NOT completed OR completed IS NULL) 
                                    AND (NOT in_progress OR in_progress IS NULL) 
                                    ORDER BY limit_pennies LIMIT 1"""
                    cursor.execute(win_query)
                    wins = cursor.fetchall()
                    if len(wins) == 1:
                        win = wins[0]
                        win_id = int(win[0])
                        amount = float(win[3])
                        limit_pennies = int(win[4])

                        bid_query = f"""SELECT id, exchange, pair, MAX(datetime(timestamp)), pennies FROM bid 
                                                WHERE pair='{pair}' GROUP BY exchange, pair ORDER BY pennies DESC LIMIT 5"""
                        # NOTE: we should get 1 record for each exchange
                        cursor.execute(bid_query)
                        bids = cursor.fetchall()

                        if bids:
                            diff_pennies = bids[0][4] - win[4]
                            diff_pennies = -1 if diff_pennies == 0 else diff_pennies
                            print(f"Next: {win} \t\t{diff_pennies:+g}")

                        for bid in bids:
                            bid_pennies = bid[4]
                            if bid_pennies > limit_pennies:
                                #                        print(f"BID: {bid}")
                                ex = bid[1]
                                if self.check_funding(
                                    "SELL", pair, ex, amount, limit_pennies
                                ):
                                    exchange: Exchange = self.exchanges[ex]
                                    limit = float(limit_pennies / 100.0)
                                    trade_result = exchange.trade(
                                        pair, "SELL", amount, limit
                                    )
                                    if trade_result is not None and {} != trade_result:
                                        try:
                                            self.record_completed_win(
                                                connection,
                                                cursor,
                                                ex,
                                                trade_result,
                                                win_id,
                                            )
                                        except OperationalError:
                                            try:
                                                self.record_completed_win(
                                                    connection,
                                                    cursor,
                                                    ex,
                                                    trade_result,
                                                    win_id,
                                                )
                                            except OperationalError:
                                                try:
                                                    self.record_completed_win(
                                                        connection,
                                                        cursor,
                                                        ex,
                                                        trade_result,
                                                        win_id,
                                                    )
                                                except OperationalError:
                                                    try:
                                                        self.record_completed_win(
                                                            connection,
                                                            cursor,
                                                            ex,
                                                            trade_result,
                                                            win_id,
                                                        )
                                                    except OperationalError:
                                                        self.record_completed_win(
                                                            connection,
                                                            cursor,
                                                            ex,
                                                            trade_result,
                                                            win_id,
                                                        )
                                        return

    def record_completed_win(self, connection, cursor, ex, trade_result, win_id):
        order_locator = (
            dgu.alphanumeric(str(trade_result)) + "_" + dgu.alphanumeric(str(ex))
        )
        update_win = f"""UPDATE win SET completed=1, order_locator='{order_locator}' 
                                                            WHERE ID={win_id}"""
        cursor.execute(update_win)
        connection.commit()
        cursor.close()
        print(f"WIN!!!\nORDER: {order_locator}\nUPDATE WIN: {update_win}")
        self._next_buy_time = datetime.now(tz=dgu.TZ_UTC) + timedelta(seconds=360)

    def sell_for_cash(self):
        for ex in self.exchanges.values():
            # TODO: use balances from database
            balances = ex.balances
            tickers = ex.tickers
            usd = float(balances["USD"])
            if (usd * 100) < (self.buy_pennies * 2):
                # need to sell something for cash
                print(f"LOW CASH: ${usd:2.2f} {type(ex)}")
                assets = []
                for b in balances:
                    if b != "USD" and b != "BTC" and b != "ETH" and (balances[b] > 0.0):
                        # is asset worth more than min buy?
                        asset_pair = f"{b}_USD"
                        bid = tickers[asset_pair]["BID"]
                        if bid * balances[b] * 100 > self.buy_pennies:
                            assets.append(b)

                if len(assets) > 0:
                    sell_this = random.choice(assets)
                    pair = f"{sell_this}_USD"
                    tic = tickers[pair]
                    bal = balances[sell_this]
                    print(f"BALANCE {bal}")
                    amount = dgu.smart_round((self.buy_pennies) / (tic["BID"] * 100))
                    limit = dgu.smart_round(tic["BID"] * 0.95)
                    print(f"{pair} {tic} {amount} {limit}")
                    sale = ex.trade(pair, "SELL", amount, limit)
                    if sale:
                        print("SALE")
                        pprint.pprint(sale)

    def buy_smart(self):
        trade = None
        try:
            if datetime.now(tz=dgu.TZ_UTC) < self._next_buy_time:
                return
            with threading.Lock():
                with sqlite3.connect(dgu.DB_NAME) as connection:
                    cursor = connection.cursor()
                    avoid_buying_this = random.choice(["GALA", "FTM"])
                    cursor.execute(
                        f"""SELECT bid.pair, bid.pennies, 
                        bid.pennies * wallet.available AS total_pennies
                        FROM bid INNER JOIN wallet ON bid.pair = wallet.symbol || '_USD'
                        WHERE wallet.symbol NOT IN ('SHIB', 'FLR', 'HBAR', '{avoid_buying_this}')
                        ORDER BY total_pennies"""
                    )

                    records = cursor.fetchall()
                    pair = dgu.BTC_USD_PAIR
                    amount = 0.0000

                    if records:
                        pairs, bid_pennies, total_pennies = zip(*records)
                        bid_pennies = np.array(bid_pennies)
                        total_pennies = np.array(total_pennies)
                        probabilities = total_pennies / total_pennies.sum()
                        sampled_index = random.choices(
                            range(len(pairs)), weights=probabilities
                        )[0]

                        # 80% just choose BTC
                        sampled_index = (
                            random.random() < 0.88
                            and pairs.index(dgu.BTC_USD_PAIR)
                            or sampled_index
                        )

                        # 5% choose ETH
                        sampled_index = (
                            random.random() < 0.005
                            and pairs.index(dgu.ETH_USD_PAIR)
                            or sampled_index
                        )

                        pair = pairs[sampled_index]
                        sampled_bid_pennies = bid_pennies[sampled_index]
                        amount = (
                            float(f"{(self.buy_pennies/sampled_bid_pennies):.5f}")
                            if sampled_bid_pennies > 100
                            else float(f"{(self.buy_pennies/sampled_bid_pennies):.0f}")
                        )
                    else:
                        print("No wallet records???")
                        return

            print(f"BUYING Pair: {pair}\tamount: {amount:.5f}")

            with threading.Lock():
                with sqlite3.connect(dgu.DB_NAME) as connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        f"""SELECT exchange, pennies FROM ask WHERE pair=='{pair}' ORDER BY pennies ASC LIMIT 1"""
                    )
                    records = cursor.fetchall()
                    if len(records) != 1:
                        print(f"No ASK found for {pair}")
                        return
                    exchange = records[0][0]
                    limit_pennies = int(records[0][1] * 1.001) + 1
                    limit = float(limit_pennies / 100.0)
                    print(f"Pair: {pair}\tamount: {amount:.5f}\tlimit: {limit}")
                    # TODO: look at db wallet instead
                    if self.check_funding("BUY", pair, exchange, amount, limit_pennies):
                        ex = self.exchanges[exchange]
                        print(
                            f"\nBest price exchange: {dgu.alphanumeric(str(type(ex)))} limit:{limit_pennies}"
                        )
                        # try to buy only at best exchange
                        trade = ex.trade(pair, "BUY", amount, float(f"{limit:0.2f}"))
                        print("Traded: ")
                        pprint.pprint(trade)
        except Exception as e:
            print("Buying exception: ")
            pprint.pprint(e)

        try:
            if trade is not None:
                for _ in range(10):
                    with threading.Lock():
                        with sqlite3.connect(dgu.DB_NAME) as connection:
                            save_cursor = connection.cursor()
                            try:
                                self.record_win(
                                    amount,
                                    connection,
                                    save_cursor,
                                    limit_pennies,
                                    pair,
                                    trade,
                                )
                                return
                            except OperationalError:
                                pass
                raise OperationalError("Failed to record_win")
        except Exception as ex:
            print(f'Exception Saving Trade: {ex}')

    def record_win(self, amount, connection, cursor, limit_pennies, pair, t):
        win_pennies = (
            dgu.round_to_nearest_hundred(int(limit_pennies * 1.0078))
            if limit_pennies > 10000
            else int(limit_pennies * 1.0078)
        )
        # TODO: use fee estimate
        # record future win with fixed profit
        cursor.execute(
            """INSERT INTO win (pair, amount, limit_pennies) VALUES (?, ?, ?);""",
            (pair, amount, win_pennies),
        )
        connection.commit()
        cursor.close()
        self._next_buy_time = datetime.now(tz=dgu.TZ_UTC) + timedelta(seconds=600)


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
                print(f"UNKNOWN ERROR: {records}")
            print(records)
            exit()

            for r in records:
                exchange = r[1]
                ex = self.exchanges.get(exchange)
                strike_price_in_pennies = int(r[5]) + int(int(r[5]) / 200)
                ex.strike_price_in_pennies = strike_price_in_pennies

            return None
        except sqlite3.Error as sql_error:
            print(f"WIN SQL error: {sql_error}")
        except TypeError as type_error:
            print(f"WIN Type error: {type_error}")
        except Exception as e:
            print(f"WIN Exception: {e}")
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
