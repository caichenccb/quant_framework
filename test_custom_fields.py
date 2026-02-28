"""
测试自定义字段功能
"""

import sys
import os
import io
import pandas as pd

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入bi.py中的函数
    from bi import read_table, infer_types_and_convert, build_pivot
    print("✅ 成功导入所需函数")
    
    # 创建测试数据
    test_data = """产品,花费,观看人数,日期
A,1000,500,2023-01-01
B,2000,800,2023-01-02
C,1500,600,2023-01-03
D,3000,1200,2023-01-04
"""
    
    # 模拟文件上传
    test_bytes = test_data.encode('utf-8')
    df = read_table(test_bytes, "test.csv")
    df, type_map = infer_types_and_convert(df)
    
    print(f"✅ 测试数据加载成功，形状: {df.shape}")
    print(f"✅ 字段类型: {type_map}")
    print(f"✅ 数据预览:\n{df}")
    
    # 模拟自定义字段计算
    print("\n测试自定义字段计算...")
    
    # 测试1: 花费/观看人数
    try:
        df_with_custom = df.copy()
        df_with_custom["人均花费"] = df_with_custom["花费"] / df_with_custom["观看人数"]
        print(f"✅ 自定义字段'人均花费'计算成功")
        print(f"✅ 计算结果:\n{df_with_custom[['产品', '花费', '观看人数', '人均花费']]}")
    except Exception as e:
        print(f"❌ 自定义字段计算失败: {str(e)}")
    
    # 测试2: 复杂计算
    try:
        df_with_custom = df.copy()
        df_with_custom["花费占比"] = df_with_custom["花费"] / df_with_custom["花费"].sum() * 100
        print(f"\n✅ 自定义字段'花费占比'计算成功")
        print(f"✅ 计算结果:\n{df_with_custom[['产品', '花费', '花费占比']]}")
    except Exception as e:
        print(f"❌ 自定义字段计算失败: {str(e)}")
    
    print("\n🎉 自定义字段功能测试完成！")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
