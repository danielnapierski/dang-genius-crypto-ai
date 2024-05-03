from datetime import datetime
from zoneinfo import ZoneInfo
from string import ascii_letters, digits

from dang_genius.exchange import Exchange

TZ_UTC: ZoneInfo = ZoneInfo("UTC")
DB_NAME = "dang_genius_crypto.db"
BUY_KEY: str = "BUY_BTC_HERE_SPENDING_USD"
SELL_KEY: str = "SELL_BTC_HERE_RECEIVING_USD"
MSG_KEY: str = "MESSAGE"
SPREAD_KEY: str = "SPREAD"
MAX_BID_KEY: str = "MAX_BID"
MIN_ASK_KEY: str = "MIN_ASK"
ASK_KEY: str = "ASK"
BID_KEY: str = "BID"
BTC_USD_PAIR: str = "BTC_USD"
ETH_USD_PAIR: str = "ETH_USD"
ETH_BTC_PAIR: str = "ETH_BTC"
#
ABT_USD_PAIR: str = "ABT_USD"
ADA_USD_PAIR: str = "ADA_USD"
AERO_USD_PAIR: str = "AERO_USD"
AIOZ_USD_PAIR: str = "AIOZ_USD"
ALEPH_USD_PAIR: str = "ALEPH_USD"
ALGO_USD_PAIR: str = "ALGO_USD"
ALI_USD_PAIR: str = "ALI_USD"
ALPHA_USD_PAIR: str = "ALPHA_USD"
AMP_USD_PAIR: str = "AMP_USD"
APT_USD_PAIR: str = "APT_USD"
ATOM_USD_PAIR: str = "ATOM_USD"
AUDIO_USD_PAIR: str = "AUDIO_USD"
AVAX_USD_PAIR: str = "AVAX_USD"
AXS_USD_PAIR: str = "AXS_USD"
BAT_USD_PAIR: str = "BAT_USD"
BDAG_USD_PAIR: str = "BDAG_USD_PAIR"
BLUR_USD_PAIR: str = "BLUR_USD"
BONK_USD_PAIR: str = "BONK_USD"
CHZ_USD_PAIR: str = "CHZ_USD"
COMP_USD_PAIR: str = "COMP_USD"
CRV_USD_PAIR: str = "CRV_USD"
CTX_USD_PAIR: str = "CTX_USD"
CUBE_USD_PAIR: str = "CUBE_USD"
DOGE_USD_PAIR: str = "DOGE_USD"
DOT_USD_PAIR: str = "DOT_USD"
ENS_USD_PAIR: str = "ENS_USD"
FET_USD_PAIR: str = "FET_USD"
FIL_USD_PAIR: str = "FIL_USD"
FLR_USD_PAIR: str = "FLR_USD"
FTM_USD_PAIR: str = "FTM_USD"
GALA_USD_PAIR: str = "GALA_USD"
GMT_USD_PAIR: str = "GMT_USD"
GRT_USD_PAIR: str = "GRT_USD"
HBAR_USD_PAIR: str = "HBAR_USD"
HNT_USD_PAIR: str = "HNT_USD"
IMX_USD_PAIR: str = "IMX_USD"
INJ_USD_PAIR: str = "INJ_USD"
IOTX_USD_PAIR: str = "IOTX_USD"
JUP_USD_PAIR: str = "JUP_USD"
KNC_USD_PAIR: str = "KNC_USD"
LDO_USD_PAIR: str = "LDO_USD"
LINK_USD_PAIR: str = "LINK_USD"
LPT_USD_PAIR: str = "LPT_USD"
LRC_USD_PAIR: str = "LRC_USD"
MANA_USD_PAIR: str = "MANA_USD"
MATIC_USD_PAIR: str = "MATIC_USD"
MKR_USD_PAIR: str = "MKR_USD"
NEAR_USD_PAIR: str = "NEAR_USD" #TODO BUY!
OP_USD_PAIR: str = "OP_USD"
OXT_USD_PAIR: str = "OXT_USD"
PEPE_USD_PAIR: str = "PEPE_USD"
PHA_USD_PAIR: str = "PHA_USD"
QNT_USD_PAIR: str = "QNT_USD"
REN_USD_PAIR: str = "REN_USD"
RNDR_USD_PAIR: str = "RNDR_USD"
SAMO_USD_PAIR: str = "SAMO_USD"
SHIB_USD_PAIR: str = "SHIB_USD"
SKL_USD_PAIR: str = "SKL_USD"
SNX_USD_PAIR: str = "SNX_USD"
SOL_USD_PAIR: str = "SOL_USD"
STORJ_USD_PAIR: str = "STORJ_USD"
STRK_USD_PAIR: str = "STRK_USD"
SUI_USD_PAIR: str = "SUI_USD"
SUSHI_USD_PAIR: str = "SUSHI_USD"
UMA_USD_PAIR: str = "UMA_USD"
UNI_USD_PAIR: str = "UNI_USD"
WAXL_USD_PAIR: str = "WAXL_USD"
WCFG_USD_PAIR: str = "WCFG_USD"
XCN_USD_PAIR: str = "XCN_USD"
XTZ_USD_PAIR: str = "XTZ_USD"
XYO_USD_PAIR: str = "XYO_USD"
YFI_USD_PAIR: str = "YFI_USD"
ZBC_USD_PAIR: str = "ZBC_USD"
ZEC_USD_PAIR: str = "ZEC_USD"
ZEN_USD_PAIR: str = "ZEN_USD"
ZETA_USD_PAIR: str = "ZETA_USD"
ZRX_USD_PAIR: str = "ZRX_USD"

DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"
TO_THE_MINUTE_FORMAT: str = "%Y-%m-%dT%H:%MZ"


def alphanumeric(s: str) -> str:
    return "".join([ch for ch in s if ch in (ascii_letters + digits)])


def generate_order_id(ex: Exchange):
    now = datetime.now(tz=TZ_UTC)
    name = alphanumeric(str(type(ex)))
    return f"{name}ORDER{now.strftime(DATETIME_FORMAT)}"


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

def round_to_nearest_hundred(number):
  """Rounds an integer to the nearest hundred (200, 300, 400, etc.)"""
  return number - number % 100 + (100 if number % 100 > 50 else 0)
