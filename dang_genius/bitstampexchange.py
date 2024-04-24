import pprint
import threading

import bitstamp.client

import dang_genius.util as dgu
from dang_genius.exchange import Exchange


class BitstampExchange(Exchange):
    def __init__(self, key: str, secret: str, client_id: str):
        super().__init__(key, secret)
        self.public_client = bitstamp.client.Public()
        self.trading_client = bitstamp.client.Trading(client_id, key, secret)
        self._lock = threading.Lock()
        self._supported_pairs = [
            dgu.BTC_USD_PAIR,
            dgu.ETH_USD_PAIR,
            dgu.ETH_BTC_PAIR,
#            dgu.AAVE
#            dgu.APE
            dgu.AVAX_USD_PAIR,
            dgu.BAT_USD_PAIR,
            dgu.CRV_USD_PAIR,
            dgu.COMP_USD_PAIR,
            dgu.DOT_USD_PAIR,
#            dgu.DAI
#            dgu.ENJ
            dgu.FTM_USD_PAIR,
            dgu.GRT_USD_PAIR,
            dgu.HBAR_USD_PAIR,
            dgu.LINK_USD_PAIR,
            dgu.MKR_USD_PAIR,
            dgu.UNI_USD_PAIR,
#            dgu.PAX
            dgu.SHIB_USD_PAIR,
            dgu.YFI_USD_PAIR,
            dgu.ZRX_USD_PAIR
        ]

    @property
    def balances(self):
        try:
            with self._lock:
                b = self.trading_client.account_balance(False, False)

            keys = b.keys()
            result = {}
            for dp in self._supported_pairs:
                product = dp.split("_")[0].lower()
                k = f"{product}_available"
                if k in keys:
                    a = float(b[k])
                    result[product.upper()] = float(f"{a: .5f}")
            usd = 0.0
            if "usd_available" in keys:
                usd = float(b["usd_available"])
            result["USD"] = float(f"{usd: .2f}")
            return result
        except Exception as e:
            print(f"BS balances exception: {e}")
            return None

    @property
    def tickers(self) -> dict[str, dict | None] | None:
        with self._lock:
            try:
                tics = self.public_client.ticker(False, False)
                tickers = {}
                for i in tics:
                    p = str(i["pair"]).replace("/", "_").upper()
                    if p in self._supported_pairs:
                        tickers[p] = {
                            dgu.ASK_KEY: float(i["ask"]),
                            dgu.BID_KEY: float(i["bid"]),
                        }

                return tickers
            except Exception as e:
                print("BS tickers exception")
                pprint.pprint(e)
                return None

    def _decode_dgu_pair(self, dgu_pair: str):
        print(f'PAIR: "{dgu_pair}"')
        [
            base,
            quote,
        ] = dgu_pair.split("_")
        if len(base) < 2 or len(quote) < 2:
            raise Exception(f"Unknown pair: {dgu_pair}")
        return [str(base).upper(), str(quote).upper()]

    def trade(
        self,
        dgu_pair: str,
        side: str,
        amount: float,
        limit: float,
        optionality: float | None = None,
    ) -> object:
        with self._lock:
            try:
                [base, quote] = self._decode_dgu_pair(dgu_pair)
                price = (
                    float(f"{limit: .8f}") if limit < 1.0 else float(f"{limit: .0f}")
                )
                response = None
                if side.lower() == "buy":
                    response = self.trading_client.buy_limit_order(
                        amount, price, base, quote, ioc_order=True
                    )
                if side.lower() == "sell":
                    response = self.trading_client.sell_limit_order(
                        amount, price, base, quote, ioc_order=True
                    )
                if not response:
                    raise Exception(
                        f"BS no response.  {dgu_pair} {side} {amount} {price} "
                    )
                pprint.pprint(response)
                # {'amount': '0.00020000',
                #  'datetime': '2024-02-29 17:36:45.597000',
                #  'id': '1721930673926146',
                #  'market': 'BTC/USD',
                #  'price': '61799',
                #  'type': '0'}
                order_id = response["id"]
                status_response = self.trading_client.order_status(order_id)
                pprint.pprint(status_response)
                # {'status': 'Finished',
                #  'transactions': [{'datetime': '2024-02-29 23:09:22',
                #                    'eth': '0.00500000',
                #                    'fee': '0.06675000',
                #                    'price': '3337.60000000',
                #                    'tid': 322837345,
                #                    'type': 2,
                #                    'usd': '16.68800000'}]}
                if status_response["status"] == "Finished":
                    transaction = status_response["transactions"][0]
                    # {'btc': '0.00050000',
                    #  'datetime': '2024-02-29 23:21:05',
                    #  'fee': '0.12282000',
                    #  'price': '61410.00000000',
                    #  'tid': 322838502,
                    #  'type': 2,
                    #  'usd': '30.70500000'}
                    return transaction
                raise Exception(f"Order failed/canceled: {status_response}")
            except Exception as e:
                print(f"BS trade exception: {e}")
                return None
