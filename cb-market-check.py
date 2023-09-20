import json
import time
import hmac
import hashlib
from threading import Thread
from websocket import create_connection, WebSocketConnectionClosedException
from dotenv import load_dotenv
import os
load_dotenv()

def main():
    ws = None
    thread = None
    thread_running = False
    thread_keepalive = None

    def websocket_thread():
        global ws

        api_key = os.environ.get('CB-API-KEY')
        api_secret = os.environ.get('CB-API-SECRET')

        channel = "level2"
        timestamp = str(int(time.time()))
        product_ids = ["BTC-USD"]
        product_ids_str = ",".join(product_ids)
        message = f"{timestamp}{channel}{product_ids_str}"
        signature = hmac.new(api_secret.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()

        ws = create_connection("wss://advanced-trade-ws.coinbase.com")
        ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": [
                        "BTC-USD",
                    ],
                    "channel": channel,
                    "api_key": api_key,
                    "timestamp": timestamp,
                    "signature": signature,
                }
            )
        )

        thread_keepalive.start()
        while not thread_running:
            try:
                data = ws.recv()
                if data != "":
                    msg = json.loads(data)
                else:
                    msg = {}
            except ValueError as e:
                print(e)
                print("{} - data: {}".format(e, data))
            except Exception as e:
                print(e)
                print("{} - data: {}".format(e, data))
            else:
                if "result" not in msg:
                    print(f'MESSAGE: {msg}')

        try:
            if ws:
                ws.close()
        except WebSocketConnectionClosedException:
            pass
        finally:
            thread_keepalive.join()

    def websocket_keepalive(interval=30):
        global ws
        while ws.connected:
            ws.ping("keepalive")
            time.sleep(interval)

    thread = Thread(target=websocket_thread)
    thread_keepalive = Thread(target=websocket_keepalive)
    thread.start()


if __name__ == "__main__":
    main()
