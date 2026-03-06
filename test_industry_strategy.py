print("测试行业策略回测功能...")

# 导入必要的库
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入策略和回测引擎
from quant_framework.data.mysql_data_provider import create_mysql_provider, DataManager
from quant_framework.backtesting.backtest_engine import BacktestEngine, IndustryStrategy

# 创建数据提供者
provider = create_mysql_provider()
manager = DataManager(provider)

# 加载测试数据
symbols = manager.get_available_symbols()
print(f"获取到 {len(symbols)} 只股票")

# 限制股票数量
max_symbols = 10
if len(symbols) > max_symbols:
    symbols = symbols[:max_symbols]
    print(f"限制股票数量为 {max_symbols} 只")

# 加载数据
df = manager.load_data(symbols, '2024-01-01', '2024-06-30')
print(f"数据加载完成，共 {len(df)} 条记录")

# 查看行业分布
industry_distribution = df['industry'].value_counts()
print("\n行业分布:")
print(industry_distribution)

# 计算技术指标
df = manager.calculate_technical_indicators(df)

# 创建行业策略
strategy = IndustryStrategy(rsi_period=14, rsi_threshold=30, exit_threshold=70)

# 回测
engine = BacktestEngine(strategy)
result = engine.run(df)

# 输出回测结果
print("\n回测结果:")
print(f"总收益率: {result.total_return:.2%}")
print(f"年化收益率: {result.annual_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown:.2%}")
print(f"总交易次数: {result.total_trades}")
print(f"胜率: {result.win_rate:.2%}")
print(f"盈亏比: {result.profit_factor:.2f}")

print("\n测试完成")
