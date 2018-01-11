import ccxt
import time
import datetime
import sqlite3
import decimal
import operator

conn = sqlite3.connect('trade.db')
market_places = []
market_places.append(ccxt.bitfinex())

delay = 2
short_delay = 1

symbols = ['ETH/USD','EOS/USD','BTC/USD','XRP/USD', 'NEO/USD', 'OMG/USD' , 'IOTA/USD', 'ZEC/USD', 'XMR/USD','DASH/USD', 'QSH/USD', 'ETC/USD']
predictions = {}
current_prices = {}
wallet = {}
wallet['USD'] = 1000
for symbol in symbols:
        wallet[symbol] = 0



def min_max_wallet(predictions, current, exchange, wallet):
    wallet_curr_value = 0
    wallet_pred_value = 0
    gain_percent = {}
    for currency in current:
        gain_percent[currency] = ((predictions[currency] - current[currency]) / current[currency]) * 100

    sorted_gain_percent = sorted(gain_percent.items(), key=operator.itemgetter(1))
    print(wallet)
    if wallet['USD'] > 0:
        print('MONEY TO USE '  , wallet['USD'])
        wallet = init_wallet(sorted_gain_percent, exchange, wallet)

    for currency in current:
        wallet_curr_value += wallet[currency] * current[currency]
        wallet_pred_value += wallet[currency] * predictions[currency]
   
    
    print('WALLET :', wallet)
    current_gain =  wallet_pred_value -  wallet_curr_value
    print("WALLET VALUE", wallet_curr_value, "PREDICTED ", wallet_pred_value, " Woot !", current_gain)

    for tuples in sorted_gain_percent:
        if(wallet[tuples[0]] > 0 and sorted_gain_percent[-1][1] - tuples[1] > 2.5): 
            print("trying to sell ", tuples[0] , tuples[1],  " for ", sorted_gain_percent[-1])

            orderbook = exchange.fetch_order_book (tuples[0], {
            'limit_bids': 1, 
            'limit_asks': 1 
            })
            
            bid_sell = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
            ask_sell = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
            print("SELL ", tuples[0] , " for ", bid_sell, ' ask :', ask_sell  )
            wallet['USD'] += (wallet[tuples[0]] * bid_sell) * 0.998
            wallet[tuples[0]] = 0
            time.sleep (delay)
            orderbook = exchange.fetch_order_book (sorted_gain_percent[-1][0], {
            'limit_bids': 1, 
            'limit_asks': 1 
            })
            ask_sell = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
            bid_sell = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
            print("BUY  ", sorted_gain_percent[-1][0] , " for ", ask_sell, ' bid :', bid_sell  )
            wallet[sorted_gain_percent[-1][0]] += (wallet['USD'] * 0.998) / ask_sell
            wallet['USD'] = 0
            print('New Wallet State :', wallet, 'current value : ', get_wallet_value(current, wallet), 'predicted value : ', get_wallet_value(predictions, wallet))
            time.sleep (delay)
    
    for currency in current:
        wallet_curr_value += wallet[currency] * current[currency]
        wallet_pred_value += wallet[currency] * predictions[currency]
    gain_percent[currency] = ((predictions[currency] - current[currency]) / current[currency]) * 100 
    

def init_wallet(sorted_gain_percent, exchange, wallet):

    time.sleep (delay)
    orderbook = exchange.fetch_order_book (sorted_gain_percent[-1][0], {
    'limit_bids': 1, 
    'limit_asks': 1 
    })
    ask_sell = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
    bid_sell = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
    print("BUY  ", sorted_gain_percent[-1][0] , " for ", ask_sell, ' bid :', bid_sell  )
    wallet[sorted_gain_percent[-1][0]] += (wallet['USD'] * 0.998) / ask_sell
    wallet['USD'] = 0

    return wallet



def get_wallet_value(prices, wallet):
    value = 0
    for currency in prices:
        value += wallet[currency] * prices[currency]
    return value

def eval_wallet(predictions, new_wallet):
    score = 0
    if get_wallet_value(predictions, new_wallet) > get_wallet_value(predictions, wallet):
        return 1
    else:
        return 0


def predict_price(history_duration, future_duration):
    from_timestamp = (time.time()) - history_duration * 60
    print(wallet)
    for exchange in market_places:
        exchange.load_markets()
        for symbol in symbols:
            ohlcvs = exchange.fetch_ohlcv(symbol, '1m', from_timestamp * 1000)
            if(len(ohlcvs) > 0):
                if(len(ohlcvs) < history_duration):
                    history_duration = len(ohlcvs)
                mean_CVPMS = 0;
                last_price = ohlcvs[-1][4]
                first_price = ohlcvs[0][1]
                for x in ohlcvs:
                    current = x[1]
                    last = x[4]
                    change_value_per_ms = (x[4] - x[1]) / 60
                    mean_CVPMS += change_value_per_ms
                    # print('CVPMS', change_value_per_ms)
                    # print(datetime.datetime.fromtimestamp(x[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'), current, last, ' evo ', ((last / current) * 100 ) - 100, '%' )
                mean_CVPMS = mean_CVPMS / len(ohlcvs)
                total_change = last_price - first_price
                # print('OPEN PRICE', ohlcvs[0][1])
                # print('CLOSE PRICE', ohlcvs[-5][4])
                # print('MEAN CVPMS', mean_CVPMS)
                # print('total_change', total_change)

                # print('CLOSING LAST CANDLE PRICE', ohlcvs[-1][4])
                if(total_change > 0):
                    predicted_price = last_price + ((mean_CVPMS * 60) * future_duration)

                if(total_change < 0):
                    predicted_price = last_price + ((mean_CVPMS * 60) * future_duration)

                if(total_change == 0):
                    predicted_price = last_price

                mean_price_last_5m = 0
                for z in ohlcvs[-6:-1]:
                    mean_price_last_5m += z[4]
                mean_price_last_5m = mean_price_last_5m / 5

                print(symbol, ' FPRICE :', first_price , ' LPRICE :', last_price , 'PREDICTION:', predicted_price , ' variation : ', ((predicted_price - last_price ) / last_price ) * 100 , '%')
                current_prices[symbol] = last_price
                predictions[symbol] = predicted_price
            else:
                print("NO DATA FOR ", symbol)
            time.sleep (delay)
        min_max_wallet(predictions, current_prices, exchange, wallet)


# init_wallet()
# predict_price(60,60)
# predict_price(10,10)


while True:
    predict_price(10,10)
    time.sleep (300)