
class Exchange:
    _recent_btc_high_in_pennies: int
    _strike_price_in_pennies: int

    def __init__(self, key: str, secret: str, btc_amount: float):
        self.key = key
        self.secret = secret
        self.btc_amount = btc_amount
        self._recent_btc_high_in_pennies: int = -1
        self._strike_price_in_pennies: int = -1


    @property
    def recent_btc_high_in_pennies(self):
        return self._recent_btc_high_in_pennies

#    @recent_high.setter
#    def recent_high(self, value):
#        self._recent_high = value

    @property
    def strike_price_in_pennies(self):
        return self._strike_price_in_pennies

    @strike_price_in_pennies.setter
    def strike_price_in_pennies(self, value):
        print(f'{self} strike price in pennies: {value}')
        self._strike_price_in_pennies = value
