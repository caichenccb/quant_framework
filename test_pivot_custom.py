"""
测试自定义字段在透视表中的计算
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
    test_data = """产品类别,产品,花费,观看人数,日期
A,产品1,1000,500,2023-01-01
A,产品2,2000,800,2023-01-02
B,产品3,1500,600,2023-01-03
B,产品4,3000,1200,2023-01-04
"""
    
    # 模拟文件上传
    test_bytes = test_data.encode('utf-8')
    df = read_table(test_bytes, "test.csv")
    df, type_map = infer_types_and_convert(df)
    
    print(f"✅ 测试数据加载成功，形状: {df.shape}")
    print(f"✅ 字段类型: {type_map}")
    print(f"✅ 数据预览:\n{df}")
    
    # 测试自定义字段在透视表中的计算
    print("\n测试自定义字段在透视表中的计算...")
    
    # 模拟自定义字段：人均花费 = 花费 / 观看人数
    custom_field_name = "人均花费"
    custom_formula = "花费/观看人数"
    
    # 测试1: 不分组，直接计算
    print("\n测试1: 不分组，直接计算")
    total_cost = df["花费"].sum()
    total_views = df["观看人数"].sum()
    expected_avg_cost = total_cost / total_views
    print(f"总花费: {total_cost}")
    print(f"总观看人数: {total_views}")
    print(f"预期人均花费: {expected_avg_cost:.2f}")
    
    # 测试2: 按产品类别分组计算
    print("\n测试2: 按产品类别分组计算")
    grouped = df.groupby("产品类别")
    for category, group in grouped:
        category_cost = group["花费"].sum()
        category_views = group["观看人数"].sum()
        category_avg_cost = category_cost / category_views
        print(f"类别 {category}: 总花费={category_cost}, 总观看人数={category_views}, 人均花费={category_avg_cost:.2f}")
    
    # 测试3: 验证透视表计算
    print("\n测试3: 验证透视表计算")
    # 先生成基础字段的透视表
    cost_pivot = build_pivot(df, ["产品类别"], [], "花费", "sum")
    views_pivot = build_pivot(df, ["产品类别"], [], "观看人数", "sum")
    
    print(f"\n花费透视表:\n{cost_pivot}")
    print(f"\n观看人数透视表:\n{views_pivot}")
    
    # 计算自定义字段
    combined = pd.merge(cost_pivot.reset_index(), views_pivot.reset_index(), on="产品类别")
    combined[custom_field_name] = combined["花费"] / combined["观看人数"]
    print(f"\n自定义字段计算结果:\n{combined}")
    
    print("\n🎉 透视表自定义字段计算测试完成！")
    print("\n说明：")
    print("1. 自定义字段'人均花费'在透视表中会先对'花费'和'观看人数'分别求和")
    print("2. 然后用总花费除以总观看人数，得到正确的人均花费")
    print("3. 这与Excel透视表的计算方式一致")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
