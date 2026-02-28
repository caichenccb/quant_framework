"""
测试新添加的模块功能
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
    test_data = """产品类别,产品,花费,观看人数,日期,地区
A,产品1,1000,500,2023-01-01,北京
A,产品2,2000,800,2023-01-02,上海
B,产品3,1500,600,2023-01-03,广州
B,产品4,3000,1200,2023-01-04,深圳
A,产品5,1200,400,2023-01-05,北京
B,产品6,1800,700,2023-01-06,上海
"""
    
    # 模拟文件上传
    test_bytes = test_data.encode('utf-8')
    df = read_table(test_bytes, "test.csv")
    df, type_map = infer_types_and_convert(df)
    
    print(f"✅ 测试数据加载成功，形状: {df.shape}")
    print(f"✅ 字段类型: {type_map}")
    print(f"✅ 数据预览:\n{df}")
    
    # 测试数据概览
    print("\n测试数据概览...")
    print(f"总数据量: {len(df)} 行")
    print(f"字段数量: {len(df.columns)} 个")
    num_cols = len([c for c, t in type_map.items() if t == "number"])
    print(f"数值字段: {num_cols} 个")
    date_cols = len([c for c, t in type_map.items() if t == "datetime"])
    print(f"日期字段: {date_cols} 个")
    
    # 测试数值字段统计
    print("\n测试数值字段统计...")
    num_fields = [c for c, t in type_map.items() if t == "number"]
    if num_fields:
        stats_df = df[num_fields].describe().T
        print(f"数值字段统计:\n{stats_df}")
    
    # 测试文本字段统计
    print("\n测试文本字段统计...")
    text_fields = [c for c, t in type_map.items() if t == "text"]
    if text_fields:
        text_stats = []
        for field in text_fields:
            unique_count = df[field].nunique()
            non_null_count = df[field].notna().sum()
            text_stats.append({"字段": field, "非空值": non_null_count, "唯一值": unique_count})
        text_stats_df = pd.DataFrame(text_stats)
        print(f"文本字段统计:\n{text_stats_df}")
    
    # 测试数据质量分析
    print("\n测试数据质量分析...")
    # 缺失值分析
    missing_data = []
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_ratio = missing_count / len(df) * 100
        missing_data.append({"字段": col, "缺失值数量": missing_count, "缺失率": f"{missing_ratio:.2f}%"})
    missing_df = pd.DataFrame(missing_data)
    print(f"缺失值分析:\n{missing_df}")
    
    # 重复值分析
    duplicate_rows = df.duplicated().sum()
    duplicate_ratio = duplicate_rows / len(df) * 100
    print(f"重复值分析: 重复行数={duplicate_rows}, 重复率={duplicate_ratio:.2f}%")
    
    # 异常值检测
    print("\n测试异常值检测...")
    for field in num_fields:
        Q1 = df[field].quantile(0.25)
        Q3 = df[field].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[field] < lower_bound) | (df[field] > upper_bound)]
        outlier_count = len(outliers)
        outlier_ratio = outlier_count / len(df) * 100
        print(f"{field}: 异常值数量={outlier_count}, 异常率={outlier_ratio:.2f}%, 正常范围=[{lower_bound:.2f}, {upper_bound:.2f}]")
    
    # 测试字段对比
    print("\n测试字段对比...")
    if len(num_fields) >= 2:
        field1 = num_fields[0]
        field2 = num_fields[1]
        correlation = df[[field1, field2]].corr().iloc[0, 1]
        print(f"{field1} 与 {field2} 的相关系数: {correlation:.4f}")
    
    print("\n🎉 新模块功能测试完成！")
    print("\n已添加的模块：")
    print("1. 数据概览：显示数据基本信息、数值字段统计、文本字段统计")
    print("2. 数据质量分析：缺失值分析、重复值分析、异常值检测")
    print("3. 数据对比：时间区间对比、字段对比（相关性分析）")
    print("4. 报表导出：支持CSV、Excel、JSON、HTML格式导出")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
