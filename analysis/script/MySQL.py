from sqlalchemy import create_engine, text, or_, and_

engine = create_engine('mysql+pymysql://root:@127.0.0.1/stock')


# === 查詢股票 ===
def get_stock(stock_status=None, stock_code=None, stock_id=None, stock_name=None):
    params = {}
    cond = []

    if stock_code:
        cond.append("stock_code IN :stock_code")
        params["stock_code"] = (
            tuple(stock_code) if isinstance(stock_code, (list, tuple)) else (stock_code,)
        )

    if stock_id:
        cond.append("stock_id = :stock_id")
        params['stock_id'] = stock_id

    if stock_status:
        cond.append("stock_status = :stock_status")
        params['stock_status'] = stock_status

    if stock_name:
        cond.append("stock_name LIKE :stock_name")
        params['stock_name'] = f"%{stock_name}%"

    sql = "SELECT * FROM stock"
    if cond:
        sql += " WHERE " + " AND ".join(cond)

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(r) for r in result.mappings()]


# === 新增股票 ===
def add_stock(stock_code, stock_name, stock_kind, isin_code):
    sql = """
          INSERT INTO stock (stock_code, stock_name, stock_kind, isin_code, stock_status)
          VALUES (:stock_code, :stock_name, :stock_kind, :isin_code, '10') ON DUPLICATE KEY
          UPDATE
              stock_name =
          VALUES (stock_name), stock_kind =
          VALUES (stock_kind), isin_code =
          VALUES (isin_code), stock_status =
          VALUES (stock_status) \
          """

    params = {
        'stock_code': stock_code,
        'stock_name': stock_name,
        'stock_kind': stock_kind,
        'isin_code': isin_code
    }

    with engine.connect() as conn:
        conn.execute(text(sql), params)
        conn.commit()  # 必須 commit 才會生效


# === 更新股票 ===
def update_stock(stock_id, **kwargs):
    allowed_fields = {"stock_name", "stock_code", "stock_kind", "isin_code", "stock_status", "entry_id", "tr_id"}
    fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not stock_id:
        raise ValueError("stock_id 必須提供")
    if not fields_to_update:
        raise ValueError("沒有可更新的欄位")

    # 建立 SET 子句
    set_clause = ", ".join(f"{k} = :{k}" for k in fields_to_update)
    sql = f"UPDATE stock SET {set_clause} WHERE stock_id = :stock_id"

    # 合併參數
    params = fields_to_update.copy()
    params['stock_id'] = stock_id

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        conn.commit()  # 更新必須 commit
        if result.rowcount == 0:
            raise RuntimeError("更新股票資料失敗")


# === 查詢價格 ===
def get_price(stock_code, limit=None, sort='desc', b_price_date=None, e_price_date=None):
    params = {}
    cond = []

    # 股票代碼：支援單筆或多筆
    if stock_code:
        cond.append("stock_code IN :stock_code")
        params["stock_code"] = (
            tuple(stock_code) if isinstance(stock_code, (list, tuple)) else (stock_code,)
        )

    # 日期範圍
    if b_price_date:
        cond.append("price_date >= :b_price_date")
        params["b_price_date"] = b_price_date
    if e_price_date:
        cond.append("price_date <= :e_price_date")
        params["e_price_date"] = e_price_date

    # 組合 SQL
    sql = """
          SELECT stock_code, price_date, open, close, high, low, volume
          FROM price \
          """
    if cond:
        sql += " WHERE " + " AND ".join(cond)

    # 排序方向
    sort = sort.lower()
    if sort not in ("asc", "desc"):
        sort = "asc"
    sql += f" ORDER BY price_date {sort.upper()}"

    # 限制筆數
    if limit:
        sql += " LIMIT :limit"
        params["limit"] = limit

    # 執行查詢
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(r) for r in result.mappings()]


