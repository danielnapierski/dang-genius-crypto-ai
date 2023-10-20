import time
from pprint import pprint
from dang_genius.market import market_check as mc
from dang_genius.wallet import check_swap_funding as check_swap_funding
import dang_genius.util as util
from dang_genius.conductor import Conductor


def bot() -> None:
    conductor = Conductor()
    max_spread: float = 0.0
    while True:
        opportunity = mc(conductor.fee_estimate)
        if opportunity:
            buy_ex = opportunity.get(util.BUY_KEY)
            sell_ex = opportunity.get(util.SELL_KEY)
            spread = opportunity.get(util.SPREAD_KEY)
            if spread and spread > max_spread:
                max_spread = spread
                print(f'Max Spread: {max_spread:.2f}')

            if buy_ex and sell_ex:
#TODO: FIX
                funded = check_swap_funding(buy_ex, 'USD', conductor.usd_amount,
                                            sell_ex, 'BTC', conductor.btc_amount)
                if not funded:
                    funded = True
                    print('ATTEMPTING WITHOUT FUNDS')

                if funded:
                    conductor.buy_btc_sell_btc(buy_ex, sell_ex)
                else:
                    print('Insuffiecient funds.')
        time.sleep(5)
