"""
数据获取模块
支持从不同数据源获取股票、期货等金融数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class DataProvider:
    """数据提供者基类"""
    
    def __init__(self):
        self.data = None
        self.symbols = []
    
    def fetch_data(self, symbols: List[str], start_date: str, end_date: str, 
                  interval: str = '1d') -> pd.DataFrame:
        """
        获取数据
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            interval: 数据间隔 (1d, 1h, 30m, 15m, 5m, 1m)
        
        Returns:
            包含所有股票数据的DataFrame
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def get_stock_list(self) -> List[str]:
        """获取股票列表"""
        raise NotImplementedError("子类必须实现此方法")


class MockDataProvider(DataProvider):
    """模拟数据提供者，用于测试"""
    
    def __init__(self):
        super().__init__()
        np.random.seed(42)
    
    def fetch_data(self, symbols: List[str], start_date: str, end_date: str, 
                  interval: str = '1d') -> pd.DataFrame:
        """生成模拟的股票数据"""
        all_data = []
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        dates = pd.date_range(start=start, end=end, freq='D')
        
        for symbol in symbols:
            for date in dates:
                # 生成随机价格数据
                base_price = np.random.uniform(10, 100)
                open_price = base_price * (1 + np.random.uniform(-0.02, 0.02))
                high_price = open_price * (1 + np.random.uniform(0, 0.05))
                low_price = open_price * (1 - np.random.uniform(0, 0.05))
                close_price = open_price * (1 + np.random.uniform(-0.03, 0.03))
                volume = np.random.randint(100000, 10000000)
                
                all_data.append({
                    'symbol': symbol,
                    'date': date,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })
        
        df = pd.DataFrame(all_data)
        df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
        return df
    
    def get_stock_list(self) -> List[str]:
        """返回模拟的股票列表"""
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'INTC', 'AMD']


class DatabaseDataProvider(DataProvider):
    """数据库数据提供者"""
    
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    def fetch_data(self, symbols: List[str], start_date: str, end_date: str, 
                  interval: str = '1d') -> pd.DataFrame:
        """从数据库数据中获取指定股票和日期范围的数据"""
        # 转换日期格式
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # 过滤数据
        filtered_data = []
        
        for item in self.data:
            # 检查股票代码是否在指定列表中
            if str(item['股票代码']) not in symbols:
                continue
            
            # 检查日期是否在指定范围内
            date = pd.to_datetime(item['日期'])
            if not (start <= date <= end):
                continue
            
            # 构建数据结构
            filtered_data.append({
                'symbol': str(item['股票代码']),
                'date': date,
                'open': float(item['开盘']),
                'high': float(item['最高']),
                'low': float(item['最低']),
                'close': float(item['收盘']),
                'volume': int(item['成交量']),
                'amount': float(item['成交额']),  # 额外字段
                'name': item['名字'],  # 额外字段
                'industry': item['行业']  # 额外字段
            })
        
        df = pd.DataFrame(filtered_data)
        df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
        return df
    
    def get_stock_list(self) -> List[str]:
        """从数据库数据中获取股票列表"""
        if not self.data:
            return []
        
        # 提取所有唯一的股票代码
        stock_codes = set()
        for item in self.data:
            stock_codes.add(str(item['股票代码']))
        
        return list(stock_codes)


