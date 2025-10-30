"""
# 前置作業
1. 安裝 pip install cx_Oracle (https://www.oracle.com/database/technologies/instant-client/macos-arm64-downloads.html)
2. 部屬 Oracle Client
"""
import cx_Oracle
from sqlalchemy import create_engine, text

# ✅ 指定 Oracle Client 目錄
cx_Oracle.init_oracle_client(lib_dir="/Users/yangfengkai/Documents/instantclient")

# ✅ 建立連線引擎
engine = create_engine('oracle+cx_oracle://prg:prg7695@116.236.30.11:1521/?service_name=mis.gs.com.cn')

# ✅ 正確用法：使用 text() 包裝 SQL
with engine.connect() as conn:
    data = conn.execute(text("SELECT * FROM idm_user WHERE ROWNUM < 10"))
    print(data.fetchall())
