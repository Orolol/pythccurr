import ccxt
import time
import datetime
import sqlite3
import decimal

conn = sqlite3.connect('trade.db')
market_places = []
market_places.append(ccxt.bitfinex())

delay = 2
short_delay = 1

symbols = ['ETH/USD','EOS/USD','BTC/USD','XRP/USD']
predictions = {}
current_prices = {}
wallet = {}

def min_max_wallet(predictions, current):
    wallet_curr_value = 0
    wallet_pred_value = 0
    for currency in current:
        wallet_curr_value += wallet[currency] * current[currency]
        wallet_pred_value += wallet[currency] * predictions[currency]
    current_gain =  wallet_pred_value -  wallet_curr_value
    print("WALLET VALUE", wallet_curr_value, "PREDICTED ", wallet_pred_value, " Woot !", current_gain)



def init_wallet():
    wallet['ETH/USD'] = 30
    wallet['XRP/USD'] = 2000
    wallet['EOS/USD'] = 1000
    wallet['BTC/USD'] = 1
        

init_wallet()




from_timestamp = (time.time()) - 7200
print(datetime.datetime.fromtimestamp(from_timestamp).strftime('%Y-%m-%d %H:%M:%S'))
# exchange = ccxt.bitfinex()

for exchange in market_places:
    exchange.load_markets()
    for symbol in symbols:
        ohlcvs = exchange.fetch_ohlcv(symbol, '1m', from_timestamp * 1000)
        print(symbol)
        mean_CVPMS = 0;
        last_price = ohlcvs[-60][4]
        first_price = ohlcvs[0][1]
        for x in ohlcvs[0:-60]:
            current = x[1]
            last = x[4]
            change_value_per_ms = (x[4] - x[1]) / 60
            mean_CVPMS += change_value_per_ms
            # print('CVPMS', change_value_per_ms)
            # print(datetime.datetime.fromtimestamp(x[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'), current, last, ' evo ', ((last / current) * 100 ) - 100, '%' )
        mean_CVPMS = mean_CVPMS / len(ohlcvs)
        total_change = ohlcvs[-1][4] - ohlcvs[0][1]
        # print('OPEN PRICE', ohlcvs[0][1])
        # print('CLOSE PRICE', ohlcvs[-5][4])
        # print('MEAN CVPMS', mean_CVPMS)
        # print('total_change', total_change)
        time.sleep (short_delay)
        orderbook = exchange.fetch_order_book (symbol, {
        'limit_bids': 1, 
        'limit_asks': 1 
        })
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        print (exchange.id, symbol, 'market price', { 'bid': bid, 'ask': ask, 'spread': spread })

        # print('CLOSING LAST CANDLE PRICE', ohlcvs[-1][4])
        if(total_change > 0):
            predicted_price = last_price + ((mean_CVPMS * 60) * 60)

        if(total_change < 0):
            predicted_price = last_price - ((mean_CVPMS * 60) * 60)

        mean_price_last_5m = 0
        for z in ohlcvs[-6:-1]:
            mean_price_last_5m += z[4]
        mean_price_last_5m = mean_price_last_5m / 5

        print('START PRICE :', first_price , 'BOLD PREDICTION:', predicted_price, ' | REALITY:' , ohlcvs[-1][4] , ' Error : ', (((ohlcvs[-1][4] ) / (predicted_price )) * 100) -100 , '%')
        print('START PRICE :', first_price , 'BOLD PREDICTION:', predicted_price, ' | mean_price_last_5m:' , mean_price_last_5m , ' Error : ', (((mean_price_last_5m ) / (predicted_price)) * 100) -100 , '%')
        current_prices[symbol] = ohlcvs[-1][4]
        predictions[symbol] = predicted_price
       
        time.sleep (delay)
    print("1 hour predictions ", predictions)
    min_max_wallet(predictions, current_prices)


