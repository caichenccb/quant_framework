"""
测试数据加载和回测
"""

import sys
import os

# 添加正确的路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quant_framework'))

from data.mysql_data_provider import create_mysql_provider, DataManager
from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy


def test_data_and_backtest():
    """测试数据加载和回测"""
    print("测试数据加载和回测...")
    
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
        
        print(f"   股票列表: {symbols}")
        
        # 加载数据
        print("\n2. 加载数据")
        start_date = '1991-04-01'
        end_date = '1991-04-10'
        
        df = manager.load_data([symbols[0]], start_date, end_date)
        
        if df.empty:
            print("❌ 没有获取到数据")
            return
        
        print(f"   数据形状: {df.shape}")
        print(f"   数据字段: {list(df.columns)}")
        print(f"   数据行数: {len(df)}")
        
        # 计算技术指标
        print("\n3. 计算技术指标")
        df = manager.calculate_technical_indicators(df)
        print("   技术指标计算成功")
        
        # 创建策略和回测引擎
        print("\n4. 创建策略和回测引擎")
        strategy = MovingAverageCrossStrategy(short_window=3, long_window=5)
        engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)
        
        # 运行回测
        print("\n5. 运行回测")
        result = engine.run(df, initial_cash=100000)
        
        # 显示回测结果
        print("\n6. 回测结果")
        print(f"   总收益率: {result.total_return:.2%}")
        print(f"   年化收益率: {result.annual_return:.2%}")
        print(f"   夏普比率: {result.sharpe_ratio:.2f}")
        print(f"   最大回撤: {result.max_drawdown:.2%}")
        print(f"   总交易次数: {result.total_trades}")
        
        print("\n✅ 测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_data_and_backtest()
