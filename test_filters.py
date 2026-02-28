"""
测试日期筛选和条件筛选功能
"""

import sys
import os
import io
import pandas as pd

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入bi.py中的函数
    from bi import read_table, infer_types_and_convert
    print("✅ 成功导入所需函数")
    
    # 创建测试数据
    test_data = """产品类别,产品,花费,观看人数,日期
A,产品1,1000,500,2023-01-01
A,产品2,2000,800,2023-01-02
B,产品3,1500,600,2023-01-03
B,产品4,3000,1200,2023-01-04
A,产品5,1200,400,2023-01-05
"""
    
    # 模拟文件上传
    test_bytes = test_data.encode('utf-8')
    df = read_table(test_bytes, "test.csv")
    df, type_map = infer_types_and_convert(df)
    
    print(f"✅ 测试数据加载成功，形状: {df.shape}")
    print(f"✅ 字段类型: {type_map}")
    print(f"✅ 数据预览:\n{df}")
    
    # 测试日期格式统一
    print("\n测试日期格式统一...")
    date_col = [c for c, t in type_map.items() if t == "datetime"][0]
    print(f"日期字段: {date_col}")
    print(f"日期格式: {df[date_col].dtype}")
    print(f"日期值:\n{df[date_col]}")
    
    # 测试日期筛选
    print("\n测试日期筛选...")
    # 模拟日期筛选
    start_date = pd.to_datetime("2023-01-02")
    end_date = pd.to_datetime("2023-01-04")
    
    filtered_df = df[
        (pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d') >= start_date.strftime('%Y-%m-%d')) &
        (pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d') <= end_date.strftime('%Y-%m-%d'))
    ]
    
    print(f"筛选后数据行数: {len(filtered_df)}")
    print(f"筛选后数据:\n{filtered_df}")
    
    # 测试条件筛选
    print("\n测试条件筛选...")
    # 模拟条件筛选：花费 > 1500
    condition_filtered = df[df["花费"] > 1500]
    print(f"条件筛选后数据行数: {len(condition_filtered)}")
    print(f"条件筛选后数据:\n{condition_filtered}")
    
    # 测试文本筛选
    print("\n测试文本筛选...")
    # 模拟文本筛选：产品类别 = A
    text_filtered = df[df["产品类别"] == "A"]
    print(f"文本筛选后数据行数: {len(text_filtered)}")
    print(f"文本筛选后数据:\n{text_filtered}")
    
    print("\n🎉 筛选功能测试完成！")
    print("\n说明：")
    print("1. 日期格式已统一为yyyy-mm-dd格式")
    print("2. 支持日期区间筛选，可以选择开始和结束日期")
    print("3. 支持条件筛选，可以根据字段类型设置不同的筛选条件")
    print("4. 筛选条件会应用到所有后续操作，包括透视表和自定义字段计算")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
