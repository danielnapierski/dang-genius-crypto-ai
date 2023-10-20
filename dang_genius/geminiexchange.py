from dang_genius.exchange import Exchange


class GeminiExchange(Exchange):
    def __init__(self, key: str, secret: str, btc_amount: float):
        super().__init__(key, secret, btc_amount)

    def buyBtc(self):
        print(f'BUY {self.btc_amount:.5f} BTC GEMINI')

    def sellBtc(self):
        print(f'SELL {self.btc_amount:.5f} BTC GEMINI')