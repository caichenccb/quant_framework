"""
简单的MySQL数据库测试脚本
"""

import pymysql

# 数据库连接信息
host = 'localhost'
port = 3306
user = 'root'
password = '123456'
database = 'metabase'

print("测试MySQL数据库连接...")

# 连接数据库
try:
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    print("✅ 数据库连接成功")
    
    # 创建游标
    cursor = conn.cursor()
    
    # 查询股票列表
    print("\n查询股票列表...")
    cursor.execute("SELECT DISTINCT `股票代码` FROM akshare LIMIT 3")
    symbols = cursor.fetchall()
    print(f"✅ 股票列表: {[str(s[0]) for s in symbols]}")
    
    # 查询数据
    print("\n查询数据...")
    cursor.execute("SELECT * FROM akshare WHERE `股票代码` = '1' LIMIT 3")
    rows = cursor.fetchall()
    print(f"✅ 数据行数: {len(rows)}")
    
    # 打印数据
    if rows:
        print("\n数据样例:")
        for row in rows:
            print(f"  日期: {row[0]}, 股票代码: {row[1]}, 收盘: {row[3]}")
    
    # 关闭连接
    cursor.close()
    conn.close()
    print("\n✅ 测试完成！")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
