import krakenex
from dotenv import load_dotenv
import os
load_dotenv()

KR_API_KEY = os.environ.get('KR-API-KEY')
KR_API_SECRET = os.environ.get('KR-API-SECRET')

k = krakenex.API(KR_API_KEY, KR_API_SECRET)

print(k.query_private('Balance'))