# === 新增價格 ===
def add_price(stock_code, price_date, open, close, high, low, volume=None):
    sql = """
          INSERT INTO price (stock_code, price_date, open, close, high, low, volume)
          VALUES (:stock_code, :price_date, :open, :close, :high, :low, :volume) ON DUPLICATE KEY
          UPDATE
              close =
          VALUES (close), volume =
          VALUES (volume) \
          """

    params = {
        'stock_code': stock_code,
        'price_date': price_date,
        'open': open,
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }

    with engine.connect() as conn:
        conn.execute(text(sql), params)
        conn.commit()  # 必須 commit 才會生效


# === 查詢營收 ===
def get_revenue(stock_code=None, b_revenue_date=None, e_revenue_date=None, limit=None, sort='asc'):
    params = {}
    cond = []

    # 股票代碼：支援單一或多股票
    if stock_code:
        cond.append("stock_code IN :stock_code")
        params["stock_code"] = (
            tuple(stock_code) if isinstance(stock_code, (list, tuple)) else (stock_code,)
        )

    # 日期範圍
    if b_revenue_date:
        cond.append("revenue_date >= :b_revenue_date")
        params["b_revenue_date"] = b_revenue_date
    if e_revenue_date:
        cond.append("revenue_date <= :e_revenue_date")
        params["e_revenue_date"] = e_revenue_date

    # 組合 SQL
    sql = """
          SELECT stock_code, revenue_date, revenue
          FROM revenue \
          """
    if cond:
        sql += " WHERE " + " AND ".join(cond)

    # 排序
    sort = sort.lower()
    if sort not in ("asc", "desc"):
        sort = "asc"
    sql += f" ORDER BY revenue_date {sort.upper()}"

    # 限制筆數
    if limit:
        sql += " LIMIT :limit"
        params["limit"] = limit

    # 執行查詢
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(r) for r in result.mappings()]


# === 新增營收 ===
def add_revenue(stock_code, revenue_date, revenue):
    sql = """
          INSERT INTO revenue (stock_code, revenue_date, revenue)
          VALUES (:stock_code, :revenue_date, :revenue) ON DUPLICATE KEY
          UPDATE
              revenue =
          VALUES (revenue) \
          """
    params = {
        'stock_code': stock_code,
        'revenue_date': revenue_date,
        'revenue': revenue
    }

    with engine.connect() as conn:
        conn.execute(text(sql), params)
        conn.commit()  # 必須 commit 才會生效


# === 查詢EPS ===
def get_eps(stock_code):
    params = {}
    cond = []
    if stock_code:
        cond.append("stock_code IN :stock_code")
        params["stock_code"] = (
            tuple(stock_code) if isinstance(stock_code, (list, tuple)) else (stock_code,)
        )

    sql = "SELECT * FROM eps"
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(row) for row in result.mappings()]


# === 新增EPS ===
def add_eps(stock_code, eps_date, eps):
    sql = """
          INSERT INTO eps (stock_code, eps_date, eps)
          VALUES (:stock_code, :eps_date, :eps) ON DUPLICATE KEY
          UPDATE
              eps =
          VALUES (eps) \
          """
    params = {
        'stock_code': stock_code,
        'eps_date': eps_date,
        'eps': eps
    }

    with engine.connect() as conn:
        conn.execute(text(sql), params)
        conn.commit()  # 必須 commit 才會生效


# === 查詢最後交易日 ===
def get_last_trade_date(stock_code=None, year=None, month=None):
    params = {}
    cond = []

    # 股票代碼支援單一或多股票
    if stock_code:
        cond.append("stock_code IN :stock_code")
        params["stock_code"] = (
            tuple(stock_code) if isinstance(stock_code, (list, tuple)) else (stock_code,)
        )

    # 年、月條件
    if year:
        cond.append("YEAR(price_date) = :year")
        params["year"] = year
    if month:
        cond.append("MONTH(price_date) = :month")
        params["month"] = month

    # 組合 SQL
    sql = "SELECT MAX(price_date) AS price_date FROM price"
    if cond:
        sql += " WHERE " + " AND ".join(cond)

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(r) for r in result.mappings()]
