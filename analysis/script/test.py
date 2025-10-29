from sqlalchemy import create_engine, text

from analysis.script import MySQL

engine = create_engine('mysql+pymysql://root:@127.0.0.1/stock')
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM stock WHERE stock_code = :sym"), {"sym": "8421"})
    #data = result.fetchall()
    data = [dict(row) for row in result.mappings().fetchall()]
print(data)

data = MySQL.get_stock(stock_status=None, stock_code='8421')
print(data)