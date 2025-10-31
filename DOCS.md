# Django架構

## MVC 關係

1. **urls.py**  
   定義 URL 路由規則，將特定的網址對應到對應的 `views` 函數或類別。
2. **views.py**  
   處理使用者請求，呼叫對應的模型（`models`），取得資料後渲染 `templates`，最後回傳 `response`。
3. **templates**  
   負責顯示層的 HTML 檔案，接收 `views` 傳入的 `context` 資料，產生最終呈現的頁面。

## 行為流程

- 流程：URL → urls → views → templates → 瀏覽器。