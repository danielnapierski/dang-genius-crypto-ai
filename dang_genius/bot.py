import time
from pprint import pprint
from dang_genius.market import market_check as mc
from dang_genius.wallet import check_swap_funding as check_swap_funding
from dang_genius.util import BUY_BTC_HERE_SPENDING_USD as BUY_KEY
from dang_genius.util import SELL_BTC_HERE_RECEIVING_USD as SELL_KEY
from dang_genius.conductor import buy_btc_using_usd_and_sell_btc_for_usd as do_it


def bot() -> None:
    while True:
        opportunity = mc()
        if opportunity:
            pprint(opportunity)
            buy_ex = opportunity.get(BUY_KEY)
            sell_ex = opportunity.get(SELL_KEY)

            if buy_ex and sell_ex:
                funded = check_swap_funding(buy_ex, 'USD', 1000.0, sell_ex, 'BTC', 0.03)
                if funded:
                    do_it(buy_ex, 0.03, sell_ex, 0.03)
                else:
                    print('Insuffiecient funds.')
        time.sleep(5)
