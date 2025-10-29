import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html


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

    # ✅ 新增：HTMX 行內編輯的股票名稱欄位
    def render_stock_name(self, record):
        url = reverse("edit_stock", args=[record["stock_id"]])
        return format_html(
            '<span hx-get="{}?fields=stock_name" hx-trigger="click" hx-target="this" hx-swap="outerHTML" style="cursor:pointer;">{}</span>',
            url,
            record["stock_name"]
        )

    def render_stock_kind(self, record):
        url = reverse("edit_stock", args=[record["stock_id"]])
        return format_html(
            '<span hx-get="{}?fields=stock_kind" hx-trigger="click" hx-target="this" hx-swap="outerHTML" style="cursor:pointer;">{}</span>',
            url,
            record["stock_kind"]
        )

    def render_stock_status(self, record):
        url = reverse("edit_stock", args=[record["stock_id"]])
        return format_html(
            '<span hx-get="{}?fields=stock_status" hx-trigger="click" hx-target="this" hx-swap="outerHTML" style="cursor:pointer;">{}</span>',
            url,
            record["stock_status"]
        )

    class Meta:
        attrs = {"class": "table table-striped table-hover"}
