"""
简单测试脚本 - 验证量化框架是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("开始测试量化框架...")

# 测试1: 导入数据模块
print("\n测试1: 导入数据模块")
try:
    from data.data_provider import DataManager, MockDataProvider
    print("✅ 数据模块导入成功")
    
    provider = MockDataProvider()
    data_manager = DataManager(provider)
    
    symbols = ['AAPL', 'MSFT']
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    df = data_manager.load_data(symbols, start_date, end_date)
    print(f"✅ 数据加载成功: {df.shape}")
    
except Exception as e:
    print(f"❌ 数据模块测试失败: {str(e)}")
    sys.exit(1)

# 测试2: 导入回测模块
print("\n测试2: 导入回测模块")
try:
    from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy
    print("✅ 回测模块导入成功")
    
    df = data_manager.calculate_technical_indicators(df)
    print("✅ 技术指标计算成功")
    
    strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)
    engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)
    
    result = engine.run(df, initial_cash=100000)
    print(f"✅ 回测执行成功: 总收益率={result.total_return:.2%}")
    
except Exception as e:
    print(f"❌ 回测模块测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试3: 导入风险管理模块
print("\n测试3: 导入风险管理模块")
try:
    from risk.risk_manager import RiskManager
    print("✅ 风险管理模块导入成功")
    
    if len(result.equity_curve) > 1:
        returns = result.equity_curve.pct_change().dropna()
        risk_manager = RiskManager()
        metrics = risk_manager.calculate_risk_metrics(returns)
        print(f"✅ 风险指标计算成功: 波动率={metrics.volatility:.2%}")
    
except Exception as e:
    print(f"❌ 风险管理模块测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("所有测试通过！量化框架运行正常。")
print("="*60)
print("\n框架功能:")
print("- 数据获取和管理")
print("- 技术指标计算")
print("- 策略回测")
print("- 风险管理")
print("\n您可以开始使用框架进行量化交易研究了！")
