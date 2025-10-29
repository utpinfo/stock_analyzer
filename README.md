# 首次運行

1. 安裝依賴
   pip install -r requirements.txt
2. 下載股票列表
   TwseUtils.py
3. 修改狀態

```sql
update stock
set stock_status = '90'
where stock_code in ('2610', '4974', '6176');
```

測試訪問

```
 http://127.0.0.1:8000/
```
## 表格工具
1.**安裝**
```bash
pip install django-tables2
```
2.定義表格模組(table.py)

## 行內編輯
1.頁面引入 HTMX (stocks.html)
```html
<script src="https://unpkg.com/htmx.org"></script>
```
2.定義編輯函數 (views.py)
```python
def edit_stock(request, stock_id):
    ...
def update_stock(request, stock_id):
    ...
```
3.定義路由 (urls.py)
```python
path('edit_stock/<int:stock_id>/', views.edit_stock, name='edit_stock'),
path('update_stock/<int:stock_id>/', views.update_stock, name='update_stock'),
```
4.新增編輯頁面(edit_stock.html)