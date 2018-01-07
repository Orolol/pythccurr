import krakenex
import decimal
import time
import datetime


k = krakenex.API()
retrievable_pairs= ['XETHZEUR']

def now():
    return decimal.Decimal(time.time())

def lineprint(msg, targetlen = 72):
    line = '-'*5 + ' '
    line += str(msg)

    l = len(line)
    if l < targetlen:
        trail = ' ' + '-'*(targetlen-l-1)
        line += trail

    print(line)
    return

since = str(now() - 2000)
dt_now = datetime.datetime.fromtimestamp(now()).strftime('%Y-%m-%d %H:%M:%S')

for pair in retrievable_pairs:
    before = now()
    ret = k.query_public('OHLC', data = {'pair': pair, 'since': since, 'interval': 1})
    after = now()

    # comment out to track the same "since"
    #since = ret['result']['last']

    # TODO: don't repeat-print if list too short
    bars = ret['result'][pair]
    last = 0
    for b in bars[:-5]:
        evo = ((float(b[4]) / float(b[1])) - 1) *100
        dt = datetime.datetime.fromtimestamp(int(b[0])).strftime('%Y-%m-%d %H:%M:%S')
        print(dt + ' From ' + b[1] + ' to ' + b[4] + ' -> ' + str(evo) + '%')
        last = float(b[4])
        # print(b)
    curr_tick = k.query_public('Ticker', data = {'pair' : pair})
    last_trade = curr_tick['result'][pair]['c'][0]
    evo = ((float(last_trade) / last) - 1) *100
    print(dt_now + ' From ' + str(last) + ' to ' + str(last_trade) + ' -> ' + str(evo) + '%')
    # print(curr_tick['result'][pair]['c'][0])

