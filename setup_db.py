import sqlite3
conn = sqlite3.connect('trade.db')

conn.execute('''CREATE TABLE history_bitfinex
             (symbol text, date text, open text, high text, low text, close text, volume text)''')

conn.commit()             