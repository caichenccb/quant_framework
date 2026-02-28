"""
测试基本的Python和pandas功能
"""

print("测试基本功能...")

try:
    import pandas as pd
    print("pandas 导入成功")
    
    # 创建一个简单的DataFrame
    data = {
        'name': ['A', 'B', 'C'],
        'value': [1, 2, 3]
    }
    df = pd.DataFrame(data)
    print("DataFrame 创建成功")
    print("DataFrame:")
    print(df)
    
    # 保存为CSV
    df.to_csv('test.csv', index=False)
    print("CSV 保存成功")
    
    print("所有测试通过！")
    
except Exception as e:
    print(f"测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
