from analysis.script.MySQLHelper import MySQLHelper


# ✅ 通用 context manager，確保自動關閉連線
class DB:
    def __enter__(self):
        self.helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
        self.helper.connect()
        return self.helper

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.helper.close()


# === 共用查詢工具 ===
def _build_conditions(conditions):
    """將條件 list 轉為 SQL WHERE 字串"""
    return " WHERE " + " AND ".join(conditions) if conditions else ""


# === 股票資訊 ===
def get_stock(stock_status=None, stock_code=None, stock_id=None, stock_name=None):
    sql = "SELECT * FROM stock"
    params, conditions = [], []

    if stock_id:
        conditions.append("stock_id = %s")
        params.append(stock_id)

    if stock_code:
        if isinstance(stock_code, (list, tuple)):
            placeholders = ', '.join(['%s'] * len(stock_code))
            conditions.append(f"stock_code IN ({placeholders})")
            params.extend(stock_code)
        else:
            conditions.append("stock_code = %s")
            params.append(stock_code)

    if stock_status:
        conditions.append("stock_status = %s")
        params.append(stock_status)

    if stock_name:
        names = stock_name if isinstance(stock_name, (list, tuple)) else [stock_name]
        sub_conditions = []
        for name in names:
            sub_conditions.append("stock_name LIKE %s")
            params.append(f"%{name}%")
        conditions.append("(" + " OR ".join(sub_conditions) + ")")

    sql += _build_conditions(conditions)
    with DB() as db:
        return db.execute_query(sql, tuple(params))


def add_stock(stock_code, stock_name, stock_kind, isin_code):
    sql = """
          INSERT INTO stock (stock_code, stock_name, stock_kind, isin_code, stock_status)
          VALUES (%s, %s, %s, %s, '10') ON DUPLICATE KEY
          UPDATE
              stock_name =
          VALUES (stock_name), stock_kind =
          VALUES (stock_kind), isin_code =
          VALUES (isin_code), stock_status =
          VALUES (stock_status) \
          """
    with DB() as db:
        db.execute_insert_update(sql, (stock_code, stock_name, stock_kind, isin_code))


def update_stock(stock_id, **kwargs):
    allowed_fields = {"stock_name", "stock_code", "stock_kind", "isin_code", "stock_status", "entry_id", "tr_id"}
    fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not stock_id:
        raise ValueError("stock_id 必須提供")
    if not fields_to_update:
        raise ValueError("沒有可更新的欄位")

    set_clause = ", ".join(f"{k} = %s" for k in fields_to_update)
    sql = f"UPDATE stock SET {set_clause} WHERE stock_id = %s"
    params = list(fields_to_update.values()) + [stock_id]

    with DB() as db:
        if not db.execute_insert_update(sql, tuple(params)):
            raise RuntimeError("更新股票資料失敗")


# === 價格相關 ===
def get_price(stock_code, limit=None, sort='asc', b_price_date=None, e_price_date=None):
    sql = """
          SELECT stock_code, price_date, open, close, high, low, volume
          FROM (
              SELECT *
              FROM price
              WHERE stock_code = %s \
          """
    params = [stock_code]

    if b_price_date:
        sql += " AND price_date >= %s"
        params.append(b_price_date)
    if e_price_date:
        sql += " AND price_date <= %s"
        params.append(e_price_date)

    sql += " ORDER BY price_date DESC"
    if limit:
        sql += " LIMIT %s"
        params.append(limit)
    sql += ") AS t ORDER BY t.price_date " + sort

    with DB() as db:
        return db.execute_query(sql, tuple(params))


def add_price(stock_code, price_date, open, close, high, low, volume=None):
    sql = """
          INSERT INTO price (stock_code, price_date, open, close, high, low, volume)
          VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
          UPDATE
              close =
          VALUES (close), volume =
          VALUES (volume) \
          """
    with DB() as db:
        db.execute_insert_update(sql, (stock_code, price_date, open, close, high, low, volume))


# === 營收相關 ===
def get_revenue(stock_code, limit=None, sort='asc'):
    sql = """
          SELECT stock_code, revenue_date, revenue
          FROM (SELECT *
                FROM revenue
                WHERE stock_code = %s
                ORDER BY revenue_date DESC \
          """
    params = [stock_code]
    if limit:
        sql += " LIMIT %s"
        params.append(limit)
    sql += ") AS t ORDER BY t.revenue_date " + sort

    with DB() as db:
        return db.execute_query(sql, tuple(params))


def add_revenue(stock_code, revenue_date, revenue):
    sql = """
          INSERT INTO revenue (stock_code, revenue_date, revenue)
          VALUES (%s, %s, %s) ON DUPLICATE KEY
          UPDATE revenue =
          VALUES (revenue) \
          """
    with DB() as db:
        db.execute_insert_update(sql, (stock_code, revenue_date, revenue))


# === EPS ===
def get_eps():
    with DB() as db:
        return db.execute_query("SELECT * FROM eps")


def add_eps(stock_code, eps_date, eps):
    sql = """
          INSERT INTO eps (stock_code, eps_date, eps)
          VALUES (%s, %s, %s) ON DUPLICATE KEY
          UPDATE eps =
          VALUES (eps) \
          """
    with DB() as db:
        db.execute_insert_update(sql, (stock_code, eps_date, eps))


# === 其他 ===
def get_last_trade_date(stock_code, year, month):
    sql = """
          SELECT MAX(price_date) AS price_date
          FROM price
          WHERE stock_code = %s
              AND YEAR (
              price_date) = %s
            AND MONTH (price_date) = %s \
          """
    with DB() as db:
        return db.execute_query(sql, (stock_code, year, month))
