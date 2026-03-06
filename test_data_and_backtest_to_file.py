"""
测试数据加载和回测，并将结果输出到文件
"""

import sys
import os

# 添加正确的路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quant_framework'))

from data.mysql_data_provider import create_mysql_provider, DataManager
from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy


def test_data_and_backtest():
    """测试数据加载和回测"""
    # 打开输出文件
    with open('test_results.txt', 'w', encoding='utf-8') as f:
        # 写入测试开始信息
        f.write("测试数据加载和回测...\n\n")
        
        try:
            # 创建MySQL数据提供者
            f.write("创建MySQL数据提供者...\n")
            provider = create_mysql_provider()
            manager = DataManager(provider)
            f.write("✅ MySQL数据提供者创建成功\n\n")
            
            # 获取股票列表
            f.write("1. 获取股票列表\n")
            symbols = manager.get_available_symbols()
            if not symbols:
                f.write("❌ 没有找到股票数据\n")
                return
            
            f.write(f"   股票列表: {symbols}\n\n")
            
            # 加载数据
            f.write("2. 加载数据\n")
            start_date = '1991-04-01'
            end_date = '1991-04-10'
            
            df = manager.load_data([symbols[0]], start_date, end_date)
            
            if df.empty:
                f.write("❌ 没有获取到数据\n")
                return
            
            f.write(f"   数据形状: {df.shape}\n")
            f.write(f"   数据字段: {list(df.columns)}\n")
            f.write(f"   数据行数: {len(df)}\n")
            f.write(f"   数据预览:\n{df.to_string()}\n\n")
            
            # 计算技术指标
            f.write("3. 计算技术指标\n")
            df = manager.calculate_technical_indicators(df)
            f.write("   技术指标计算成功\n")
            f.write(f"   技术指标数据:\n{df[['symbol', 'date', 'close', 'ma5', 'rsi', 'macd']].to_string()}\n\n")
            
            # 创建策略和回测引擎
            f.write("4. 创建策略和回测引擎\n")
            strategy = MovingAverageCrossStrategy(short_window=3, long_window=5)
            engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)
            f.write("   策略和回测引擎创建成功\n\n")
            
            # 运行回测
            f.write("5. 运行回测\n")
            result = engine.run(df, initial_cash=100000)
            f.write("   回测运行成功\n\n")
            
            # 显示回测结果
            f.write("6. 回测结果\n")
            f.write(f"   总收益率: {result.total_return:.2%}\n")
            f.write(f"   年化收益率: {result.annual_return:.2%}\n")
            f.write(f"   夏普比率: {result.sharpe_ratio:.2f}\n")
            f.write(f"   最大回撤: {result.max_drawdown:.2%}\n")
            f.write(f"   总交易次数: {result.total_trades}\n")
            f.write(f"   胜率: {result.win_rate:.2%}\n")
            f.write(f"   盈亏比: {result.profit_factor:.2f}\n")
            
            f.write("\n✅ 测试通过！\n")
            
        except Exception as e:
            f.write(f"❌ 测试失败: {str(e)}\n")
            import traceback
            traceback.print_exc(file=f)


if __name__ == "__main__":
    test_data_and_backtest()
    print("测试完成，结果已输出到 test_results.txt 文件")
