print("测试脚本开始执行...")

# 导入必要的库
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 测试导入
print("测试导入...")
try:
    from quant_framework.data.mysql_data_provider import create_mysql_provider
    from quant_framework.data.data_manager import DataManager
    from quant_framework.backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy, RSIStrategy, MACDStrategy, BollingerBandsStrategy, KDJStrategy, VolumeStrategy, MomentumStrategy
    print("✅ 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("测试脚本执行完成")
