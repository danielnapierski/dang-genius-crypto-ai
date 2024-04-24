#!python3
import pprint
import asyncio, base64, hashlib, hmac, json, os, time, websockets

import coinbasepro as cbp
from coinbase import jwt_generator
from dotenv import load_dotenv
import json
import os
import ssl

import asyncio
import websockets

import websocket
from rich.json import JSON

public_client = cbp.PublicClient()

# Get the order book at the default level.
pprint.pprint(public_client.get_product_order_book("BTC-USD"))
# Get the order book at a specific level.
public_client.get_product_order_book("BTC-USD", level=1)
# Get the product ticker for a specific product.
public_client.get_product_ticker(product_id="ETH-USD")
# Get the product trades for a specific product.
# Returns a generator
public_client.get_product_trades(product_id="ETH-USD")


import asyncio
import websockets

async def hello(uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
        "type": "subscribe",
        "product_ids": [
            "ETH-USD",
            "BTC-USD"
        ],
        "channels": ["ticker"]
    }))
        while True:
            greeting = await websocket.recv()
            print(f"Received: {greeting}")

asyncio.run(hello('wss://ws-feed.exchange.coinbase.com'))


#ws = websocket.WebSocketApp('wss://ws-feed.exchange.coinbase.com')
#x = ws.send(json.dumps({
#        "type": "subscribe",
#        "product_ids": [
#            "ETH-USD",
#            "BTC-USD"
#        ],
#        "channels": ["ticker"]
#    }))
#pprint.pprint(x)

time.sleep(10)

#ws = websocket.WebSocketApp(
#    "wss://api.gemini.com/v1/marketdata/ethusd?top_of_book=true&bids=true",
#    "wss://api.gemini.com/v1/multimarketdata?top_of_book=true&symbols=BTCUSD,ETHUSD",
#    on_message=on_message,
#)
#wss://api.gemini.com/v1/multimarketdata?symbols=BTCUSD,ETHUSD

#ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
