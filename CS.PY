from quant_framework.data.mysql_data_provider import create_mysql_provider, DataManager
from quant_framework.backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy, RSIStrategy
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

# 设置plotly渲染方式为浏览器
pio.renderers.default = 'browser'

# 创建数据提供者
provider = create_mysql_provider()
manager = DataManager(provider)

# 获取股票列表
symbols = manager.get_available_symbols()

# 加载数据
df = manager.load_data(['1'], '2024-01-01', '2024-12-31')

# 计算技术指标
df = manager.calculate_technical_indicators(df)

# 创建策略并生成信号
strategy = RSIStrategy(rsi_period=14, oversold=30, overbought=70)
df_with_signals = strategy.generate_signals(df)

# 查看信号情况
print("\n信号情况:")
print(df_with_signals[['date', 'close', 'rsi', 'signal']].head(20))
print(f"\n总信号数: {df_with_signals['signal'].abs().sum()}")

# 回测
engine = BacktestEngine(strategy)
result = engine.run(df)

# 输出回测结果
print("回测结果:")
print(f"总收益率: {result.total_return:.2%}")
print(f"年化收益率: {result.annual_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown:.2%}")
print(f"总交易次数: {result.total_trades}")
print(f"胜率: {result.win_rate:.2%}")
print(f"盈亏比: {result.profit_factor:.2f}")

# 可视化回测结果
def visualize_backtest(df, trades, result):
    """可视化回测结果"""
    # 创建一个plotly图表
    fig = go.Figure()
    
    # 绘制收盘价曲线
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        mode='lines',
        name='收盘价',
        line=dict(color='blue', width=2),
        hovertemplate=
        '<b>日期:</b> %{x}<br>' +
        '<b>收盘价:</b> %{y:.2f}<br>' +
        '<b>开盘价:</b> %{customdata[0]:.2f}<br>' +
        '<b>成交额:</b> %{customdata[1]:.2f}<br>',
        customdata=list(zip(df['open'], df['amount']))
    ))
    
    # 标记买卖点
    buy_signals = []
    sell_signals = []
    
    for trade in trades:
        if trade.action == 'buy':
            buy_signals.append((trade.date, trade.price))
        elif trade.action == 'sell':
            sell_signals.append((trade.date, trade.price))
    
    # 绘制买点（红色加粗）
    if buy_signals:
        buy_dates, buy_prices = zip(*buy_signals)
        fig.add_trace(go.Scatter(
            x=buy_dates,
            y=buy_prices,
            mode='markers',
            name='买点',
            marker=dict(color='red', symbol='triangle-up', size=12, line=dict(width=2)),
            hovertemplate='<b>买点</b><br>日期: %{x}<br>价格: %{y:.2f}<br>'
        ))
    
    # 绘制卖点（绿色加粗）
    if sell_signals:
        sell_dates, sell_prices = zip(*sell_signals)
        fig.add_trace(go.Scatter(
            x=sell_dates,
            y=sell_prices,
            mode='markers',
            name='卖点',
            marker=dict(color='green', symbol='triangle-down', size=12, line=dict(width=2)),
            hovertemplate='<b>卖点</b><br>日期: %{x}<br>价格: %{y:.2f}<br>'
        ))
    
    # 设置图表标题和标签
    fig.update_layout(
        title='回测结果',
        xaxis_title='日期',
        yaxis_title='收盘价',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    
    # 添加回测结果注释
    text_str = f"总收益率: {result.total_return:.2%}<br>" \
               f"年化收益率: {result.annual_return:.2%}<br>" \
               f"夏普比率: {result.sharpe_ratio:.2f}<br>" \
               f"最大回撤: {result.max_drawdown:.2%}<br>" \
               f"总交易次数: {result.total_trades}<br>" \
               f"胜率: {result.win_rate:.2%}<br>" \
               f"盈亏比: {result.profit_factor:.2f}"
    
    fig.add_annotation(
        x=1,
        y=0,
        xref='paper',
        yref='paper',
        text=text_str,
        showarrow=False,
        align='right',
        bgcolor='white',
        bordercolor='black',
        borderwidth=1,
        borderpad=10,
        font=dict(size=12)
    )
    
    # 显示图表
    fig.show()
    
    # 保存图表为HTML文件
    fig.write_html('backtest_results.html')
    print("图表已保存为 backtest_results.html")


# 限制输出的行数
pd.options.display.max_rows = 20

# 可视化回测结果
visualize_backtest(df, result.trades, result)