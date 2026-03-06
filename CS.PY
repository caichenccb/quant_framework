from quant_framework.data.mysql_data_provider import create_mysql_provider, DataManager
from quant_framework.backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy, RSIStrategy, MACDStrategy, BollingerBandsStrategy, KDJStrategy, VolumeStrategy, MomentumStrategy, IndustryStrategy
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

# 设置plotly渲染方式为浏览器8

pio.renderers.default = 'browser'

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

# 创建数据提供者
provider = create_mysql_provider()
manager = DataManager(provider)

# 策略类型选择
print("请选择策略类型：")
print("1. 股票策略")
print("2. 行业策略")

strategy_type = input("请输入策略类型编号：")

if strategy_type == "1":
    # 股票策略
    print("\n请选择股票策略：")
    print("1. 移动平均线交叉策略 (Moving Average Cross)")
    print("2. RSI策略")
    print("3. MACD策略")
    print("4. 布林带策略 (Bollinger Bands)")
    print("5. KDJ策略")
    print("6. 成交量策略")
    print("7. 动量策略")
    
    strategy_choice = input("请输入策略编号：")
    
    # 输入股票代码
    stock_code = input("请输入股票代码（示例：1）：")
    
    # 输入时间区间
    start_date = input("请输入开始日期（示例：2024-01-01）：")
    end_date = input("请输入结束日期（示例：2024-12-31）：")
    
    # 加载数据
    df = manager.load_data([stock_code], start_date, end_date)
    
    # 计算技术指标
    df = manager.calculate_technical_indicators(df)
    
    # 创建策略
    if strategy_choice == "1":
        short_window = int(input("请输入短期移动平均线周期："))
        long_window = int(input("请输入长期移动平均线周期："))
        strategy = MovingAverageCrossStrategy(short_window=short_window, long_window=long_window)
    elif strategy_choice == "2":
        rsi_period = int(input("请输入RSI周期："))
        oversold = float(input("请输入超卖阈值："))
        overbought = float(input("请输入超买阈值："))
        strategy = RSIStrategy(rsi_period=rsi_period, oversold=oversold, overbought=overbought)
    elif strategy_choice == "3":
        fast_period = int(input("请输入快速EMA周期："))
        slow_period = int(input("请输入慢速EMA周期："))
        signal_period = int(input("请输入信号线周期："))
        strategy = MACDStrategy(fast_period=fast_period, slow_period=slow_period, signal_period=signal_period)
    elif strategy_choice == "4":
        window = int(input("请输入布林带周期："))
        num_std = float(input("请输入标准差倍数："))
        strategy = BollingerBandsStrategy(window=window, num_std=num_std)
    elif strategy_choice == "5":
        period = int(input("请输入KDJ周期："))
        k_period = int(input("请输入K值周期："))
        d_period = int(input("请输入D值周期："))
        strategy = KDJStrategy(period=period, k_period=k_period, d_period=d_period)
    elif strategy_choice == "6":
        volume_period = int(input("请输入成交量移动平均线周期："))
        volume_ratio = float(input("请输入成交量放大比率："))
        strategy = VolumeStrategy(volume_period=volume_period, volume_ratio=volume_ratio)
    elif strategy_choice == "7":
        momentum_period = int(input("请输入动量周期："))
        strategy = MomentumStrategy(momentum_period=momentum_period)
    else:
        print("无效的策略选择，使用默认的RSI策略")
        strategy = RSIStrategy(rsi_period=14, oversold=30, overbought=70)
    
    # 生成信号
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
    visualize_backtest(df, result.trades, result)
    
