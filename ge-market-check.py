#!python3
import json
import os
import ssl

import websocket
from dotenv import load_dotenv

load_dotenv()

GE_API_KEY = os.environ.get("GE-API-KEY")
GE_API_SECRET = os.environ.get("GE-API-SECRET")


def on_message(ws, message):
    message_object = json.loads(message)
    event = message_object.get("events")[0]
    side = event.get("side")
    if "bid" == side:
        print("Bid: " + event.get("price"))
    if "ask" == side:
        print("Ask: " + event.get("price"))


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


# gemini_api_key = GE_API_KEY
# gemini_api_secret = GE_API_SECRET.encode()
# payload = {"request": "/v1/order/events","nonce": time.time()}
# encoded_payload = json.dumps(payload).encode()
# b64 = base64.b64encode(encoded_payload)
# signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()
# ws = websocket.WebSocketApp("wss://api.sandbox.gemini.com/v1/order/events",
#                            on_message=on_message,
#                            header={
#                                'X-GEMINI-PAYLOAD': b64.decode(),
#                                'X-GEMINI-APIKEY': gemini_api_key,
#                                'X-GEMINI-SIGNATURE': signature
#                            })
# ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

ws = websocket.WebSocketApp(
#    "wss://api.gemini.com/v1/marketdata/ethusd?top_of_book=true&bids=true",
    "wss://api.gemini.com/v1/multimarketdata?top_of_book=true&symbols=BTCUSD,ETHUSD",
    on_message=on_message,
)
#wss://api.gemini.com/v1/multimarketdata?symbols=BTCUSD,ETHUSD

ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
