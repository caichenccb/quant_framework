import pandas as pd
import numpy as np

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
        # 为了生成更多复苏节点，设置更多行业有正趋势
        if i % 2 == 0:
            trend = 0.0005  # 正趋势
        else:
            trend = -0.0002  # 负趋势
        # 添加一些随机噪声，使价格波动更大
        noise = np.random.randn() * 5
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
    
    # 动量趋势型信号：20日收益率为正
    momentum_cond = industry_df['momentum_20'] > 0
    
    # 均值回归型信号：RSI低于阈值（超卖）
    rsi_cond = industry_df['rsi'] < 40
    
    # 综合信号
    industry_df.loc[momentum_cond & rsi_cond, 'signal'] = 1  # 行业开始复苏，买入
    
    # 输出各行业的复苏节点
    recovery_nodes = industry_df.loc[industry_df['signal'] == 1, ['date', 'industry', 'close', 'momentum_20', 'momentum_120', 'rsi']]
    
    return recovery_nodes

# 计算行业指标
print("\n计算行业指标...")
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
recovery_nodes.to_csv('industry_recovery_nodes_mock.csv', index=False)
print("\n复苏节点已保存到 industry_recovery_nodes_mock.csv")
