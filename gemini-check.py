from gemini_api.endpoints.fund_management import FundManagement
from gemini_api.authentication import Authentication
from dotenv import load_dotenv
import os
load_dotenv()


GE_API_KEY = os.environ.get('GE-API-KEY')
GE_API_SECRET = os.environ.get('GE-API-SECRET')

auth = Authentication(
    public_key=GE_API_KEY, private_key=GE_API_SECRET
)

if __name__ == "__main__":
    x = FundManagement.get_available_balances(
        auth=auth
    )
    y = x[0]
    print(dir(y))
    print(getattr(y,'amount'))
