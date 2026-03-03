"""
示例策略：双均线策略
展示如何使用量化框架
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from data.data_provider import DataManager, MockDataProvider
from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy, print_backtest_results
from risk.risk_manager import RiskManager, print_risk_metrics


class DualMovingAverageStrategy(MovingAverageCrossStrategy):
    """
    双均线策略
    短期均线上穿长期均线时买入，下穿时卖出
    """
    
    def __init__(self, short_window: int = 5, long_window: int = 20,
                 stop_loss_pct: float = 0.05, take_profit_pct: float = 0.10):
        super().__init__(short_window, long_window)
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
    
    def on_bar(self, bar_data: pd.Series):
        """
        每个bar触发的回调函数
        可以在这里添加止损止盈逻辑
        """
        symbol = bar_data['symbol']
        if symbol in self.positions:
            position = self.positions[symbol]
            current_price = bar_data['close']
            
            # 计算止损止盈价格
            stop_loss = position.entry_price * (1 - self.stop_loss_pct)
            take_profit = position.entry_price * (1 + self.take_profit_pct)
            
            # 检查是否需要止损止盈
            if current_price <= stop_loss:
                print(f"{bar_data['date']} {symbol} 触发止损: {current_price:.2f}")
            elif current_price >= take_profit:
                print(f"{bar_data['date']} {symbol} 触发止盈: {current_price:.2f}")


def run_backtest_example():
    """运行回测示例"""
    print("="*60)
    print("双均线策略回测示例")
    print("="*60)
    
    # 1. 准备数据
    print("\n1. 准备数据...")
    provider = MockDataProvider()
    data_manager = DataManager(provider)
    
    # 选择测试股票
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    print(f"测试股票: {symbols}")
    
    # 设置时间范围
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    print(f"回测期间: {start_date} 至 {end_date}")
    
    # 加载数据
    df = data_manager.load_data(symbols, start_date, end_date)
    print(f"数据加载完成: {df.shape[0]} 条记录")
    
    # 计算技术指标
    df = data_manager.calculate_technical_indicators(df)
    print(f"技术指标计算完成")
    
    # 2. 创建策略
    print("\n2. 创建策略...")
    strategy = DualMovingAverageStrategy(
        short_window=5,
        long_window=20,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    print(f"策略参数: 短期均线={strategy.short_window}, 长期均线={strategy.long_window}")
    print(f"风险控制: 止损={strategy.stop_loss_pct:.1%}, 止盈={strategy.take_profit_pct:.1%}")
    
    # 3. 创建回测引擎
    print("\n3. 创建回测引擎...")
    engine = BacktestEngine(
        strategy,
        commission=0.001,  # 0.1% 手续费
        slippage=0.001   # 0.1% 滑点
    )
    print(f"交易成本: 手续费={engine.commission:.1%}, 滑点={engine.slippage:.1%}")
    
    # 4. 运行回测
    print("\n4. 运行回测...")
    initial_cash = 100000
    print(f"初始资金: {initial_cash:,.2f}")
    
    result = engine.run(df, initial_cash=initial_cash)
    
    # 5. 显示回测结果
    print_backtest_results(result)
    
    # 6. 风险分析
    print("\n5. 风险分析...")
    if len(result.equity_curve) > 1:
        returns = result.equity_curve.pct_change().dropna()
        risk_manager = RiskManager()
        risk_metrics = risk_manager.calculate_risk_metrics(returns)
        print_risk_metrics(risk_metrics)
    
    # 7. 交易明细
    print("\n6. 交易明细...")
    if result.trades:
        trades_df = pd.DataFrame([{
            'symbol': t.symbol,
            'action': t.action,
            'shares': t.shares,
            'price': t.price,
            'date': t.date,
            'commission': t.commission
        } for t in result.trades])
        
        print(f"\n总交易次数: {len(result.trades)}")
        print(f"买入次数: {len(trades_df[trades_df['action'] == 'buy'])}")
        print(f"卖出次数: {len(trades_df[trades_df['action'] == 'sell'])}")
        print(f"\n最近10笔交易:")
        print(trades_df.tail(10).to_string(index=False))
    
    # 8. 权益曲线
    print("\n7. 权益曲线...")
    equity_df = pd.DataFrame(result.equity_curve)
    print(equity_df.describe())
    
    return result


def compare_strategies():
    """比较不同策略"""
    print("\n" + "="*60)
    print("策略比较")
    print("="*60)
    
    # 准备数据
    provider = MockDataProvider()
    data_manager = DataManager(provider)
    
    symbols = ['AAPL', 'MSFT']
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    df = data_manager.load_data(symbols, start_date, end_date)
    df = data_manager.calculate_technical_indicators(df)
    
    # 比较不同的均线参数
    strategies = [
        ("快线(5/20)", MovingAverageCrossStrategy(5, 20)),
        ("中线(10/30)", MovingAverageCrossStrategy(10, 30)),
        ("慢线(20/50)", MovingAverageCrossStrategy(20, 50)),
    ]
    
    results = []
    for name, strategy in strategies:
        print(f"\n回测策略: {name}")
        engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)
        result = engine.run(df, initial_cash=100000)
        results.append({
            '策略': name,
            '总收益率': result.total_return,
            '年化收益率': result.annual_return,
            '夏普比率': result.sharpe_ratio,
            '最大回撤': result.max_drawdown,
            '交易次数': result.total_trades
        })
    
    # 显示比较结果
    print("\n" + "="*60)
    print("策略比较结果")
    print("="*60)
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    return results_df


def run_risk_analysis():
    """运行风险分析示例"""
    print("\n" + "="*60)
    print("风险分析示例")
    print("="*60)
    
    # 生成模拟收益率数据
    np.random.seed(42)
    
    # 生成不同波动率的收益率
    scenarios = {
        '低波动': np.random.normal(0.0005, 0.01, 252),
        '中波动': np.random.normal(0.001, 0.02, 252),
        '高波动': np.random.normal(0.0015, 0.03, 252),
    }
    
    from risk.risk_manager import RiskManager
    risk_manager = RiskManager()
    
    results = []
    for name, returns in scenarios.items():
        returns_series = pd.Series(returns)
        metrics = risk_manager.calculate_risk_metrics(returns_series)
        
        results.append({
            '场景': name,
            '波动率': f"{metrics.volatility:.2%}",
            '95% VaR': f"{metrics.var_95:.2%}",
            '最大回撤': f"{metrics.max_drawdown:.2%}",
            '夏普比率': f"{metrics.sharpe_ratio:.2f}",
            '风险等级': metrics.risk_level.value
        })
    
    # 显示结果
    print("\n不同风险场景对比:")
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    # 运行回测示例
    result = run_backtest_example()
    
    # 比较不同策略
    compare_strategies()
    
    # 风险分析
    run_risk_analysis()
    
    print("\n" + "="*60)
    print("示例运行完成！")
    print("="*60)
    print("\n您可以根据需要修改以下内容:")
    print("1. 数据源: 替换 MockDataProvider 为真实的数据提供者")
    print("2. 策略参数: 调整均线周期、止损止盈等参数")
    print("3. 交易成本: 调整手续费和滑点设置")
    print("4. 风险控制: 调整最大回撤、单笔交易风险等")
    print("5. 技术指标: 添加或修改技术指标计算")
    print("\n祝您量化投资顺利！")
