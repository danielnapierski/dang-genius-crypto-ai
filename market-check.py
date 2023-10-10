from requests.exceptions import HTTPError
import coinbasepro as cbp
import krakenex
import pprint
from gemini_api.endpoints.public import Public
kraken = krakenex.API()
coinbase = cbp.PublicClient()
gemini = Public()

try:

    recentTrades = kraken.query_public('Trades',{'pair': 'XXBTZUSD'})
    dir(recentTrades)
    print('Kraken BTC\nLast:')
    pprint.pprint(recentTrades.get('result').get('XXBTZUSD')[0][0])

    response = kraken.query_public('Depth', {'pair': 'XXBTZUSD', 'count': '10'})
    print('Ask:')
    pprint.pprint(response.get('result').get('XXBTZUSD').get('asks')[0][0])
    print('Bid:')
    pprint.pprint(response.get('result').get('XXBTZUSD').get('bids')[0][0])

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

