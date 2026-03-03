"""
简单测试MySQL数据库连接
"""

import sys
import os

# 检查依赖包
try:
    import pymysql
    import sqlalchemy
    from sqlalchemy import create_engine, text
    print("✅ 依赖包已安装")
except ImportError as e:
    print(f"❌ 缺少依赖包: {str(e)}")
    print("请运行: pip install pymysql sqlalchemy")
    sys.exit(1)

# 数据库连接字符串
connection_string = 'mysql+pymysql://root:123456@localhost:3306/metabase'
table_name = 'akshare'

print("测试MySQL数据库连接...")

# 测试连接
try:
    print("正在连接数据库...")
    engine = create_engine(connection_string, echo=False)
    
    # 测试连接
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")
    
    # 测试获取股票列表
    print("\n测试获取股票列表...")
    with engine.connect() as conn:
        query = text(f"SELECT DISTINCT `股票代码` FROM {table_name} LIMIT 3")
        result = conn.execute(query)
        symbols = [str(row[0]) for row in result]
        print(f"✅ 股票列表获取成功: {symbols}")
    
    # 测试获取数据
    print("\n测试获取数据...")
    with engine.connect() as conn:
        query = text(f"SELECT * FROM {table_name} LIMIT 2")
        result = conn.execute(query)
        columns = result.keys()
        rows = result.fetchall()
        print(f"✅ 数据获取成功: {len(rows)} 条记录")
        print(f"列名: {list(columns)}")
        if rows:
            print("数据样例:")
            for row in rows:
                print(dict(zip(columns, row)))
    
    print("\n✅ 所有测试通过！")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
