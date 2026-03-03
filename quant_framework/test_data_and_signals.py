"""
测试数据加载和信号生成
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mysql_data_provider import create_mysql_provider, DataManager
from backtesting.backtest_engine import MovingAverageCrossStrategy


def test_data_and_signals():
    """测试数据加载和信号生成"""
    print("测试数据加载和信号生成...")
    
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
        print(f"   第一只股票: {symbols[0]}")
        
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
        print(f"   数据预览:")
        print(df)
        
        # 检查数据类型
        print("\n3. 检查数据类型")
        print(df.dtypes)
        
        # 计算技术指标
        print("\n4. 计算技术指标")
        df = manager.calculate_technical_indicators(df)
        print("   技术指标计算成功")
        print(f"   技术指标数据:")
        print(df[['symbol', 'date', 'close', 'ma5', 'ma10', 'rsi', 'macd']])
        
        # 生成信号
        print("\n5. 生成信号")
        strategy = MovingAverageCrossStrategy(short_window=3, long_window=5)
        data_with_signals = strategy.generate_signals(df)
        print("   信号生成成功")
        print(f"   信号数据:")
        print(data_with_signals[['symbol', 'date', 'close', 'ma_short', 'ma_long', 'ma_diff', 'ma_diff_prev', 'signal']])
        
        # 检查信号
        print("\n6. 检查信号")
        print(f"   买入信号数量: {(data_with_signals['signal'] == 1).sum()}")
        print(f"   卖出信号数量: {(data_with_signals['signal'] == -1).sum()}")
        print(f"   持有信号数量: {(data_with_signals['signal'] == 0).sum()}")
        
        print("\n✅ 测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_data_and_signals()
