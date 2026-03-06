print("测试行业策略回测功能（使用模拟数据）...")

# 导入必要的库
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入策略和回测引擎
from quant_framework.backtesting.backtest_engine import BacktestEngine, IndustryStrategy

# 创建模拟数据
dates = pd.date_range('2024-01-01', '2024-06-30')
symbols = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
industries = ['银行', '科技', '金融', '消费', '医药', '能源', '化工', '地产', '汽车', '通信']

# 生成模拟数据
data = []
for i, (symbol, industry) in enumerate(zip(symbols, industries)):
    for date in dates:
        # 生成随机价格，不同行业有不同的趋势
        base_price = 100 + i * 10
        
        # 为了生成更多交易信号，设置行业特定的趋势
        if industry == '银行':
            # 银行行业：先下跌后上涨，产生买入信号
            if date < dates[60]:  # 前60天下跌
                trend = -0.001
            else:  # 后60天上涨
                trend = 0.001
        elif industry == '科技':
            # 科技行业：先上涨后下跌，产生卖出信号
            if date < dates[60]:  # 前60天上涨
                trend = 0.001
            else:  # 后60天下跌
                trend = -0.001
        elif industry == '金融':
            # 金融行业：波动较大，产生多个交易信号
            trend = 0.0005 * np.sin((date - dates[0]).days / 10)
        else:
            # 其他行业：随机趋势
            trend = 0.0005 * np.random.randn()
        
        # 添加一些随机噪声，使价格波动更大
        noise = np.random.randn() * 3
        close = base_price * (1 + trend) ** (date - dates[0]).days + noise
        open_price = close * (1 + np.random.randn() * 0.01)
        high = max(open_price, close) * (1 + np.random.randn() * 0.01)
        low = min(open_price, close) * (1 - np.random.randn() * 0.01)
        amount = 1000000 + np.random.randn() * 100000
        
        data.append({
            'date': date,
            'symbol': symbol,
            'industry': industry,
            'open': open_price,
            'close': close,
            'high': high,
            'low': low,
            'amount': amount
        })

df = pd.DataFrame(data)
print(f"模拟数据生成完成，共 {len(df)} 条记录")

# 查看行业分布
industry_distribution = df['industry'].value_counts()
print("\n行业分布:")
print(industry_distribution)

# 创建行业策略，调整阈值以生成更多信号
strategy = IndustryStrategy(rsi_period=14, rsi_threshold=40, exit_threshold=60)

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
