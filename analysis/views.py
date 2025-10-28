from django.shortcuts import render
from django.utils.html import format_html

from analysis import MySQL
from analysis.analysis_core import main
import json
import django_tables2 as tables

class StockTable(tables.Table):
    stock_id = tables.Column(verbose_name="ID", visible=False)
    stock_code = tables.Column(verbose_name="股票代號")
    stock_name = tables.Column(verbose_name="股票名稱")
    stock_kind = tables.Column(verbose_name="市場別")
    stock_status = tables.Column(verbose_name="狀態")

    # 導航按鈕
    action = tables.Column(verbose_name="操作", empty_values=(), orderable=False)

    def render_action(self, record):
        # record 是該列的 dict
        url = f"/analysis?stockCode={record['stock_code']}"  # 你可以換成實際 URL
        return format_html(
            '<a href="{}" class="btn btn-primary btn-sm">前往</a>', url
        )

    class Meta:
        attrs = {"class": "table table-striped table-hover"}

def home(request):
    return stocks(request)
def stocks(request):
    stock_code = request.GET.get('stockCode')
    stock_code = [str(stock_code)] if stock_code else None
    stock_status = request.GET.get('stockStatus')
    stock_status = str(stock_status) if stock_status else 90

    data = MySQL.get_stock(stock_status=stock_status, stock_code=stock_code)  # 股票列表
    # data = json.dumps(data, ensure_ascii=False, default=str)
    table = StockTable(data)
    return render(request, 'analysis/stocks.html', {'table': table})


def stock_detail(request, id):
    # 假資料
    stock = {'id': id, 'name': 'AAPL', 'price': 150}
    return render(request, 'analysis/stock_detail.html', {'stock': stock})


# http://127.0.0.1:8000/?stockCode=6176
def analysis(request):
    stock_code = request.GET.get('stockCode', '6176')
    analyseDays = request.GET.get('analyseDays', 90)
    print(analyseDays);
    df = main(stock_code, int(analyseDays))

    if df.empty:
        return render(request, 'analysis/analysis.html', {
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

    return render(request, 'analysis/analysis.html', {
        'data': df.to_json(orient='records', date_format='iso'),
        'stockCode': stockCode,
        'stockName': stockName,
        'analyseDays': analyseDays,
    })
