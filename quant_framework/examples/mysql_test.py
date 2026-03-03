"""
MySQL数据连接示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mysql_data_provider import create_mysql_provider, DataManager


def test_mysql_data_connection():
    """测试MySQL数据连接"""
    print("测试MySQL数据连接...")
    
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
        print(f"   前3只股票: {symbols[:3]}")
        
        # 选择一只股票
        test_symbol = symbols[0]
        print(f"\n2. 选择股票: {test_symbol}")
        
        # 加载数据
        print("\n3. 加载数据")
        start_date = '1991-04-01'
        end_date = '1991-04-10'
        
        print(f"   时间范围: {start_date} 至 {end_date}")
        df = manager.load_data([test_symbol], start_date, end_date)
        
        if df.empty:
            print("❌ 没有获取到数据")
            return
        
        print(f"   数据形状: {df.shape}")
        print(f"   数据字段: {list(df.columns)}")
        print(f"   数据预览:")
        print(df)
        
        # 计算技术指标
        print("\n4. 计算技术指标")
        df = manager.calculate_technical_indicators(df)
        print("   技术指标计算成功")
        print(f"   技术指标字段: {[col for col in df.columns if col in ['ma5', 'ma10', 'ma20', 'rsi', 'macd', 'bb_middle']]}")
        
        print("\n✅ 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_mysql_data_connection()
