import ccxt
import time
import sqlite3

conn = sqlite3.connect('trade.db')
market_places = []
market_places.append(ccxt.bitfinex())
# exchange = ccxt.bitfinex()

for exchange in market_places:
    exchange.load_markets()
    print(exchange.symbols)
    delay = exchange.rateLimit / 500
    for symbol in exchange.symbols:
        orderbook = exchange.fetch_order_book (symbol, {
        'limit_bids': 1, 
        'limit_asks': 1 
        })
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        print (exchange.id, symbol, 'market price', { 'bid': bid, 'ask': ask, 'spread': spread })
        time.sleep (delay)

    if exchange.hasFetchOHLCV:
        for symbol in exchange.markets:
            time.sleep (exchange.rateLimit / 500) # time.sleep wants seconds
            print (symbol, exchange.fetch_ohlcv (symbol, '1d')) # one day
