from dang_genius.exchange import Exchange


class CoinbaseExchange(Exchange):
    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)

    def buy_btc(self):
        print(f'BUY {self.btc_amount:.5f} BTC COINBASE')

    def sell_btc(self):
        print(f'SELL {self.btc_amount:.5f} BTC COINBASE')