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
SHIB_USD_PAIR: str = 'SHIB_USD'
SAMO_USD_PAIR: str = 'SAMO_USD'
GALA_USD_PAIR: str = 'GALA_USD'
FTM_USD_PAIR: str = 'FTM_USD'
BONK_USD_PAIR: str = 'BONK_USD'
AVAX_USD_PAIR: str = 'AVAX_USD'
LINK_USD_PAIR: str = 'LINK_USD'
FET_USD_PAIR: str = 'FET_USD'
DATETIME_FORMAT: str = '%Y-%m-%dT%H:%M:%S.%fZ'
TO_THE_MINUTE_FORMAT: str = '%Y-%m-%dT%H:%MZ'


def alphanumeric(s: str) -> str:
    return "".join([ch for ch in s if ch in (ascii_letters + digits)])


def generate_order_id(ex: Exchange):
    now = datetime.now(tz=TZ_UTC)
    name = alphanumeric(str(type(ex)))
    return f'{name}ORDER{now.strftime(DATETIME_FORMAT)}'


def time_str(date_time):
    # 2021-05-31T09:59:59.999999Z
    return date_time.strftime(DATETIME_FORMAT)


def time_str_to_the_minute(date_time):
    # 2021-05-31T09:59Z
    return date_time.strftime(TO_THE_MINUTE_FORMAT)


# possible parsing suggestion for minute time: 2024-03-05T18:11Z
# dt = datetime.datetime.strptime(dt_str, "%Y-%m-%dT%H:%MZ")

def get_datetime(text: str) -> datetime:
    timestamp = datetime.strptime(text, DATETIME_FORMAT)
    return timestamp
