import time
from dang_genius.market import market_check as mc
from dang_genius.wallet import check_swap_funding as check_swap_funding
import dang_genius.util as dgu
from dang_genius.conductor import Conductor

def bot() -> None:
    conductor = Conductor()
    print('Are you ready to rumble?')
    input_text = input()
    print(input_text)
# TODO: add go/no go

    conductor.buy_the_dip(dgu.BTC_USD_PAIR)
    conductor.buy_the_dip(dgu.ETH_USD_PAIR)
    #    conductor.take_the_win()

    max_spread: float = 0.0
    while True:
        opportunity = mc(conductor.fee_estimate)
        if opportunity:
            buy_ex = opportunity.get(dgu.BUY_KEY)
            sell_ex = opportunity.get(dgu.SELL_KEY)
            spread = opportunity.get(dgu.SPREAD_KEY)
            min_ask = opportunity.get(dgu.MIN_ASK_KEY)
            max_bid = opportunity.get(dgu.MAX_BID_KEY)

            if spread and spread > max_spread:
                max_spread = spread
                print(f'\nMax Spread: {max_spread:.2f}')

            if buy_ex and sell_ex:
                funded = check_swap_funding(buy_ex, 'USD', conductor.usd_amount,
                                            sell_ex, 'BTC', conductor.btc_amount)

                if funded:
                    conductor.buy_btc_sell_btc(buy_ex, sell_ex, min_ask, max_bid)
                else:
                    print('MISSED! Not enough funds.')
        time.sleep(0.5)
