from sqlalchemy import create_engine, text, or_, and_

engine = create_engine('mysql+pymysql://root:@127.0.0.1/stock')


# === 股票資訊 ===
def get_stock(stock_status=None, stock_code=None, stock_id=None, stock_name=None):
    params = {}
    cond = []

    if stock_id:
        cond.append("stock_id = :stock_id")
        params['stock_id'] = stock_id

    if stock_code:
        key = 'stock_code'
        if isinstance(stock_code, (list, tuple)):
            cond.append(f"{key} IN :{key}")
            params[key] = tuple(stock_code)
        else:
            cond.append(f"{key} = :{key}")
            params[key] = stock_code

    if stock_status:
        cond.append("stock_status = :stock_status")
        params['stock_status'] = stock_status

    if stock_name:
        names = stock_name if isinstance(stock_name, (list, tuple)) else [stock_name]
        or_parts = [f"stock_name LIKE :n{i}" for i in range(len(names))]
        cond.append(f"({' OR '.join(or_parts)})")
        params.update({f"n{i}": f"%{n}%" for i, n in enumerate(names)})

    sql = "SELECT * FROM stock"
    if cond:
        sql += " WHERE " + " AND ".join(cond)

    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings()]


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


# === 價格相關 ===
def get_price(stock_code, limit=None, sort='desc', b_price_date=None, e_price_date=None):
    # 基本 SQL
    sql = """
          SELECT stock_code, price_date, open, close, high, low, volume
          FROM price
          WHERE stock_code = :stock_code \
          """

    # 參數字典
    params = {'stock_code': stock_code}

    # 日期篩選
    if b_price_date:
        sql += " AND price_date >= :b_price_date"
        params['b_price_date'] = b_price_date
    if e_price_date:
        sql += " AND price_date <= :e_price_date"
        params['e_price_date'] = e_price_date

    # 排序
    sort = sort.lower()
    if sort not in ['asc', 'desc']:
        sort = 'asc'
    sql += f" ORDER BY price_date {sort.upper()}"

    # 限制筆數
    if limit:
        sql += " LIMIT :limit"
        params['limit'] = limit
    # 執行查詢
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        # 轉成 list of dict
        return [dict(row) for row in result.mappings()]


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


# === 營收相關 ===
def get_revenue(stock_code, limit=None, sort='asc'):
    # 基本 SQL
    sql = """
          SELECT stock_code, revenue_date, revenue
          FROM revenue
          WHERE stock_code = :stock_code
          """

    # 參數字典
    params = {'stock_code': stock_code}

    # 排序
    sort = sort.lower()
    if sort not in ['asc', 'desc']:
        sort = 'asc'
    sql += f" ORDER BY revenue_date {sort.upper()}"

    # 限制筆數
    if limit:
        sql += " LIMIT :limit"
        params['limit'] = limit
    # 執行查詢
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        # 轉成 list of dict
        return [dict(row) for row in result.mappings()]


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


# === EPS ===
def get_eps():
    sql = "SELECT * FROM eps"
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return [dict(row) for row in result.mappings()]


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


# === 其他 ===
def get_last_trade_date(stock_code, year, month):
    sql = """
          SELECT MAX(price_date) AS price_date
          FROM price
          WHERE stock_code = :stock_code
              AND YEAR(price_date) = :year
            AND MONTH(price_date) = :month \
          """

    params = {
        'stock_code': stock_code,
        'year': year,
        'month': month
    }

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        # 轉成字典列表
        return [dict(row) for row in result.mappings()]