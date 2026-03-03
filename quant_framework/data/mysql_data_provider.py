"""
MySQL数据库数据提供者
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pymysql
from data.data_provider import DataProvider, DataManager


class MySQLDataProvider(DataProvider):
    """MySQL数据库数据提供者"""
    
    def __init__(self, host='localhost', port=3306, user='root', 
                 password='123456', database='metabase', table_name='akshare'):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.table_name = table_name
        self.conn = None
    
    def _connect(self):
        """连接到数据库"""
        try:
            print("正在连接数据库...")
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def fetch_data(self, symbols: list, start_date: str, end_date: str, 
                  interval: str = '1d') -> pd.DataFrame:
        """从MySQL数据库获取数据"""
        print("开始fetch_data方法...")
        if not self.conn:
            print("连接不存在，正在重新连接...")
            self._connect()
        
        # 构建SQL查询
        symbol_condition = ""
        if symbols:
            symbol_list = [f"'{symbol}'" for symbol in symbols]
            symbol_str = ",".join(symbol_list)
            symbol_condition = f" AND `股票代码` IN ({symbol_str})"
        
        # 简化查询，只查询必要的字段
        # 测试时限制为100条，正式交付时取消限制
        # limit_clause = "LIMIT 100"  # 测试时使用
        limit_clause = ""  # 正式交付时使用
        
        query = f"""
        SELECT 
            `日期` as date,
            `股票代码` as symbol,
            `开盘` as open,
            `收盘` as close,
            `最高` as high,
            `最低` as low,
            `成交额` as amount
        FROM 
            {self.table_name}
        WHERE 
            `日期` >= '{start_date}' 
            AND `日期` <= '{end_date}'
            {symbol_condition}
        {limit_clause}
        """
        
        print(f"执行SQL查询: {query}")
        
        try:
            # 使用pymysql执行查询
            print("开始执行SQL查询...")
            cursor = self.conn.cursor()
            print("游标创建成功")
            
            try:
                # 执行查询
                print("准备执行查询...")
                cursor.execute(query)
                print("查询执行成功")
                
                # 获取结果
                print("准备获取结果...")
                rows = cursor.fetchall()
                print(f"查询结果行数: {len(rows)}")
                
                # 关闭游标
                cursor.close()
                print("游标关闭成功")
                
                if not rows:
                    print("❌ 没有查询到数据")
                    return pd.DataFrame()
                
                # 转换为DataFrame
                columns = ['date', 'symbol', 'open', 'close', 'high', 'low', 'amount']
                df = pd.DataFrame(rows, columns=columns)
                
                print(f"数据获取成功，原始数据形状: {df.shape}")
                print(f"原始数据列: {list(df.columns)}")
                print(f"原始数据前3行: {rows[:3]}")
                
                # 数据类型转换
                print("开始数据类型转换...")
                df['symbol'] = df['symbol'].astype(str)
                print("symbol字段转换成功")
                
                # 处理日期字段
                try:
                    df['date'] = pd.to_datetime(df['date'])
                    print("date字段转换成功")
                except Exception as e:
                    print(f"date字段转换失败: {str(e)}")
                    # 如果日期转换失败，使用原始值
                    pass
                
                # 处理数值字段
                numeric_fields = ['open', 'close', 'high', 'low', 'amount']
                for field in numeric_fields:
                    try:
                        df[field] = pd.to_numeric(df[field], errors='coerce')
                        print(f"{field}字段转换成功")
                    except Exception as e:
                        print(f"{field}字段转换失败: {str(e)}")
                        # 如果数值转换失败，使用原始值
                        pass
                
                # 按日期排序
                if 'date' in df.columns:
                    df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
                    print("数据排序成功")
                
                print(f"✅ 数据处理成功: {df.shape[0]} 条记录")
                print(f"处理后数据形状: {df.shape}")
                print(f"处理后数据列: {list(df.columns)}")
                print(f"数据前5行:")
                print(df.head())
                return df
            except Exception as e:
                print(f"❌ 查询执行失败: {str(e)}")
                import traceback
                traceback.print_exc()
                cursor.close()
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ 数据获取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_stock_list(self) -> list:
        """从数据库获取股票列表"""
        if not self.conn:
            self._connect()
        
        query = f"""
        SELECT DISTINCT `股票代码` 
        FROM {self.table_name}
        LIMIT 5
        """
        
        print(f"执行股票列表查询: {query}")
        
        try:
            # 使用pymysql执行查询
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            symbols = [str(row[0]) for row in rows]
            print(f"✅ 股票列表获取成功: {len(symbols)} 只股票")
            print(f"股票列表: {symbols}")
            return symbols
        except Exception as e:
            print(f"❌ 股票列表获取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


def test_mysql_connection():
    """测试MySQL数据库连接"""
    print("测试MySQL数据库连接...")
    
    try:
        # 创建数据提供者
        provider = MySQLDataProvider()
        manager = DataManager(provider)
        
        # 1. 获取股票列表
        print("\n1. 获取股票列表")
        symbols = manager.get_available_symbols()
        if symbols:
            print(f"   股票列表: {symbols}")
        else:
            print("   没有找到股票数据")
            return
        
        # 2. 加载数据
        print("\n2. 加载数据")
        start_date = '1991-04-01'
        end_date = '1991-04-10'
        
        # 只取前1只股票测试
        test_symbols = symbols[:1] if len(symbols) >= 1 else symbols
        print(f"   测试股票: {test_symbols}")
        
        df = manager.load_data(test_symbols, start_date, end_date)
        
        if not df.empty:
            print(f"\n3. 数据处理")
            print(f"   数据形状: {df.shape}")
            print(f"   数据字段: {list(df.columns)}")
            print(f"   数据预览:")
            print(df)
            
            # 4. 计算技术指标
            print("\n4. 计算技术指标")
            df_with_indicators = manager.calculate_technical_indicators(df)
            print("   技术指标计算成功")
            print("   技术指标数据:")
            print(df_with_indicators[['symbol', 'date', 'close', 'ma5', 'rsi', 'macd']].head())
            
        else:
            print("   没有获取到数据")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def create_mysql_provider():
    """创建MySQL数据提供者"""
    return MySQLDataProvider()


def simple_test():
    """简单测试"""
    print("简单测试MySQL数据提供者...")
    
    try:
        # 创建数据提供者
        provider = create_mysql_provider()
        
        # 获取股票列表
        symbols = provider.get_stock_list()
        print(f"股票列表: {symbols}")
        
        # 加载数据
        if symbols:
            print("开始加载数据...")
            df = provider.fetch_data([symbols[0]], '1991-04-01', '1991-04-10')
            print(f"数据形状: {df.shape}")
            print(f"数据预览:")
            print(df)
        
        print("✅ 简单测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 检查依赖包
    try:
        import pymysql
        print("✅ 依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {str(e)}")
        print("请运行: pip install pymysql")
        sys.exit(1)
    
    simple_test()
