"""
直接使用pymysql连接数据库的测试脚本
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
    cursor.execute("SELECT DISTINCT `股票代码` FROM akshare LIMIT 5")
    symbols = cursor.fetchall()
    print(f"✅ 股票列表: {[str(s[0]) for s in symbols]}")
    
    # 查询数据
    print("\n查询数据...")
    query = """
    SELECT 
        `日期` as date,
        `股票代码` as symbol,
        `开盘` as open,
        `收盘` as close,
        `最高` as high,
        `最低` as low,
        `成交量` as volume,
        `成交额` as amount,
        `名字` as name,
        `行业` as industry
    FROM 
        akshare
    WHERE 
        `日期` >= '1991-04-01' 
        AND `日期` <= '1991-04-10'
        AND `股票代码` IN ('1')
    LIMIT 10
    """
    
    print(f"执行查询: {query}")
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"✅ 查询结果行数: {len(rows)}")
    
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
