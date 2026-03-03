"""
使用MySQL数据进行策略回测示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mysql_data_provider import create_mysql_provider, DataManager
from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy


def run_backtest_with_mysql_data():
    """使用MySQL数据运行回测"""
    print("使用MySQL数据运行回测...")
    
    try:
        # 创建MySQL数据提供者
        provider = create_mysql_provider()
        manager = DataManager(provider)
        
        # 获取股票列表
        print("\n1. 获取股票列表")
        symbols = manager.get_available_symbols()
        if not symbols:
            print("❌ 没有找到股票数据")
            return
        
        print(f"   股票数量: {len(symbols)}")
        print(f"   前5只股票: {symbols[:5]}")
        
        # 选择一只股票进行回测
        test_symbol = symbols[0]
        print(f"\n2. 选择股票: {test_symbol}")
        
        # 加载数据
        print("\n3. 加载数据")
        start_date = '2025-07-01'
        end_date = '2025-07-31'
        
        print(f"   时间范围: {start_date} 至 {end_date}")
        df = manager.load_data([test_symbol], start_date, end_date)
        
        if df.empty:
            print("❌ 没有获取到数据")
            return
        
        print(f"   数据形状: {df.shape}")
        print(f"   数据预览:")
        print(df.head())
        
        # 计算技术指标
        print("\n4. 计算技术指标")
        df = manager.calculate_technical_indicators(df)
        print("   技术指标计算成功")
        
        # 创建策略
        print("\n5. 创建策略")
        strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)
        print(f"   策略: 移动平均交叉策略")
        print(f"   参数: 短期均线={strategy.short_window}, 长期均线={strategy.long_window}")
        
        # 创建回测引擎
        print("\n6. 创建回测引擎")
        engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)
        print(f"   交易成本: 手续费=0.1%, 滑点=0.1%")
        
        # 运行回测
        print("\n7. 运行回测")
        initial_cash = 100000
        print(f"   初始资金: {initial_cash:,.2f}")
        
        result = engine.run(df, initial_cash=initial_cash)
        
        # 显示回测结果
        print("\n8. 回测结果")
        print(f"   总收益率: {result.total_return:.2%}")
        print(f"   年化收益率: {result.annual_return:.2%}")
        print(f"   夏普比率: {result.sharpe_ratio:.2f}")
        print(f"   最大回撤: {result.max_drawdown:.2%}")
        print(f"   交易次数: {result.total_trades}")
        
        # 显示交易明细
        if result.trades:
            print("\n9. 交易明细")
            print(f"   总交易次数: {len(result.trades)}")
            print(f"   最近5笔交易:")
            for i, trade in enumerate(result.trades[-5:], 1):
                print(f"   {i}. {trade.date} {trade.symbol} {trade.action} {trade.shares}股 @ {trade.price:.2f}")
        
        print("\n✅ 回测完成！")
        
    except Exception as e:
        print(f"❌ 回测失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_backtest_with_mysql_data()
