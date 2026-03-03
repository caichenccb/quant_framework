"""
测试数据库数据输入格式
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_provider import DataManager, create_database_provider_from_sample

print("测试数据库数据输入格式...")

# 1. 创建数据库数据提供者
print("\n1. 创建数据库数据提供者")
try:
    provider = create_database_provider_from_sample()
    manager = DataManager(provider)
    print("✅ 数据库数据提供者创建成功")
except Exception as e:
    print(f"❌ 创建数据库数据提供者失败: {str(e)}")
    sys.exit(1)

# 2. 获取股票列表
print("\n2. 获取股票列表")
try:
    symbols = manager.get_available_symbols()
    print(f"✅ 股票列表获取成功: {symbols}")
except Exception as e:
    print(f"❌ 获取股票列表失败: {str(e)}")
    sys.exit(1)

# 3. 加载数据
print("\n3. 加载数据")
try:
    start_date = '2025-07-28'
    end_date = '2025-07-28'
    df = manager.load_data(symbols, start_date, end_date)
    print(f"✅ 数据加载成功: {df.shape} 条记录")
    print(f"数据字段: {list(df.columns)}")
    print(f"\n数据预览:")
    print(df.head())
except Exception as e:
    print(f"❌ 数据加载失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 计算收益率
print("\n4. 计算收益率")
try:
    df_with_returns = manager.calculate_returns(df)
    print("✅ 收益率计算成功")
    print(f"\n收益率数据:")
    print(df_with_returns[['symbol', 'date', 'close', 'return']].head())
except Exception as e:
    print(f"❌ 收益率计算失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 计算技术指标
print("\n5. 计算技术指标")
try:
    df_with_indicators = manager.calculate_technical_indicators(df)
    print("✅ 技术指标计算成功")
    print(f"\n技术指标数据:")
    print(df_with_indicators[['symbol', 'date', 'close', 'ma5', 'rsi', 'macd']].head())
except Exception as e:
    print(f"❌ 技术指标计算失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. 测试回测功能
print("\n6. 测试回测功能")
try:
    from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy
    
    strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)
    engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)
    
    result = engine.run(df_with_indicators, initial_cash=100000)
    print(f"✅ 回测执行成功")
    print(f"总收益率: {result.total_return:.2%}")
    print(f"年化收益率: {result.annual_return:.2%}")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"最大回撤: {result.max_drawdown:.2%}")
except Exception as e:
    print(f"❌ 回测执行失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("数据库数据输入格式测试完成！")
print("="*60)
print("\n如何使用您的数据库数据:")
print("1. 准备您的数据库数据，格式如下:")
print("   [")
print("       {")
print("           '日期': '2025-07-28',")
print("           '股票代码': 920108,")
print("           '开盘': 18.04,")
print("           '收盘': 18.71,")
print("           '最高': 18.93,")
print("           '最低': 17.99,")
print("           '成交量': 147670,")
print("           '成交额': 26920398.11,")
print("           '名字': '安科科技',")
print("           '行业': '电气设备'")
print("       },")
print("       # 更多数据...")
print("   ]")
print("\n2. 使用DatabaseDataProvider:")
print("   from data.data_provider import DataManager, DatabaseDataProvider")
print("   " )
print("   # 您的数据库数据")
print("   your_data = [...]")
print("   " )
print("   # 创建数据提供者")
print("   provider = DatabaseDataProvider(your_data)")
print("   manager = DataManager(provider)")
print("   " )
print("   # 加载数据")
print("   symbols = manager.get_available_symbols()")
print("   df = manager.load_data(symbols, '2025-07-01', '2025-07-31')")
print("\n3. 然后可以进行策略回测、风险管理等操作")
