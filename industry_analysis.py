from quant_framework.data.mysql_data_provider import create_mysql_provider, DataManager
import pandas as pd
import numpy as np

# 创建数据提供者
provider = create_mysql_provider()
manager = DataManager(provider)

# 加载所有股票数据
print("加载所有股票数据...")
symbols = manager.get_available_symbols()
print(f"获取到 {len(symbols)} 只股票")

# 限制股票数量，避免数据量过大
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

# 按照行业和日期分组，计算行业平均收盘价
def calculate_industry_metrics(df):
    """计算行业指标"""
    # 按照行业和日期分组，计算平均收盘价
    industry_df = df.groupby(['industry', 'date']).agg({
        'close': 'mean',
        'open': 'mean',
        'high': 'mean',
        'low': 'mean',
        'amount': 'sum'
    }).reset_index()
    
    # 计算行业动量指标
    industry_df['momentum_20'] = industry_df.groupby('industry')['close'].transform(
        lambda x: x / x.shift(20) - 1
    )
    industry_df['momentum_120'] = industry_df.groupby('industry')['close'].transform(
        lambda x: x / x.shift(120) - 1
    )
    
    # 计算RSI
    def calculate_rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    industry_df['rsi'] = industry_df.groupby('industry')['close'].transform(calculate_rsi)
    
    return industry_df

# 分析行业复苏阶段
def analyze_industry_recovery(industry_df):
    """分析行业复苏阶段"""
    # 生成信号
    industry_df['signal'] = 0
    
    # 动量趋势型信号：20日收益率为正（120日收益率可能因为数据不足为NaN）
    momentum_cond = industry_df['momentum_20'] > 0
    
    # 均值回归型信号：RSI低于阈值（超卖），调整为40以增加信号数量
    rsi_cond = industry_df['rsi'] < 40
    
    # 综合信号
    industry_df.loc[momentum_cond & rsi_cond, 'signal'] = 1  # 行业开始复苏，买入
    
    # 输出各行业的复苏节点
    recovery_nodes = industry_df.loc[industry_df['signal'] == 1, ['date', 'industry', 'close', 'momentum_20', 'momentum_120', 'rsi']]
    
    return recovery_nodes

# 计算行业指标
print("计算行业指标...")
industry_df = calculate_industry_metrics(df)

# 分析行业复苏阶段
print("分析行业复苏阶段...")
recovery_nodes = analyze_industry_recovery(industry_df)

# 输出结果
print("\n行业复苏节点:")
print(recovery_nodes)

# 按行业分组，统计复苏次数
recovery_count = recovery_nodes.groupby('industry').size().reset_index(name='recovery_count')
print("\n各行业复苏次数:")
print(recovery_count)

# 保存结果
recovery_nodes.to_csv('industry_recovery_nodes.csv', index=False)
print("\n复苏节点已保存到 industry_recovery_nodes.csv")
