import pprint

import coinbasepro as cbp
import krakenex
from gemini_api.endpoints.public import Public
from requests.exceptions import HTTPError

kraken = krakenex.API()
kraken_pair: str = 'XXBTZUSD'
coinbase = cbp.PublicClient()
gemini = Public()

try:
    recentTrades = kraken.query_public('Trades', {'pair': kraken_pair})
    print('Kraken BTC\nLast:')
    pprint.pprint(recentTrades.get('result').get(kraken_pair)[0][0])

    kraken_public_result = (
        kraken.query_public('Depth', {'pair': kraken_pair, 'count': '10'}).get('result').get(kraken_pair))
    print('Ask:')
    pprint.pprint(kraken_public_result.get('asks')[0][0])
    print('Bid:')
    pprint.pprint(kraken_public_result.get('bids')[0][0])

    print('\n')
    print('Coinbase BTC\nLast:')
    print('TODO')
    print('Ask:')
    cb_order_book = coinbase.get_product_order_book('BTC-USD')
    pprint.pprint(cb_order_book.get('asks')[0][0])
    print('Bid:')
    pprint.pprint(cb_order_book.get('bids')[0][0])

    print('\n')
    print('Gemini BTC\nLast:')
    ge_ticker = gemini.get_ticker('BTCUSD')
    print(ge_ticker.get('last'))
    print('Ask:')
    print(ge_ticker.get('ask'))
    print('Bid:')
    print(ge_ticker.get('bid'))

except HTTPError as e:
    print(str(e))
