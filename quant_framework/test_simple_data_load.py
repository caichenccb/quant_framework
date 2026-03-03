"""
简单测试MySQL数据加载
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mysql_data_provider import create_mysql_provider, DataManager


def test_simple_data_load():
    """简单测试MySQL数据加载"""
    print("简单测试MySQL数据加载...")
    
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
        print(f"   数据前5行:")
        print(df.head())
        
        # 检查数据类型
        print("\n3. 检查数据类型")
        print(df.dtypes)
        
        # 检查数据统计
        print("\n4. 数据统计")
        print(df.describe())
        
        print("\n✅ 测试通过！数据加载成功")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_simple_data_load()
