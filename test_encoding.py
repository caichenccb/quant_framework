"""
测试编码处理功能
"""

import sys
import os
import io

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入bi.py中的函数
    from bi import read_table
    print("✅ 成功导入read_table函数")
    
    # 测试不同编码的CSV文件
    test_data_utf8 = """Name,Age,Score
Alice,25,85
Bob,30,90
"""
    
    # 模拟GBK编码的文件
    test_data_gbk = """姓名,年龄,分数
张三,25,85
李四,30,90
"""
    test_data_gbk_bytes = test_data_gbk.encode('gbk')
    
    # 测试UTF-8编码
    print("\n测试UTF-8编码...")
    utf8_bytes = test_data_utf8.encode('utf-8')
    df_utf8 = read_table(utf8_bytes, "test_utf8.csv")
    print(f"✅ UTF-8测试成功，形状: {df_utf8.shape}")
    print(f"✅ 列名: {list(df_utf8.columns)}")
    
    # 测试GBK编码
    print("\n测试GBK编码...")
    df_gbk = read_table(test_data_gbk_bytes, "test_gbk.csv")
    print(f"✅ GBK测试成功，形状: {df_gbk.shape}")
    print(f"✅ 列名: {list(df_gbk.columns)}")
    
    print("\n🎉 所有编码测试通过！")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