elif strategy_type == "2":
    # 行业策略
    print("\n" + "="*80)
    print("行业周期分析策略")
    print("="*80)
    print("\n本策略通过以下维度判断行业复苏/衰退：")
    print("1. 价格动量（短期/中期/长期）")
    print("2. 资金流向（成交量/成交额）")
    print("3. 趋势强度（均线排列）")
    print("4. RSI超买超卖")
    print("5. 波动率")
    print("\n综合评分系统：")
    print("> 0.6: 强烈看多（买入）")
    print("0.3 ~ 0.6: 看多")
    print("-0.3 ~ 0.3: 中性")
    print("-0.6 ~ -0.3: 看空")
    print("< -0.6: 强烈看空（卖出）")
    print("="*80)
    
    # 输入时间区间
    start_date = input("\n请输入开始日期（示例：2024-01-01）：")
    end_date = input("请输入结束日期（示例：2024-12-31）：")
    
    # 加载所有股票数据
    print("\n加载所有股票数据...")
    symbols = manager.get_available_symbols()
    print(f"获取到 {len(symbols)} 只股票")
    
    # 限制股票数量，避免数据量过大
    max_symbols = 50
    if len(symbols) > max_symbols:
        symbols = symbols[:max_symbols]
        print(f"限制股票数量为 {max_symbols} 只")
    
    # 加载数据
    df = manager.load_data(symbols, start_date, end_date)
    print(f"数据加载完成，共 {len(df)} 条记录")
    
    # 查看行业分布
    industry_distribution = df['industry'].value_counts()
    print("\n行业分布:")
    print(industry_distribution)
    
    # 创建行业策略（使用默认参数，无需用户输入）
    print("\n使用默认策略参数进行分析...")
    strategy = IndustryStrategy()
    
    # 回测
    engine = BacktestEngine(strategy)
    result = engine.run(df)
    
    # 输出回测结果
    print("\n" + "="*80)
    print("回测结果汇总")
    print("="*80)
    print(f"总收益率: {result.total_return:.2%}")
    print(f"年化收益率: {result.annual_return:.2%}")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"最大回撤: {result.max_drawdown:.2%}")
    print(f"总交易次数: {result.total_trades}")
    print(f"胜率: {result.win_rate:.2%}")
    print(f"盈亏比: {result.profit_factor:.2f}")
    print("="*80)
    
    # 输出交易明细表格
    if result.trades:
        print("\n" + "="*80)
        print("交易明细表")
        print("="*80)
        
        # 按行业分组统计交易
        trades_df = pd.DataFrame([
            {
                '日期': t.date.strftime('%Y-%m-%d') if hasattr(t.date, 'strftime') else str(t.date)[:10],
                '股票代码': t.symbol,
                '操作': '买入' if t.action == 'buy' else '卖出',
                '数量': t.shares,
                '价格': f"{t.price:.2f}",
                '金额': f"{t.shares * t.price:,.2f}",
                '手续费': f"{t.commission:.2f}"
            }
            for t in result.trades
        ])
        
        if not trades_df.empty:
            # 添加行业信息
            trades_df['行业'] = trades_df['股票代码'].map(
                df.drop_duplicates('symbol').set_index('symbol')['industry'].to_dict()
            )
            
            # 重新排列列顺序
            trades_df = trades_df[['日期', '行业', '股票代码', '操作', '数量', '价格', '金额', '手续费']]
            
            print(trades_df.to_string(index=False))
        print("="*80)
        
        # 输出行业买卖汇总
        print("\n" + "="*80)
        print("行业买卖汇总")
        print("="*80)
        
        buy_trades = trades_df[trades_df['操作'] == '买入']
        sell_trades = trades_df[trades_df['操作'] == '卖出']
        
        # 买入汇总
        if not buy_trades.empty:
            print("\n【买入记录】")
            buy_summary = buy_trades.groupby('行业').agg({
                '股票代码': 'count',
                '金额': lambda x: f"{sum([float(i.replace(',', '')) for i in x]):,.2f}"
            }).rename(columns={'股票代码': '买入次数', '金额': '买入金额'})
            print(buy_summary.to_string())
        
        # 卖出汇总
        if not sell_trades.empty:
            print("\n【卖出记录】")
            sell_summary = sell_trades.groupby('行业').agg({
                '股票代码': 'count',
                '金额': lambda x: f"{sum([float(i.replace(',', '')) for i in x]):,.2f}"
            }).rename(columns={'股票代码': '卖出次数', '金额': '卖出金额'})
            print(sell_summary.to_string())
        print("="*80)
    
    # 可视化回测结果
    visualize_backtest(df, result.trades, result)
else:
    print("无效的策略类型选择")
    exit(1)


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