class DataManager:
    """数据管理器"""
    
    def __init__(self, provider: DataProvider):
        self.provider = provider
        self.cache = {}
    
    def load_data(self, symbols: List[str], start_date: str, end_date: str, 
                 interval: str = '1d', use_cache: bool = True) -> pd.DataFrame:
        """
        加载数据
        
        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            interval: 数据间隔
            use_cache: 是否使用缓存
        
        Returns:
            包含所有股票数据的DataFrame
        """
        cache_key = f"{'_'.join(sorted(symbols))}_{start_date}_{end_date}_{interval}"
        
        if use_cache and cache_key in self.cache:
            print(f"使用缓存数据: {cache_key}")
            return self.cache[cache_key]
        
        print(f"从数据源获取数据: {symbols}")
        df = self.provider.fetch_data(symbols, start_date, end_date, interval)
        
        if use_cache:
            self.cache[cache_key] = df
        
        return df
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        print("缓存已清空")
    
    def get_available_symbols(self) -> List[str]:
        """获取可用的股票代码列表"""
        return self.provider.get_stock_list()
    
    def calculate_returns(self, df: pd.DataFrame, period: int = 1) -> pd.DataFrame:
        """
        计算收益率
        
        Args:
            df: 包含价格数据的DataFrame
            period: 计算周期
        
        Returns:
            添加了收益率列的DataFrame
        """
        df = df.copy()
        df = df.sort_values(['symbol', 'date'])
        
        df['return'] = df.groupby('symbol')['close'].pct_change(period)
        df['log_return'] = np.log(df['close'] / df.groupby('symbol')['close'].shift(period))
        
        return df
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 包含OHLCV数据的DataFrame
        
        Returns:
            添加了技术指标的DataFrame
        """
        df = df.copy()
        df = df.sort_values(['symbol', 'date'])
        
        # 移动平均线
        df['ma5'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=5).mean())
        df['ma10'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=10).mean())
        df['ma20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=20).mean())
        
        # RSI
        def calculate_rsi(series, period=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        df['rsi'] = df.groupby('symbol')['close'].transform(calculate_rsi)
        
        # MACD
        def calculate_macd(series):
            exp12 = series.ewm(span=12, adjust=False).mean()
            exp26 = series.ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9, adjust=False).mean()
            return macd, signal
        
        # 分别计算MACD和信号线
        macd_list = []
        signal_list = []
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol]['close'].reset_index(drop=True)
            macd, signal = calculate_macd(symbol_data)
            macd_list.extend(macd.tolist())
            signal_list.extend(signal.tolist())
        
        df['macd'] = macd_list
        df['macd_signal'] = signal_list
        
        # 布林带
        df['bb_middle'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=20).mean())
        df['bb_std'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window=20).std())
        df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']
        
        return df


def create_database_provider_from_sample():
    """从示例数据创建数据库提供者"""
    # 示例数据
    sample_data = [
        {
            '日期': '2025-07-28',
            '股票代码': 920108,
            '开盘': 18.04,
            '收盘': 18.71,
            '最高': 18.93,
            '最低': 17.99,
            '成交量': 147670,
            '成交额': 26920398.11,
            '振幅': 1.72,
            '涨跌幅': 0.39,
            '涨跌额': 0.07,
            '换手率': 4.53,
            '名字': '安科科技',
            '行业': '电气设备',
            '代码修正': 920108
        },
        {
            '日期': '2025-07-28',
            '股票代码': 920116,
            '开盘': 28.58,
            '收盘': 28.2,
            '最高': 29.3,
            '最低': 28.59,
            '成交量': 10178,
            '成交额': 29474351.62,
            '振幅': 1.22,
            '涨跌幅': 0.9,
            '涨跌额': 0.25,
            '换手率': 2.76,
            '名字': '荣科科技',
            '行业': '电网设备',
            '代码修正': 920116
        },
        {
            '日期': '2025-07-28',
            '股票代码': 920116,
            '开盘': 69.59,
            '收盘': 69.35,
            '最高': 71.17,
            '最低': 68.59,
            '成交量': 23304,
            '成交额': 6231014.77,
            '振幅': 3.69,
            '涨跌幅': -0.9,
            '涨跌额': -0.63,
            '换手率': 6.37,
            '名字': '星图测控',
            '行业': '航空航天',
            '代码修正': 920116
        }
    ]
    
    return DatabaseDataProvider(sample_data)


if __name__ == "__main__":
    # 测试数据库数据提供者
    provider = create_database_provider_from_sample()
    manager = DataManager(provider)
    
    # 获取股票列表
    symbols = manager.get_available_symbols()
    print(f"可用股票: {symbols}")
    
    # 加载数据
    end_date = '2025-07-28'
    start_date = '2025-07-28'
    
    df = manager.load_data(symbols, start_date, end_date)
    print(f"\n数据形状: {df.shape}")
    print(f"数据预览:\n{df.head()}")
    
    # 计算收益率
    df = manager.calculate_returns(df)
    print(f"\n收益率数据:\n{df[['symbol', 'date', 'close', 'return']].head()}")
    
    # 计算技术指标
    df = manager.calculate_technical_indicators(df)
    print(f"\n技术指标数据:\n{df[['symbol', 'date', 'close', 'ma5', 'ma10', 'rsi']].head()}")
