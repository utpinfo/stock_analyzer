"""
# 前置作業
1. 安裝 pip install cx_Oracle (https://www.oracle.com/database/technologies/instant-client/macos-arm64-downloads.html)
2. 部屬 Oracle Client
"""
import cx_Oracle
from sqlalchemy import create_engine, text

# ✅ 指定 Oracle Client 目錄
#cx_Oracle.init_oracle_client(lib_dir="/Users/yangfengkai/Documents/instantclient")

# ✅ 建立連線引擎
engine = create_engine('mysql+pymysql://root:@127.0.0.1/stock')

# ✅ 正確用法：使用 text() 包裝 SQL
with engine.connect() as conn:
    data = conn.execute(text("SELECT * FROM stock limit 10"))
    print(data.fetchall())
