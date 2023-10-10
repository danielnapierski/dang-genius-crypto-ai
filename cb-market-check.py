import pprint
#pprint.pprint('TODO: show last trade, bid and ask at coinbase')
import coinbasepro as cbp
public_client = cbp.PublicClient()

# Get the order book at the default level.
pprint.pprint(public_client.get_product_order_book('BTC-USD'))
# Get the order book at a specific level.
public_client.get_product_order_book('BTC-USD', level=1)
# Get the product ticker for a specific product.
public_client.get_product_ticker(product_id='ETH-USD')
# Get the product trades for a specific product.
# Returns a generator
public_client.get_product_trades(product_id='ETH-USD')
