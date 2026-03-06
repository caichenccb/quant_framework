from quant_framework.data.mysql_data_provider import create_mysql_provider, DataManager
from quant_framework.backtesting.backtest_engine import IndustryStrategy

# 创建数据提供者
provider = create_mysql_provider()
manager = DataManager(provider)

# 加载数据
df = manager.load_data(['1'], '2024-01-01', '2024-01-31')

# 计算技术指标
df = manager.calculate_technical_indicators(df)

# 创建行业策略
strategy = IndustryStrategy()

# 生成信号
df_with_signals = strategy.generate_signals(df)

# 查看信号情况
print("信号情况:")
print(df_with_signals[['date', 'industry', 'symbol', 'close', 'rsi', 'signal']].head(20))
print(f"总信号数: {df_with_signals['signal'].abs().sum()}")