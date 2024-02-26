class Exchange:

    def __init__(self, key: str, secret: str):
        self._key = key
        self._secret = secret

    @property
    def balances(self):
        raise NotImplementedError("Exchanges should implement balances.")

    @property
    def tickers(self) -> dict[str, dict | None]:
        raise NotImplementedError("Exchanges should implement tickers.")

    def trade(self, pair: str, side: str, amount: float, limit: float, optionality: float | None = None):
        raise NotImplementedError("Exchanges should implement trading.")
