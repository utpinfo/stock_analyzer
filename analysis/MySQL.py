from analysis.MySQLHelper import MySQLHelper


def get_last_trade_date(stock_code, year, month):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = "select max(price_date) price_date from price where stock_code=%s and year(price_date) = %s and month(price_date) = %s"
    params = (stock_code, year, month)
    data = helper.execute_query(sql, params)
    helper.close()
    return data


def get_stock(stock_status='10', stock_code=None, stock_id=None):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()

    sql = "SELECT * FROM stock"
    params = []
    conditions = []

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

    # 如果有任何條件，就加上 WHERE
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    data = helper.execute_query(sql, tuple(params))
    helper.close()
    return data


def add_stock(stock_code, stock_name, stock_kind, isin_code):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = """
        insert into stock
            (stock_code, stock_name, stock_kind, isin_code, stock_status)
        values (%s, %s, %s, %s, '10')
            on duplicate key update stock_name = values(stock_name), stock_kind = values(stock_kind), isin_code = values(isin_code), stock_status = values(stock_status)
        """
    params = (stock_code, stock_name, stock_kind, isin_code)
    helper.execute_insert_update(sql, params)
    helper.close()

def update_stock(stock_id, **kwargs):
    """
    更新 stock 表的多個欄位。
    :param stock_id: 必須提供，指定要更新的股票
    :param kwargs: 欲更新的欄位，例如 stock_name="新名稱", stock_status="10"
    """
    if not stock_id:
        raise ValueError("stock_id 必須提供")

    allowed_fields = {"stock_name", "stock_code", "stock_kind", "isin_code", "stock_status", "entry_id", "tr_id"}
    fields_to_update = {k: v for k, v in kwargs.items() if k in allowed_fields}

    if not fields_to_update:
        raise ValueError("沒有可更新的欄位")

    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()

    # 拼接 SQL
    set_clause = ", ".join([f"{k} = %s" for k in fields_to_update.keys()])
    sql = f"UPDATE stock SET {set_clause} WHERE stock_id = %s"
    params = list(fields_to_update.values()) + [stock_id]
    success = helper.execute_insert_update(sql, tuple(params))
    helper.close()

    if not success:
        raise RuntimeError("更新股票資料失敗")

def get_price(stock_code, limit, sort='asc', b_price_date=None, e_price_date=None):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = """
        SELECT stock_code, price_date, open, close, high, low, volume
        FROM (
            SELECT *
            FROM price
            WHERE stock_code = %s
    """
    params = [stock_code]
    # 如果提供 price_date，加入過濾
    if b_price_date:
        sql += " AND price_date >= %s"
        params.append(b_price_date)

    if e_price_date:
        sql += " AND price_date <= %s"
        params.append(e_price_date)
    # 內層排序與限制筆數
    if limit:
        sql += " ORDER BY price_date DESC LIMIT %s"
        params.append(limit)
    else:
        sql += " ORDER BY price_date DESC"

    # 外層排序
    sql += ") AS t ORDER BY t.price_date " + sort

    data = helper.execute_query(sql, tuple(params))
    helper.close()
    return data


def add_price(stock_code, price_date, open, close, high, low, volume=None):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = """
    insert into price
        (stock_code, price_date, open, close, high, low, volume)
    values (%s, %s, %s, %s, %s, %s, %s)
        on duplicate key update close = values (close), volume = values(volume)
    """
    params = (stock_code, price_date, open, close, high, low, volume)
    helper.execute_insert_update(sql, params)
    # if helper.execute_insert_update(sql, params):
    #    print("Data inserted successfully")
    helper.close()


def get_revenue(stock_code, limit, sort='asc'):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = """
        SELECT stock_code, revenue_date, revenue
        FROM (
            SELECT *
            FROM revenue
            WHERE stock_code = %s
    """
    params = [stock_code]
    # 內層排序與限制筆數
    if limit:
        sql += " ORDER BY revenue_date DESC LIMIT %s"
        params.append(limit)
    else:
        sql += " ORDER BY revenue_date DESC"

    # 外層排序
    sql += ") AS t ORDER BY t.revenue_date " + sort

    data = helper.execute_query(sql, tuple(params))
    helper.close()
    return data



def add_revenue(stock_code, revenue_date, revenue):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = """
    insert into revenue
        (stock_code, revenue_date, revenue)
    values (%s, %s, %s)
        on duplicate key update revenue = values (revenue)
    """
    params = (stock_code, revenue_date, revenue)
    helper.execute_insert_update(sql, params)
    # if helper.execute_insert_update(sql, params):
    #    print("Data inserted successfully")
    helper.close()


def get_eps():
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = "select * from eps"
    data = helper.execute_query(sql)
    helper.close()
    return data


def add_eps(stock_code, eps_date, eps):
    helper = MySQLHelper(host='127.0.0.1', user='root', password='', database='stock')
    helper.connect()
    sql = """
    insert into eps
        (stock_code, eps_date, eps)
    values (%s, %s, %s)
        on duplicate key update eps = values (eps)
    """
    params = (stock_code, eps_date, eps)
    helper.execute_insert_update(sql, params)
    # if helper.execute_insert_update(sql, params):
    #    print("Data inserted successfully")
    helper.close()
