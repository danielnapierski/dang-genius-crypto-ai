import base64
import hashlib
import hmac
import json
import pprint
import threading
import time
import urllib.parse

import krakenex
# See: https://github.com/veox/python3-krakenex
import requests
import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class KrakenExchange(Exchange):

    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.api_url = "https://api.kraken.com"
        self.public_client = krakenex.API()
        self.private_client = krakenex.API(self._key, self._secret)
        self._lock = threading.Lock()
        self.supported_pairs = {
            dgu.BTC_USD_PAIR: "XXBTZUSD",
            dgu.ETH_USD_PAIR: "XETHZUSD",
            dgu.ETH_BTC_PAIR: "XETHXXBT",
            dgu.ADA_USD_PAIR: "ADAUSD",
            dgu.ALGO_USD_PAIR: "ALGOUSD",
            dgu.ALPHA_USD_PAIR: "ALPHAUSD",
            dgu.AVAX_USD_PAIR: "AVAXUSD",
            dgu.APT_USD_PAIR: "APTUSD",
            dgu.AXS_USD_PAIR: "AXSUSD",
            dgu.BAT_USD_PAIR: "BATUSD",
            dgu.BLUR_USD_PAIR: "BLURUSD",
            dgu.CHZ_USD_PAIR: "CHZUSD",
            dgu.COMP_USD_PAIR: "COMPUSD",
            dgu.CRV_USD_PAIR: "CRVUSD",
            dgu.DOT_USD_PAIR: "DOTUSD",
            dgu.ENS_USD_PAIR: "ENSUSD",
            dgu.FET_USD_PAIR: "FETUSD",
            dgu.FIL_USD_PAIR: "FILUSD",
            dgu.FLR_USD_PAIR: "FLRUSD",
            dgu.FTM_USD_PAIR: "FTMUSD",
            dgu.GALA_USD_PAIR: "GALAUSD",
            dgu.GMT_USD_PAIR: "GMTUSD",
            dgu.GRT_USD_PAIR: "GRTUSD",
            dgu.IMX_USD_PAIR: "IMXUSD",
            dgu.INJ_USD_PAIR: "INJUSD",
            dgu.JUP_USD_PAIR: "JUPUSD",
            dgu.KNC_USD_PAIR: "KNCUSD",
            dgu.LDO_USD_PAIR: "LDOUSD",
            dgu.LINK_USD_PAIR: "LINKUSD",
            dgu.LPT_USD_PAIR: "LPTUSD",
            dgu.LRC_USD_PAIR: "LRCUSD",
            dgu.MANA_USD_PAIR: "MANAUSD",
            dgu.MATIC_USD_PAIR: "MATICUSD",
            dgu.MKR_USD_PAIR: "MKRUSD",
            dgu.NEAR_USD_PAIR: "NEARUSD",
            dgu.PHA_USD_PAIR: "PHAUSD",
            dgu.OP_USD_PAIR: "OPUSD",
            dgu.OXT_USD_PAIR: "OXTUSD",
            dgu.QNT_USD_PAIR: "QNTUSD",
            dgu.REN_USD_PAIR: "RENUSD",
            dgu.RNDR_USD_PAIR: "RNDRUSD",
            dgu.SHIB_USD_PAIR: "SHIBUSD",
            dgu.SNX_USD_PAIR: "SNXUSD",
            dgu.SOL_USD_PAIR: "SOLUSD",
            dgu.STORJ_USD_PAIR: "STORJUSD",
            dgu.STRK_USD_PAIR: "STRKUSD",
            dgu.SUSHI_USD_PAIR: "SUSHIUSD",
            dgu.UMA_USD_PAIR: "UMAUSD",
            dgu.UNI_USD_PAIR: "UNIUSD",
            dgu.WAXL_USD_PAIR: "WAXLUSD",
            dgu.XCN_USD_PAIR: "XCNUSD",
            dgu.XTZ_USD_PAIR: "XTZUSD",
            dgu.ZRX_USD_PAIR: "ZRXUSD",
        }
        # Note ['EAccount:Invalid permissions:SAMO trading restricted for US:MA.']
        # The following assets are restricted for US clients:
        # ACA, AGLD, ALICE, ASTR, ATLAS, AUDIO, AVT, BONK, CFG, CSM, C98, GENS, GLMR, HDX, INJ, INTR, JASMY, KIN, LMWR,
        # MC, MV, NMR, NODL, NYM, ORCA, OTP, OXY, PARA, PEPE, PERP, PICA, POL, PSTAKE, PYTH, RAY, REQ, ROOK, SAMO, SDN,
        # STEP, SUI, SXP, TEER, WETH, WIF, WOO, YGG or XRT.

    @property
    def balances(self) -> dict:
        with self._lock:
            b = self.private_client.query_private("Balance")["result"]

        products = {}
        for p in self.supported_pairs.values():
            chars = len(p)
            half = int((chars + 1) / int(2))
            products[p[0:half]] = True
            products[p[half:chars]] = True

        balances = {}
        for k in products.keys():
            try:
                cn = self._get_common_name(str(k).upper())
                balances[cn] = float(b.get(k))
            except TypeError:
                pass
        return balances

    @staticmethod
    def _get_common_name(kraken_symbol: str):
        if kraken_symbol.upper() == "ZUSD":
            return "USD"
        if kraken_symbol.upper() == "XXBT" or kraken_symbol.upper() == "XBT":
            return "BTC"
        if kraken_symbol.upper() == "XETH":
            return "ETH"
        return kraken_symbol

    @staticmethod
    def _get_kraken_signature(urlpath, data, secret):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data["nonce"]) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def _kraken_request(self, uri_path, data, api_key, api_sec):
        with self._lock:
            headers = {
                "API-Key": api_key,
                "API-Sign": self._get_kraken_signature(uri_path, data, api_sec),
            }
            return requests.post((self.api_url + uri_path), headers=headers, data=data)

    def get_ticker_deprecated(self, pair: str):
        with self._lock:
            tic = (
                self.public_client.query_public("Depth", {"pair": pair, "count": "1"})
                .get("result")
                .get(pair)
            )

            if self.supported_pairs[dgu.BTC_USD_PAIR] == pair:
                tic2 = self.public_client.query_public("Depth", {"count": "1"})
                pprint.pprint(tic2)

            return {
                dgu.ASK_KEY: (float(tic.get("asks")[0][0])),
                dgu.BID_KEY: (float(tic.get("bids")[0][0])),
            }

    @property
    def tickers(self) -> dict[str, dict | None]:
        try:
            tickers = {}
            t = self.public_client.query_public("Ticker")["result"]
            for pair in self.supported_pairs.keys():
                tp = t[self.supported_pairs[pair]]
                tickers[pair] = { dgu.ASK_KEY: float(tp['a'][0]), dgu.BID_KEY: float(tp['b'][0]) }
            return tickers
        except Exception as e:
            print(f"KRAKEN tickers exception: {e}")
            return {}

    def match_pair(self, dgu_pair: str):
        if dgu_pair in self.supported_pairs.keys():
            return self.supported_pairs[dgu_pair]
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
            price = f"{limit:.1f}" if limit > 1.0 else f"{limit:.8f}"
            response = self._kraken_request(
                "/0/private/AddOrder",
                {
                    "nonce": str(int(1000 * time.time())),
                    "ordertype": "limit",
                    "price": price,
                    "type": side.lower(),
                    "volume": amount,
                    "pair": self.match_pair(dgu_pair),
                    "timeinforce": "ioc",
                },
                self._key,
                self._secret,
            )

            json_response = json.loads(getattr(response, "text"))
            error = json_response.get("error")
            if error:
                raise Exception(
                    f"KRAKEN AddOrder error response: {error}\n{dgu_pair}|{price}|{amount}|{side}"
                )
            result = json_response.get("result")
            # {'txid': [''], 'descr' : {'order': 'buy ...'}}
            txid = result["txid"][0]
            trade = self._get_closed_trade(txid)
            if "closed" in trade.keys() and trade["closed"]:
                return trade
            print("KRAKEN tx failed/canceled.")

        except Exception as e:
            print(f"KRAKEN trade exception: {e}")

    def _get_closed_trade(self, txid: str) -> dict:
        response = self._kraken_request(
            "/0/private/ClosedOrders",
            {"nonce": str(int(1000 * time.time()))},
            self._key,
            self._secret,
        ).json()
        # status could be 'closed' 'canceled' or something else possibly
        tx = response["result"]["closed"][txid]
        is_closed = "closed" == tx["status"]
        if not is_closed:
            return {}
        price = tx["price"]
        cost = tx["cost"]
        fee = tx["fee"]
        # TODO: add symbol/product
        # add side, fees, timestamp
        trade = {"closed": is_closed, "price": price, "cost": cost, "fee": fee}
        print(trade)
        return trade
