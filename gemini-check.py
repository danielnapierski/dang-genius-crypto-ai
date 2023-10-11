import os

from dotenv import load_dotenv
from gemini_api.authentication import Authentication
from gemini_api.endpoints.fund_management import FundManagement

load_dotenv()

GE_API_KEY = os.environ.get('GE-API-KEY')
GE_API_SECRET = os.environ.get('GE-API-SECRET')

auth = Authentication(
    public_key=GE_API_KEY, private_key=GE_API_SECRET
)

if __name__ == "__main__":
    x = FundManagement.get_notional_balances(
        auth=auth, currency='USD'
    )
    y = x[0]
    print(getattr(y, 'amount'))
    print(getattr(y, 'currency'))
