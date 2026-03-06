"""
测试新的行业周期策略
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入策略
from quant_framework.strategies.industry_cycle_strategy import IndustryCycleStrategy, IndustryCyclePhase

# 创建模拟数据
print("创建模拟行业数据...")
dates = pd.date_range('2024-01-01', '2024-06-30', freq='D')
industries = ['银行', '科技', '金融', '消费', '医药', '能源']

# 为每个行业生成数据
data = []
for i, industry in enumerate(industries):
    base_price = 100 + i * 20
    
    for j, date in enumerate(dates):
        # 模拟不同行业的周期特征
        if industry == '银行':
            # 银行：先跌后涨（复苏中）
            if j < len(dates) * 0.3:
                trend = -0.001
            else:
                trend = 0.0015
        elif industry == '科技':
            # 科技：持续上涨（扩张期）
            trend = 0.002
        elif industry == '医药':
            # 医药：先涨后跌（放缓期）
            if j < len(dates) * 0.5:
                trend = 0.001
            else:
                trend = -0.001
        else:
            # 其他：随机波动
            trend = np.random.randn() * 0.0005
        
        # 生成价格
        close = base_price * (1 + trend) ** j + np.random.randn() * 2
        volume = np.random.randint(100000, 1000000)
        amount = close * volume
        
        data.append({
            'date': date,
            'industry': industry,
            'close': close,
            'volume': volume,
            'amount': amount
        })

df = pd.DataFrame(data)
print(f"模拟数据创建完成: {len(df)} 条记录")

# 创建策略实例
strategy = IndustryCycleStrategy()

# 生成信号
print("\n生成行业周期信号...")
signals_df = strategy.generate_signals(df)

# 输出结果
print("\n" + "="*80)
print("测试完成!")
print("="*80)

# 显示最新日期的各行业评分
latest_date = signals_df['date'].max()
latest_data = signals_df[signals_df['date'] == latest_date]

print(f"\n最新日期 ({latest_date.strftime('%Y-%m-%d')}) 各行业状态:")
print("-" * 80)
for _, row in latest_data.iterrows():
    print(f"{row['industry']}: {row['cycle_phase']} (评分: {row['composite_score_smooth']:.2f})")
