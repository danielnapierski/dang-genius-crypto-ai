import base64
import hashlib
import hmac
import json
import ssl
import time
from threading import Thread

import requests
import websocket

# See: https://github.com/eliasbenaddou/gemini_api
from gemini_api.endpoints.public import Public

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class GeminiExchange(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.api_url = "https://api.gemini.com"
        self.order_endpoint = "/v1/order/new"
        self.balances_endpoint = "/v1/balances"
        self._asks = {}
        self._bids = {}
        self._supported_pairs = {
            dgu.BTC_USD_PAIR: "btcusd",
            dgu.ETH_USD_PAIR: "ethusd",
            dgu.ETH_BTC_PAIR: "ethbtc",
            dgu.ALI_USD_PAIR: "aliusd",
            dgu.ATOM_USD_PAIR: "atomusd",
            dgu.AMP_USD_PAIR: "ampusd",
            dgu.AVAX_USD_PAIR: "avaxusd",
            dgu.CUBE_USD_PAIR: "cubeusd",
            dgu.FET_USD_PAIR: "fetusd",
            dgu.FIL_USD_PAIR: "filusd",
            dgu.FTM_USD_PAIR: "ftmusd",
            dgu.GALA_USD_PAIR: "galausd",
            dgu.GMT_USD_PAIR: "gmtusd",
            dgu.IMX_USD_PAIR: "imxusd",
            dgu.PEPE_USD_PAIR: "pepeusd",
            dgu.SAMO_USD_PAIR: "samousd",
            dgu.SHIB_USD_PAIR: "shibusd",
            dgu.XTZ_USD_PAIR: "xtzusd",
            dgu.YFI_USD_PAIR: "yfiusd",
            dgu.ZBC_USD_PAIR: "zbcusd",
            dgu.ZEC_USD_PAIR: "zecusd",
        }
        self.BUY_SIDE = "buy"
        self.SELL_SIDE = "sell"
        self.public_api = Public()
        Thread(target=self.follow_market_thread, daemon=True).start()

    def follow_market_thread(self):
        symbols = []
        for v in self._supported_pairs.values():
            symbols.append(v.upper())
        symbol_str = ",".join(symbols)
        ws = websocket.WebSocketApp(
            f"wss://api.gemini.com/v1/multimarketdata?top_of_book=true&symbols={symbol_str}",
            on_message=self.on_message,
        )
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def on_message(self, ws, message):
        message_object = json.loads(message)
        event = message_object["events"][0]
        side = event["side"]
        symbol = event["symbol"]
        price = float(event["price"])
        if side == "ask":
            self._asks[symbol] = price
        if side == "bid":
            self._bids[symbol] = price

    @staticmethod
    def _get_nonce() -> str:
        return str(int(1000 * time.time()) + 11698339415999)

    def _make_headers(self, request_endpoint: str):
        b64 = base64.b64encode(
            json.dumps(
                {"request": request_endpoint, "nonce": self._get_nonce()}
            ).encode("utf-8")
        )
        signature = hmac.new(
            self._secret.encode("utf-8"), b64, hashlib.sha384
        ).hexdigest()

        return {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self._key,
            "X-GEMINI-PAYLOAD": b64,
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache",
        }

    @property
    def balances(self) -> dict:
        try:
            request_headers = self._make_headers(self.balances_endpoint)
            request = requests.post(
                self.api_url + self.balances_endpoint,
                data=None,
                headers=request_headers,
            )
            data = request.json()

            currencies = ["USD"]
            for dgu_pair in self._supported_pairs.keys():
                currencies.append(str(dgu_pair.split("_")[0]).upper())

            result = {}
            for d in data:
                currency = str(d.get("currency")).upper()
                if currency in currencies:
                    a = float(d.get("available"))
                    result[currency] = (
                        float(f"{a: .2f}") if currency == "USD" else float(f"{a: .2E}")
                    )
            return result
        except Exception as e:
            print(f"Gemini balances exception: {e}")
            return {}

    def get_ticker(self, pair: str):
        ticker = self.public_api.get_ticker(pair)
        return {
            dgu.ASK_KEY: (float(ticker.get("ask"))),
            dgu.BID_KEY: (float(ticker.get("bid"))),
        }

    @property
    def tickers(self) -> dict[str, dict | None]:
        try:
            tickers = {}
            for pair in self._supported_pairs.keys():
                gp = self._supported_pairs[pair].upper()
                if gp in self._asks.keys() and gp in self._bids.keys():
                    ask = self._asks[gp]
                    bid = self._bids[gp]
                    tickers[pair] = {dgu.ASK_KEY: ask, dgu.BID_KEY: bid}
                    continue

                tickers[pair] = self.get_ticker(self._supported_pairs[pair])
            return tickers
        except Exception as e:
            print(f"Gemini tickers exception: {e}")
            return {}

    def match_pair(self, dgu_pair: str):
        if dgu_pair in self._supported_pairs.keys():
            return self._supported_pairs[dgu_pair]
        raise Exception(f"Unsupported pair: {dgu_pair}")

    def trade(
        self,
        dgu_pair: str,
        side: str,
        amount: float,
        limit: float,
        optionality: float | None = None,
    ):
        # https://docs.gemini.com/rest-api/#new-order
        price = float(f"{limit: .8f}") if limit < 1.0 else float(f"{limit: .2f}")
        try:
            payload = {
                "request": self.order_endpoint,
                "nonce": self._get_nonce(),
                "symbol": self.match_pair(dgu_pair),
                "amount": float(f"{amount: 0.5f}"),
                "side": side,
                "type": "exchange limit",
                "price": price,
                "options": ["immediate-or-cancel"],
            }

            b64 = base64.b64encode(json.dumps(payload).encode())
            request_headers = {
                "Content-Type": "text/plain",
                "Content-Length": "0",
                "X-GEMINI-APIKEY": self._key,
                "X-GEMINI-PAYLOAD": b64,
                "X-GEMINI-SIGNATURE": (
                    hmac.new(self._secret.encode(), b64, hashlib.sha384).hexdigest()
                ),
                "Cache-Control": "no-cache",
            }

            new_order = requests.post(
                self.api_url + self.order_endpoint, data=None, headers=request_headers
            ).json()
            if new_order.get("result") == "error":
                print(f"GEMINI ERROR: {new_order}")
            else:
                if new_order.get("remaining_amount") == "0":
                    tx_price = new_order.get("avg_execution_price")
                    order_id = new_order.get("order_id")
                    timestamp = new_order.get("timestamp")
                    timestampms = new_order.get("timestampms")
                    symbol = new_order.get("symbol")
                    side = new_order.get("side")
                    amount = new_order.get("executed_amount")
                    return {
                        "price": tx_price,
                        "order_id": order_id,
                        "timestamp": timestamp,
                        "timestampms": timestampms,
                        "symbol": symbol,
                        "side": side,
                        "amount": amount,
                    }
                else:
                    print(f"GEMINI FAIL or partial fill: {new_order}")
                    # success can be a cancelled order
        except Exception as e:
            print(f"GEMINI trade exception: {e}")
