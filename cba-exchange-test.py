import os
import pprint

from coinbase import jwt_generator
from dotenv import load_dotenv

from dang_genius.coinbaseadvancedexchange import CoinbaseAdvancedExchange

load_dotenv()

CBA_API_KEY = os.environ.get('CBA-API-KEY')
CBA_API_SECRET = os.environ.get('CBA-API-SECRET')

cbae = CoinbaseAdvancedExchange(os.environ.get('CBA-API-KEY'), os.environ.get('CBA-API-SECRET'))
print('\nCoinbaseAdvancedExchange')
pprint.pprint(cbae.balances)
pprint.pprint(cbae.tickers)
print()
jwt = cbae._generate_jwt()
pprint.pprint(jwt)

print('\njwt_generator')
# Get another JWT with using jwt_generator:
request_method = "GET"
request_path = "/api/v3/brokerage/accounts"
jwt_uri = jwt_generator.format_jwt_uri(request_method, request_path)
jwt2 = jwt_generator.build_rest_jwt(jwt_uri, CBA_API_KEY, CBA_API_SECRET)
pprint.pprint(jwt2)