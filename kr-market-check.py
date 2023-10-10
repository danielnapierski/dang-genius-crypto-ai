from requests.exceptions import HTTPError

import krakenex

import pprint

kraken = krakenex.API()

try:

    # Get a list of the most recent trades
#{'error': [],
# 'result': {'XXBTZUSD': [['26202.00000',

    recentTrades = kraken.query_public('Trades',{'pair': 'XXBTZUSD'})
    dir(recentTrades)
    print('Kraken BTC\nLast:')
    pprint.pprint(recentTrades.get('result').get('XXBTZUSD')[0][0])

    response = kraken.query_public('Depth', {'pair': 'XXBTZUSD', 'count': '10'})
    print('Ask:')
    pprint.pprint(response.get('result').get('XXBTZUSD').get('asks')[0][0])
    print('Bid:')
    pprint.pprint(response.get('result').get('XXBTZUSD').get('bids')[0][0])
except HTTPError as e:
    print(str(e))
