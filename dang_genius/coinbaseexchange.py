import hashlib
import hmac
import json
import time
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
import coinbasepro as cbp
import numpy as np
import requests

from dang_genius.exchange import Exchange


class CoinbaseExchange(Exchange):
    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)
        self.api_url = 'https://coinbase.com'
        self.order_endpoint = "/api/v3/brokerage/orders"
        self.public_client = cbp.PublicClient()
        self.BTC_USD_PAIR: str = 'BTC-USD'
        self.BUY_SIDE: str = 'BUY'
        self.SELL_SIDE: str = 'SELL'
        self.ASK_KEY: str = 'ask'
        self.BID_KEY: str = 'bid'
        self.DIP: float = 0.001
        self.STRIKES = [35410.00]
        self.MAX_STRIKES = 1
        self.COVER: float = 400.0

    def buy_btc(self):
        self.trade(self.BTC_USD_PAIR, self.BUY_SIDE)

    def sell_btc(self):
        self.trade(self.BTC_USD_PAIR, self.SELL_SIDE)

    def set_limits(self, min_ask: float, max_bid: float) -> None:
        self.min_ask = min_ask
        self.max_bid = max_bid

    def get_ticker(self, pair:str) -> dict:
        order_book = self.public_client.get_product_order_book(pair)
        ask: float = float(order_book.get('asks')[0][0])
        bid: float = float(order_book.get('bids')[0][0])
        return {self.ASK_KEY: ask, self.BID_KEY: bid}


    def buy_btc_dip(self):
        self.buy_the_dip(self.BTC_USD_PAIR)


    def buy_the_dip(self, pair: str):
        # read the market
        # identify when a dip has occurred
        # buy at the market rate
        top_bid = 0.0
        top_ask = 0.0

        while True:
            ticker = self.get_ticker(self.BTC_USD_PAIR)
            ask: float =  float(ticker.get(self.ASK_KEY))
            if ask > top_ask:
                top_ask = ask
            bid: float = float(ticker.get(self.BID_KEY))

            if len(self.STRIKES) > 0:
                lowest_strike = np.min(self.STRIKES)
                if lowest_strike and bid > lowest_strike:
                    self.set_limits(bid, bid)
                    sell_tx = self.trade(pair, self.SELL_SIDE)
                    if sell_tx:
                        print(f'SOLD! {sell_tx}')
                        self.STRIKES.remove(lowest_strike)
            if bid > top_bid:
                top_bid = bid
            if (ask + bid) * (1 + self.DIP) < (top_ask + top_bid) and len(self.STRIKES) < self.MAX_STRIKES:
                print(f"DIP {ask:8.2f} {bid:8.2f} TOP: {top_ask:8.2f} {top_bid:8.2f}")
                self.set_limits(ask, ask)
                tx = self.trade(pair, self.BUY_SIDE)
                if tx:
                    strike = float(tx.get("price")) + self.COVER
                    print(f'CB COVER PRICE: {strike}')
                    self.STRIKES.append(strike)
                    top_ask = 0.0
                    top_bid = 0.0
                    time.sleep(10)
            time.sleep(1)


    #    https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder
    def trade(self, pair: str, side: str):
        room = float((self.max_bid - self.min_ask) / 3.0)
        price = (self.min_ask + room) if side == 'buy' else (self.max_bid - room)
        now = datetime.now(tz=ZoneInfo("UTC"))
        client_order_id = 'CB-order-' + now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        end_time = now + timedelta(milliseconds=2001)
        ets = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        timestamp = str(int(time.time()))
        payload = {
            "side": side,
            "client_order_id": client_order_id,
            "product_id": pair,
            "order_configuration": {
                "limit_limit_gtd": {
                    "base_size": f'{self.btc_amount:0.5f}',
                    "limit_price": f'{price:0.2f}',
                    "end_time": ets,
                    "post_only": False
                }
            }
        }
        print(f'TIMESTAMP: {timestamp}')
        message = timestamp + "POST" + self.order_endpoint + json.dumps(payload)
        signature = hmac.new(self.secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
        headers = {
            'CB-ACCESS-SIGN': signature.hex(),
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.key,
            'User-Agent': 'my-user-agent',
            'accept': "application/json",
            'Content-Type': 'application/json'
        }

        try:
            new_order = requests.post(self.api_url + self.order_endpoint,
                                      data=json.dumps(payload), headers=headers).json()
            if new_order.get('result') == 'error':
                # TODO: retry??
                print(f'CB ERROR: {new_order}')
            else:
                if new_order.get('error') == 'unknown':
                    print(f'CB UNKNOWN ERROR {new_order}')
                else:
                    if (new_order.get('success') and new_order.get('success_response')
                            and new_order.get('order_configuration')
                            and new_order.get('order_configuration').get('limit_limit_gtd')):
                        response = new_order.get('success_response')
                        print(f'CB SUCCESS: {response}')
                        order_id = new_order.get('order_id')
                        # TODO: product_id, side, client_order_id,
                        # TODO: get actual execution price
                        config = new_order.get('order_configuration').get('limit_limit_gtd')
                        tx_price = config.get('limit_price')
                        # TODO: timestampms
                        # TODO: add KEYS to self
                        return { "price": tx_price, "order_id": order_id, "timestamp": timestamp, "timestampms": timestamp }
                print(f'CB ERROR {new_order}')

        except Exception as e:
            print(f'CB EXCEPTION: {e}')


    def market_trade(self, pair: str, side: str):
        # market orders set size [optional]* Desired amount in BTC
        # time_in_force = 'FOK' not for market
        # client_order_id can be added later must be UNIQ
        quote_size = f'{self.btc_amount * self.min_ask:.2f}'
        mm = {"quote_size": quote_size} if side == self.BUY_SIDE else {"base_size": f'{self.btc_amount:0.5f}'}

        timestamp = str(int(time.time()))

        payload = {
            "side": side,
            "client_order_id": f'CB-order-{timestamp}',
            "product_id": pair,
            "order_configuration": {
                "market_market_ioc": mm
            }
        }

        message = timestamp + "POST" + self.order_endpoint + json.dumps(payload)
        signature = hmac.new(self.secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
        headers = {
            'CB-ACCESS-SIGN': signature.hex(),
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.key,
            'User-Agent': 'my-user-agent',
            'accept': "application/json",
            'Content-Type': 'application/json'
        }

        try:
            new_order = requests.post(self.api_url + self.order_endpoint,
                                      data=json.dumps(payload), headers=headers).json()
            if new_order.get('result') == 'error':
                # TODO: retry??
                print(f'CB ERROR: {new_order}')
            else:
                # TODO: this can include cancelled orders????
                print(f'CB SUCCESS: {new_order}')

        except Exception as e:
            print(f'CB EXCEPTION: {e}')

# CB SUCCESS: {'success': True, 'failure_reason': 'UNKNOWN_FAILURE_REASON', 'order_id': 'be546e69-554a-4f93-b201-5b5702b4c801', 'success_response':
# {'order_id': 'be546e69-554a-4f93-b201-5b5702b4c801', 'product_id': 'BTC-USD', 'side': 'SELL', 'client_order_id': 'CB-order-1698437759'},
# 'order_configuration': {'market_market_ioc': {'base_size': '0.00010'}}}
# 2023-10-27 16:16:00.513768 min_ask:   33700.00  max_bid:   33731.99     Spread:  31.99  Fee:  25.30     TRADE buy 0.00010 XBTUSD KRAKEN ...
# SELL 0.00010 BTC