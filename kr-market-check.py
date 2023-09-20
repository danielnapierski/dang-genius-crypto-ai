from requests.exceptions import HTTPError

import krakenex

import pprint

kraken = krakenex.API()

try:
    response = kraken.query_public('Depth', {'pair': 'XXBTZUSD', 'count': '10'})
    pprint.pprint(response)
except HTTPError as e:
    print(str(e))
