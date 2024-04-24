#!python3
import os
import pprint
import time

from dotenv import load_dotenv

from dang_genius.geminiexchange import GeminiExchange

load_dotenv()

ge = GeminiExchange(os.environ.get("GE-API-KEY"), os.environ.get("GE-API-SECRET"))

print("\nGeminiExchange")
pprint.pprint(ge.balances)
pprint.pprint(ge.tickers)





# Not using gemini_api anymore as the nonce was not configurable.
# import os
# from typing import List

# from dotenv import load_dotenv
# from gemini_api.authentication import Authentication
# from gemini_api.endpoints.fund_management import FundManagement

# load_dotenv()

# GE_API_KEY = os.environ.get('GE-API-KEY')
# GE_API_SECRET = os.environ.get('GE-API-SECRET')

# auth = Authentication(
#    public_key=GE_API_KEY, private_key=GE_API_SECRET
# )

# if __name__ == "__main__":
#    account : List[str] = ["primary"]
#    path = "/v1/balances"
#    res = auth.make_request(endpoint=path, payload={"account": account})
#    print(f'res: {res}')

#    balances = FundManagement.get_available_balances(auth)
#    print(f'balances: {balances}')
#    x = FundManagement.get_notional_balances(
#        auth=auth, currency='USD'
#    )
#    y = x[0]
#    print(getattr(y, 'amount'))
#    print(getattr(y, 'currency'))
