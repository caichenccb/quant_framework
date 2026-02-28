"""
测试bi.py的基本功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入bi.py中的函数
    from bi import read_table, infer_types_and_convert, build_pivot, pivot_to_tidy, save_to_local
    import pandas as pd
    import io
    
    print("✅ 成功导入bi.py中的函数")
    
    # 测试数据
    test_data = """Name,Age,Score,Date,Active
Alice,25,85,2023-01-01,True
Bob,30,90,2023-01-02,False
Charlie,35,80,2023-01-03,True
David,40,95,2023-01-04,False
"""
    
    # 测试read_table函数
    test_bytes = test_data.encode('utf-8')
    df = read_table(test_bytes, "test.csv")
    print(f"✅ 成功读取测试数据，形状: {df.shape}")
    print(f"✅ 列名: {list(df.columns)}")
    
    # 测试infer_types_and_convert函数
    df_converted, type_map = infer_types_and_convert(df)
    print(f"✅ 成功推断字段类型")
    print(f"✅ 字段类型: {type_map}")
    
    # 测试build_pivot函数
    pv = build_pivot(df_converted, ['Name'], [], 'Score', 'sum')
    print(f"✅ 成功生成透视表")
    print(f"✅ 透视表形状: {pv.shape}")
    
    # 测试pivot_to_tidy函数
    tidy = pivot_to_tidy(pv)
    print(f"✅ 成功转换为tidy格式")
    print(f"✅ tidy数据形状: {tidy.shape}")
    
    # 测试save_to_local函数
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = save_to_local(df, "test_output.csv", tmpdir)
        print(f"✅ 成功保存到本地: {save_path}")
        
    print("\n🎉 所有测试通过！代码可以正常运行。")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
