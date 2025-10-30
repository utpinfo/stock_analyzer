from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from analysis.script import MySQL
from analysis.script.analysis_core import main
from analysis.table import StockTable


def home(request):
    return stocks(request)


def stocks(request):
    stock_code = request.GET.get('stockCode')
    stock_code = [str(stock_code)] if stock_code else None
    stock_status = request.GET.get('stockStatus')
    stock_name = request.GET.get('stockName')

    data = MySQL.get_stock(stock_status=stock_status, stock_code=stock_code, stock_name=stock_name)
    # data = data[:3000]  # 限制最大筆數
    page_size = 30
    table = StockTable(data)
    paginator = Paginator(data, page_size)

    page_number = request.GET.get("page", "1")

    page_obj = paginator.get_page(page_number)

    table.paginate(page=page_obj.number, per_page=page_size)

    return render(request, 'analysis/stocks.html', {
        'table': table,
        'page_obj': page_obj,
    })


def edit_stock(request, stock_id):
    stock = MySQL.get_stock(stock_id=stock_id, stock_status=None)
    if not stock:
        return HttpResponse("Not found", status=404)
    stock = stock[0]

    fields = request.GET.getlist("fields") or ["stock_name"]

    # 把欄位和值組成 tuple 列表
    field_values = [(f, stock[f]) for f in fields]
    # ✅ 傳入 request，才能讓模板裡的 {% csrf_token %} 正常工作
    html = render_to_string("analysis/edit_stock.html", {
        "field_values": field_values,
        "stock_id": stock_id
    }, request=request)
    return HttpResponse(html)


def update_stock(request, stock_id):
    if request.method != "POST":
        return HttpResponse(status=405)

    # 取得前端送來的欄位與值
    fields = request.POST.dict()
    fields.pop("csrfmiddlewaretoken", None)  # 移除 CSRF
    if not fields:
        return HttpResponse("No data to update", status=400)

    # 更新資料庫
    MySQL.update_stock(stock_id, **fields)  # ✅ 注意 **fields

    # 更新後的單筆資料
    updated_stock = MySQL.get_stock(stock_id=stock_id, stock_status=None)[0]

    # 回傳新的 span，用於 HTMX 替換
    field = list(fields.keys())[0]  # 假設一次只更新一個欄位
    url = reverse("edit_stock", args=[stock_id])
    html = f'<span hx-get="{url}" hx-trigger="click" hx-target="this" hx-swap="outerHTML" style="cursor:pointer;">{updated_stock[field]}</span>'
    # return HttpResponse(html)
    return HttpResponse(status=204)


# http://127.0.0.1:8000/?stockCode=6176
def analysis(request):
    stock_code = request.GET.get('stockCode', '6176')
    analyseDays = request.GET.get('analyseDays', 90)
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


def opportunity():
    print(123)
