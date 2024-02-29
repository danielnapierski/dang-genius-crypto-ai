from datetime import datetime
from zoneinfo import ZoneInfo
from string import ascii_letters, digits

from dang_genius.exchange import Exchange

TZ_UTC: ZoneInfo = ZoneInfo("UTC")
DB_NAME = "dang_genius_crypto.db"
BUY_KEY: str = 'BUY_BTC_HERE_SPENDING_USD'
SELL_KEY: str = 'SELL_BTC_HERE_RECEIVING_USD'
MSG_KEY: str = 'MESSAGE'
SPREAD_KEY: str = 'SPREAD'
MAX_BID_KEY: str = 'MAX_BID'
MIN_ASK_KEY: str = 'MIN_ASK'
ASK_KEY: str = 'ASK'
BID_KEY: str = 'BID'
BTC_USD_PAIR: str = 'BTC_USD'
ETH_USD_PAIR: str = 'ETH_USD'
ETH_BTC_PAIR: str = 'ETH_BTC'
DATETIME_FORMAT: str = '%Y-%m-%dT%H:%M:%S.%fZ'


def alphanumeric(s: str) -> str:
    return "".join([ch for ch in s if ch in (ascii_letters + digits)])


def generate_order_id(ex: Exchange):
    now = datetime.now(tz=TZ_UTC)
    name = alphanumeric(str(type(ex)))
    return f'{name}ORDER{now.strftime(DATETIME_FORMAT)}'

def time_str(date_time):
    #2021-05-31T09:59:59Z
    return date_time.strftime(DATETIME_FORMAT)