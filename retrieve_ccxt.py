import ccxt
import time
import sqlite3

conn = sqlite3.connect('trade.db')
market_places = []
market_places.append(ccxt.bitfinex())

msec = 1000
minute = 60 * msec
hold = 30

# exchange = ccxt.bitfinex()

for exchange in market_places:
    exchange.load_markets()
    print(exchange.symbols)
    delay = 10
    # for symbol in exchange.symbols:
    #     orderbook = exchange.fetch_order_book (symbol, {
    #     'limit_bids': 1, 
    #     'limit_asks': 1 
    #     })
    #     bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
    #     ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
    #     spread = (ask - bid) if (bid and ask) else None
    #     print (exchange.id, symbol, 'market price', { 'bid': bid, 'ask': ask, 'spread': spread })
    #     time.sleep (delay)

    for symbol in exchange.symbols:
        from_datetime = '2018-01-01 00:00:00'
        from_timestamp = exchange.parse8601(from_datetime)
        now = exchange.milliseconds()
        data = []
        while from_timestamp < now:
            try:
                print(exchange.milliseconds(), 'Fetching candles starting from', exchange.iso8601(from_timestamp))
                ohlcvs = exchange.fetch_ohlcv(symbol, '1m', from_timestamp)
                print(exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')
                for x in ohlcvs:
                    conn.execute("INSERT INTO history_bitfinex VALUES ('"+ symbol +"', '" + str(x[0]) + "','"+str(x[1])+"','"+str(x[2])+"','"+str(x[3])+"','"+str(x[4])+"','"+str(x[5])+"')")
                conn.commit()
                first = ohlcvs[0][0]
                last = ohlcvs[-1][0]
                print('First candle epoch', first, exchange.iso8601(first))
                print('Last candle epoch', last, exchange.iso8601(last))
                from_timestamp += len(ohlcvs) * minute * 1
                data += ohlcvs
                time.sleep (delay)

            except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:

                print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
                time.sleep (delay)