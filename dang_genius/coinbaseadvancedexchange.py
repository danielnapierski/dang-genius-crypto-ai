import json
import pprint
import time
from datetime import datetime
from datetime import timedelta

import asyncio
from threading import Thread

import websockets

import coinbasepro as cbp
import requests
from coinbase import jwt_generator
from coinbase.rest import RESTClient

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class CoinbaseAdvancedExchange(Exchange):
    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.public_client = cbp.PublicClient()
        self.private_client = RESTClient(key, secret)
        self._asks = {}
        self._bids = {}
        self._supported_pairs = {
            dgu.BTC_USD_PAIR: "BTC-USD",
            dgu.ETH_USD_PAIR: "ETH-USD",
            dgu.ETH_BTC_PAIR: "ETH-BTC",
            dgu.ABT_USD_PAIR: "ABT-USD",
            dgu.ADA_USD_PAIR: "ADA-USD",
            dgu.AERO_USD_PAIR: "AERO-USD",
            dgu.AIOZ_USD_PAIR: "AIOZ-USD",
            dgu.ALEPH_USD_PAIR: "ALEPH-USD",
            dgu.ALGO_USD_PAIR: "ALGO-USD",
            dgu.APT_USD_PAIR: "APT-USD",
            dgu.AUDIO_USD_PAIR: "AUDIO-USD",
            dgu.AVAX_USD_PAIR: "AVAX-USD",
            dgu.BONK_USD_PAIR: "BONK-USD",
            dgu.CTX_USD_PAIR: "CTX-USD",
            dgu.DOGE_USD_PAIR: "DOGE-USD",
            dgu.FET_USD_PAIR: "FET-USD",
            dgu.FLR_USD_PAIR: "FLR-USD",
            dgu.GMT_USD_PAIR: "GMT-USD",
            dgu.HBAR_USD_PAIR: "HBAR-USD",
            dgu.HNT_USD_PAIR: "HNT-USD",
            dgu.IMX_USD_PAIR: "IMX-USD",
            dgu.INJ_USD_PAIR: "INJ-USD",
            dgu.IOTX_USD_PAIR: "IOTX-USD",
            dgu.KNC_USD_PAIR: "KNC-USD",
            dgu.NEAR_USD_PAIR: "NEAR-USD",
            dgu.OP_USD_PAIR: "OP-USD",
            dgu.SHIB_USD_PAIR: "SHIB-USD",
            dgu.SKL_USD_PAIR: "SKL-USD",
            dgu.STRK_USD_PAIR: "STRK-USD",
            dgu.SUI_USD_PAIR: "SUI-USD",
            dgu.WAXL_USD_PAIR: "WAXL-USD",
            dgu.WCFG_USD_PAIR: "WCFG-USD",
            dgu.XCN_USD_PAIR: "XCN-USD",
            dgu.XTZ_USD_PAIR: "XTZ-USD",
            dgu.XYO_USD_PAIR: "XYO-USD",
            dgu.ZEN_USD_PAIR: "ZEN-USD",
            dgu.ZETA_USD_PAIR: "ZETA-USD",
        }
        # GALA not supported.
        Thread(target=self.follow_market_thread).start()

    def follow_market_thread(self):
        product_ids = []
        for v in self._supported_pairs.values():
            product_ids.append(v.upper())

        asyncio.run(self.listen("wss://ws-feed.exchange.coinbase.com", product_ids))

    async def listen(self, uri, product_ids):
        async with websockets.connect(uri) as websocket:
            await websocket.send(
                json.dumps(
                    {
                        "type": "subscribe",
                        "product_ids": product_ids,
                        "channels": ["ticker"],
                    }
                )
            )
            while True:
                try:
                    response_str = await websocket.recv()
                    response = json.loads(response_str)
                    if response["type"] == "ticker":
                        ask = float(response["best_ask"])
                        bid = float(response["best_bid"])
                        symbol = response["product_id"]
                        self._asks[symbol] = ask
                        self._bids[symbol] = bid
                except Exception as e:
                    print(f"CBA websocket error: {e}")

    # https://docs.cloud.coinbase.com/advanced-trade-api/docs/sdk-rest-overview
    def _generate_jwt(self):
        request_method = "GET"
        request_path = "/api/v3/brokerage/accounts"
        jwt_uri = jwt_generator.format_jwt_uri(request_method, request_path)
        jwt_token = jwt_generator.build_rest_jwt(jwt_uri, self._key, self._secret)
        return jwt_token

    @property
    def balances(self) -> dict:
        try:
            response = self.private_client.get_accounts()
            currencies = ["USD"]
            for dgu_pair in self._supported_pairs.keys():
                currencies.append(str(dgu_pair.split("_")[0]).upper())
            balances = {}
            for account in response["accounts"]:
                currency = account["currency"]
                if currency in currencies:
                    val = float(account["available_balance"]["value"])
                    balances[currency] = (
                        float(f"{val: .2f}")
                        if currency == "USD"
                        else float(f"{val: .2E}")
                    )
            return balances
        except Exception as e:
            print("CBA balances error: ")
            pprint.pprint(e)
            return {}

    def get_ticker(self, pair: str) -> dict[str, float] | None:
        try:
            time.sleep(0.003)
            order_book = self.public_client.get_product_order_book(pair)
            return {
                dgu.ASK_KEY: (float(order_book.get("asks")[0][0])),
                dgu.BID_KEY: (float(order_book.get("bids")[0][0])),
            }
        except requests.exceptions.ReadTimeout as readtimeout_error:
            print(f"CBA ticker ReadTimeout error: {readtimeout_error}")
            return None
        except Exception as error:
            print(f"CBA ticker Exception error: {error} \nPair: {pair}")
            return None

    @property
    def tickers(self) -> dict[str, dict | None]:
        tickers = {}
        for pair in self._supported_pairs.keys():
            cbap = self._supported_pairs[pair].upper()
            if cbap in self._asks.keys() and cbap in self._bids.keys():
                ask = self._asks[cbap]
                bid = self._bids[cbap]
                tickers[pair] = {dgu.ASK_KEY: ask, dgu.BID_KEY: bid}
                continue

            tickers[pair] = self.get_ticker(self._supported_pairs[pair])
        return tickers

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
        try:
            price = float(f"{limit: .8f}") if limit < 1.0 else float(f"{limit: .5f}")
            client_order_id = dgu.generate_order_id(self)
            product_id = self.match_pair(dgu_pair)
            base_size = f"{amount:.5f}"
            now = datetime.now(tz=dgu.TZ_UTC)
            end_time = now + timedelta(milliseconds=3001)
            order_response = self.private_client.limit_order_gtd(
                client_order_id,
                product_id,
                side.upper(),
                base_size,
                f"{price}",
                dgu.time_str(end_time),
            )
            if "error_response" in order_response.keys():
                print("CBA trade error: ")
                pprint.pprint(order_response)
                return

            order_id = order_response["order_id"]
            #            print(f'ORDER ID: {order_id}')

            for t in [100, 200, 400, 2600]:
                time.sleep(float(t / 1000.0))
                fills_response = self.private_client.get_fills(order_id=order_id)
                fills = fills_response["fills"]
                if fills:
                    for f in fills:
                        if order_id == f["order_id"]:
                            #                            pprint.pprint(f)
                            # {'commission': '0.NNNNN',
                            #  'entry_id': 'HASH...',
                            #  'liquidity_indicator': 'TAKER',
                            #  'order_id': 'HASH...',
                            #  'price': 'NUM_USD_DOLLARS',
                            #  'product_id': 'BTC-USD',
                            #  'sequence_timestamp': '2024-12-29T17:08:21.462918Z',
                            #  'side': 'BUY',
                            #  'size': '0.0001',
                            #  'size_in_quote': False,
                            #  'trade_id': 'HASH...',
                            #  'trade_time': '2024-12-29T17:08:21.459857Z',
                            #  'trade_type': 'FILL',
                            #  'user_id': 'may_be_same_as_principal_in_api_key_json'}
                            return f
        except Exception as e:
            print("CBA trade error: ")
            pprint.pprint(e)
