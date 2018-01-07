import krakenex
import decimal
import time


k = krakenex.API()
retrievable_pairs= ['BCHEUR', 'XXBTZEUR', 'XETHZEUR']

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

since = str(now() - 6000)


for pair in retrievable_pairs:
    lineprint(now())

    before = now()
    ret = k.query_public('OHLC', data = {'pair': pair, 'since': since, 'interval': 5})
    after = now()

    # comment out to track the same "since"
    #since = ret['result']['last']

    # TODO: don't repeat-print if list too short
    bars = ret['result'][pair]
    for b in bars[:5]:
        evo = (float(b[4]) / float(b[1]))
        print(str(evo) + '%')
    lineprint(after - before)

