from django.shortcuts import render
from analysis.analysis_core import main


def stock_list(request):
    # 假資料
    stocks = [
        {'id': 1, 'name': 'AAPL'},
        {'id': 2, 'name': 'TSLA'}
    ]
    return render(request, 'analysis/stock_list.html', {'stocks': stocks})


def stock_detail(request, id):
    # 假資料
    stock = {'id': id, 'name': 'AAPL', 'price': 150}
    return render(request, 'analysis/stock_detail.html', {'stock': stock})

# http://127.0.0.1:8000/?stockCode=6176
def home(request):
    stock_code = request.GET.get('stockCode', '6176')
    analyseDays = request.GET.get('analyseDays', 90)
    print(analyseDays);
    df = main(stock_code, int(analyseDays))

    if df.empty:
        return render(request, 'analysis/home.html', {
            'data': '[]',
            'stockCode': '',
            'stockName': '無資料',
            'analyseDays': analyseDays,
            'signals': [],
            'alert_msg': f"股票 {stock_code} 查無資料"  # 新增 alert_msg
        })

    # 安全取出第一筆 stockCode 和 stockName
    stockCode = str(df['stockCode'].iloc[0])
    stockName = str(df['stockName'].iloc[0])

    return render(request, 'analysis/home.html', {
        'data': df.to_json(orient='records', date_format='iso'),
        'stockCode': stockCode,
        'stockName': stockName,
        'analyseDays': analyseDays,
    })
