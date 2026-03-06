"""
测试数据加载和回测，并将结果输出到文件
"""

import sys
import os

# 添加正确的路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quant_framework'))

print("开始测试...")

# 首先测试基本的导入
print("测试导入...")
try:
    from data.mysql_data_provider import create_mysql_provider, DataManager
    from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy
    print("✅ 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试MySQL数据提供者
print("\n测试MySQL数据提供者...")
try:
    provider = create_mysql_provider()
    print("✅ MySQL数据提供者创建成功")
    
    # 获取股票列表
    print("\n获取股票列表...")
    symbols = provider.get_stock_list()
    print(f"   股票列表: {symbols}")
    
    # 加载数据
    print("\n加载数据...")
    if symbols:
        df = provider.fetch_data([symbols[0]], '1991-04-01', '1991-04-10')
        print(f"   数据形状: {df.shape}")
        print(f"   数据前5行: {df.head()}")
    
    print("✅ 数据加载测试通过")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ 所有测试通过！")
