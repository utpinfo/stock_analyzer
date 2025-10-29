from datetime import datetime, timedelta

import yfinance as yf

from analysis.script import MySQL, YahooStockInfo


# 獲取3年股價/成交量
def DailySchedule(stock_kind, stock_code, isin_code,
                  start_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")):
    # start_date = "2023-03-01"
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    data = MySQL.get_price(stock_code, None, 'asc', start_date, end_date)
    msg = f"stock_code:{stock_code}, isin_code:{isin_code}, start_date:{start_date}, end_date:{end_date}, DB:{len(data)}"
    print(msg)
    # rows = yf.Ticker(isin_code).history(start=start_date, end=end_date)
    stock_code_yf = f"{stock_code}.TWO" if stock_kind == '上櫃' else f"{stock_code}.TW"

    rows = yf.Ticker(stock_code_yf).history(start=start_date, end=end_date)
    rows[['Close', 'Open', 'High', 'Low']] = rows[['Close', 'Open', 'High', 'Low']].fillna(0)
    for date, row in rows.iterrows():
        price_date = str(date.date())
        # print(f"日期: {price_date}, 收盤價: {round(row['Close'], 2)}, 成交量: {row['Volume']}")
        MySQL.add_price(stock_code, price_date, row['Open'], row['Close'], row['High'], row['Low'], row['Volume'])


def MonthlySchedule(code):
    # r = YahooStockInfo.get_revenue(code)
    rows = YahooStockInfo.get_revenue(code)
    if rows:
        for row in rows:
            MySQL.add_revenue(code, row['date'], row['price'].replace(",", ""))


def QuarterlySchedule(code):
    # r = YahooStockInfo.get_revenue(code)
    rows = YahooStockInfo.get_eps(code)
    if rows:
        for row in rows:
            MySQL.add_eps(code, row['date'], row['price'].replace(",", ""))