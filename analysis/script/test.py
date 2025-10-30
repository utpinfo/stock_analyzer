import datetime
import json

from fugle_marketdata import RestClient

apiKey = "NmM4YzY4YmYtMDI3ZC00YjUyLTkxNjItODExZjY3OTExYjUwIGJlMzgwOTc3LTVhYTYtNDMxMS1hY2U4LTgxYzMzZmIwOWYxMw=="
client = RestClient(api_key = apiKey)
stock = client.stock
# 查詢股票
# data = stock.intraday.tickers(type='EQUITY', exchange="TWSE", isNormal=True)
# 查詢即時股價
#data = stock.intraday.quote(symbol='2330')

# 取得股票成交明細
data = stock.intraday.trades(symbol='2330')
for trade in data['data']:  # 直接用 'data'，非 data[0]
    trade['date'] = datetime.datetime.fromtimestamp(trade['time'] / 1_000_000).strftime('%Y-%m-%d %H:%M:%S')
    del trade['time']
data = json.dumps(data, ensure_ascii=False)
print(data)