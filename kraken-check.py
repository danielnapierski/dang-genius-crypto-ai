import os
import pprint

import krakenex
from dotenv import load_dotenv

load_dotenv()

KR_API_KEY = os.environ.get('KR-API-KEY')
KR_API_SECRET = os.environ.get('KR-API-SECRET')

k = krakenex.API(KR_API_KEY, KR_API_SECRET)
b = k.query_private('Balance')
pprint.pprint(b['result'])
