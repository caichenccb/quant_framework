"""
策略回测模块
提供策略基类和回测引擎
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    shares: int
    entry_price: float
    entry_date: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Trade:
    """交易记录"""
    symbol: str
    action: str  # 'buy' or 'sell'
    shares: int
    price: float
    date: datetime
    commission: float = 0.0


@dataclass
class BacktestResult:
    """回测结果"""
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    equity_curve: pd.Series
    trades: List[Trade]


class Strategy:
    """策略基类"""
    
    def __init__(self, name: str = "BaseStrategy"):
        self.name = name
        self.positions = {}  # symbol -> Position
        self.trades = []
        self.cash = 0
        self.initial_cash = 0
    
    def initialize(self, data: pd.DataFrame, initial_cash: float = 100000):
        """
        初始化策略
        
        Args:
            data: 历史数据
            initial_cash: 初始资金
        """
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions = {}
        self.trades = []
        self.data = data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            data: 历史数据
        
        Returns:
            包含信号的DataFrame，需要包含 'signal' 列
            signal: 1=买入, -1=卖出, 0=持有
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def on_bar(self, bar_data: pd.Series):
        """
        每个bar触发的回调函数
        
        Args:
            bar_data: 当前bar的数据
        """
        pass
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        计算当前组合价值
        
        Args:
            current_prices: 当前价格字典 {symbol: price}
        
        Returns:
            组合总价值
        """
        portfolio_value = self.cash
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                portfolio_value += position.shares * current_prices[symbol]
        return portfolio_value


class MovingAverageCrossStrategy(Strategy):
    """移动平均线交叉策略"""
    
    def __init__(self, short_window: int = 5, long_window: int = 20):
        super().__init__("MovingAverageCross")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成移动平均线交叉信号"""
        data = data.copy()
        
        # 计算移动平均线
        data['ma_short'] = data.groupby('symbol')['close'].transform(
            lambda x: x.rolling(window=self.short_window).mean()
        )
        data['ma_long'] = data.groupby('symbol')['close'].transform(
            lambda x: x.rolling(window=self.long_window).mean()
        )
        
        # 生成信号
        data['ma_diff'] = data['ma_short'] - data['ma_long']
        data['ma_diff_prev'] = data.groupby('symbol')['ma_diff'].shift(1)
        
        # 交叉信号
        data['signal'] = 0
        data.loc[(data['ma_diff'] > 0) & (data['ma_diff_prev'] <= 0), 'signal'] = 1  # 金叉买入
        data.loc[(data['ma_diff'] < 0) & (data['ma_diff_prev'] >= 0), 'signal'] = -1  # 死叉卖出
        
        return data


class RSIStrategy(Strategy):
    """RSI策略"""
    
    def __init__(self, rsi_period: int = 14, oversold: float = 30, overbought: float = 70):
        super().__init__("RSI")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成RSI信号"""
        data = data.copy()
        
        # 计算RSI
        def calculate_rsi(series, period=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        data['rsi'] = data.groupby('symbol')['close'].transform(calculate_rsi)
        
        # 生成信号
        data['signal'] = 0
        data.loc[data['rsi'] < self.oversold, 'signal'] = 1  # 超卖买入
        data.loc[data['rsi'] > self.overbought, 'signal'] = -1  # 超买卖出
        
        return data


class MACDStrategy(Strategy):
    """MACD策略"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__("MACD")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成MACD信号"""
        data = data.copy()
        
        # 计算MACD
        def calculate_macd(series, fast_period=12, slow_period=26, signal_period=9):
            exp12 = series.ewm(span=fast_period, adjust=False).mean()
            exp26 = series.ewm(span=slow_period, adjust=False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=signal_period, adjust=False).mean()
            return macd, signal
        
        # 分别计算MACD和信号线
        macd_list = []
        signal_list = []
        for symbol in data['symbol'].unique():
            symbol_data = data[data['symbol'] == symbol]['close'].reset_index(drop=True)
            macd, signal = calculate_macd(symbol_data, self.fast_period, self.slow_period, self.signal_period)
            macd_list.extend(macd.tolist())
            signal_list.extend(signal.tolist())
        
        data['macd'] = macd_list
        data['macd_signal'] = signal_list
        data['macd_hist'] = data['macd'] - data['macd_signal']
        
        # 生成信号
        data['signal'] = 0
        data['macd_hist_prev'] = data.groupby('symbol')['macd_hist'].shift(1)
        data.loc[(data['macd_hist'] > 0) & (data['macd_hist_prev'] <= 0), 'signal'] = 1  # 金叉买入
        data.loc[(data['macd_hist'] < 0) & (data['macd_hist_prev'] >= 0), 'signal'] = -1  # 死叉卖出
        
        return data


class BollingerBandsStrategy(Strategy):
    """布林带策略"""
    
    def __init__(self, window: int = 20, num_std: float = 2):
        super().__init__("BollingerBands")
        self.window = window
        self.num_std = num_std
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成布林带信号"""
        data = data.copy()
        
        # 计算布林带
        data['bb_middle'] = data.groupby('symbol')['close'].transform(lambda x: x.rolling(window=self.window).mean())
        data['bb_std'] = data.groupby('symbol')['close'].transform(lambda x: x.rolling(window=self.window).std())
        data['bb_upper'] = data['bb_middle'] + self.num_std * data['bb_std']
        data['bb_lower'] = data['bb_middle'] - self.num_std * data['bb_std']
        
        # 生成信号
        data['signal'] = 0
        data.loc[data['close'] < data['bb_lower'], 'signal'] = 1  # 下轨突破买入
        data.loc[data['close'] > data['bb_upper'], 'signal'] = -1  # 上轨突破卖出
        
        return data


class KDJStrategy(Strategy):
    """KDJ策略"""
    
    def __init__(self, period: int = 9, k_period: int = 3, d_period: int = 3):
        super().__init__("KDJ")
        self.period = period
        self.k_period = k_period
        self.d_period = d_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成KDJ信号"""
        data = data.copy()
        
        # 计算KDJ
        def calculate_kdj(high, low, close, period=9, k_period=3, d_period=3):
            # 计算RSV
            rsv = []
            for i in range(len(close)):
                if i < period - 1:
                    rsv.append(50)
                else:
                    high_max = max(high[i-period+1:i+1])
                    low_min = min(low[i-period+1:i+1])
                    if high_max == low_min:
                        rsv.append(50)
                    else:
                        rsv.append((close[i] - low_min) / (high_max - low_min) * 100)
            
            # 计算K和D
            k = []
            d = []
            for i in range(len(rsv)):
                if i == 0:
                    k_val = 50
                    d_val = 50
                else:
                    k_val = (2/3) * k[i-1] + (1/3) * rsv[i]
                    d_val = (2/3) * d[i-1] + (1/3) * k_val
                k.append(k_val)
                d.append(d_val)
            
            # 计算J
            j = [3 * k_val - 2 * d_val for k_val, d_val in zip(k, d)]
            
            return k, d, j
        
        # 分别计算KDJ
        k_list = []
        d_list = []
        j_list = []
        for symbol in data['symbol'].unique():
            symbol_data = data[data['symbol'] == symbol]
            high = symbol_data['high'].tolist()
            low = symbol_data['low'].tolist()
            close = symbol_data['close'].tolist()
            k, d, j = calculate_kdj(high, low, close, self.period, self.k_period, self.d_period)
            k_list.extend(k)
            d_list.extend(d)
            j_list.extend(j)
        
        data['k'] = k_list
        data['d'] = d_list
        data['j'] = j_list
        
        # 生成信号
        data['signal'] = 0
        data.loc[(data['k'] < 20) & (data['d'] < 20) & (data['j'] < 20), 'signal'] = 1  # 超卖买入
        data.loc[(data['k'] > 80) & (data['d'] > 80) & (data['j'] > 80), 'signal'] = -1  # 超买卖出
        
        return data


class VolumeStrategy(Strategy):
    """成交量策略"""
    
    def __init__(self, volume_period: int = 20, volume_ratio: float = 1.5):
        super().__init__("Volume")
        self.volume_period = volume_period
        self.volume_ratio = volume_ratio
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成成交量信号"""
        data = data.copy()
        
        # 计算成交量移动平均线
        data['volume_ma'] = data.groupby('symbol')['amount'].transform(lambda x: x.rolling(window=self.volume_period).mean())
        data['volume_ratio'] = data['amount'] / data['volume_ma']
        
        # 生成信号
        data['signal'] = 0
        data.loc[data['volume_ratio'] > self.volume_ratio, 'signal'] = 1  # 成交量放大买入
        
        return data


class MomentumStrategy(Strategy):
    """动量策略"""
    
    def __init__(self, momentum_period: int = 12):
        super().__init__("Momentum")
        self.momentum_period = momentum_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成动量信号"""
        data = data.copy()
        
        # 计算动量
        data['momentum'] = data.groupby('symbol')['close'].transform(lambda x: x / x.shift(self.momentum_period) - 1)
        
        # 生成信号
        data['signal'] = 0
        data.loc[data['momentum'] > 0, 'signal'] = 1  # 动量为正买入
        data.loc[data['momentum'] < 0, 'signal'] = -1  # 动量为负卖出
        
        return data


# 导入新的行业周期策略
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.industry_cycle_strategy import IndustryCycleStrategy, IndustryCyclePhase


class IndustryStrategy(IndustryCycleStrategy):
    """
    行业周期策略 - 基于多维度指标判断行业复苏/衰退
    
    核心指标：
    1. 价格动量（短期/中期/长期）
    2. 资金流向（成交量/成交额）
    3. 趋势强度（均线排列）
    4. RSI超买超卖
    5. 波动率
    
    综合评分系统生成买卖信号
    """
    
    def __init__(self, momentum_periods: list = None, rsi_period: int = 14, 
                 rsi_threshold: float = 30, exit_threshold: float = 70):
        # 使用新的策略框架初始化
        super().__init__(
            rsi_period=rsi_period,
            rsi_oversold=rsi_threshold,
            rsi_overbought=exit_threshold
        )
        self.name = "Industry"
        self.data = None
        self.cash = 0
        self.positions = {}
    
    def initialize(self, data: pd.DataFrame, initial_cash: float = 100000):
        """初始化策略"""
        self.data = data
        self.cash = initial_cash
        self.positions = {}
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """获取组合价值"""
        position_value = sum(
            pos.shares * current_prices.get(symbol, 0)
            for symbol, pos in self.positions.items()
        )
        return self.cash + position_value


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, strategy: Strategy, commission: float = 0.001, slippage: float = 0.001):
        """
        初始化回测引擎
        
        Args:
            strategy: 交易策略
            commission: 手续费率
            slippage: 滑点率
        """
        self.strategy = strategy
        self.commission = commission
        self.slippage = slippage
        self.equity_curve = []
        self.all_trades = []
    
    def run(self, data: pd.DataFrame, initial_cash: float = 100000) -> BacktestResult:
        """
        运行回测
        
        Args:
            data: 历史数据
            initial_cash: 初始资金
        
        Returns:
            回测结果
        """
        # 初始化策略
        self.strategy.initialize(data, initial_cash)
        
        # 生成信号
        data_with_signals = self.strategy.generate_signals(data)
        
        # 按日期排序
        data_with_signals = data_with_signals.sort_values('date').reset_index(drop=True)
        
        # 按日期分组回测
        for date, date_data in data_with_signals.groupby('date'):
            # 计算当前日期的所有股票价格
            current_prices = dict(zip(date_data['symbol'], date_data['close']))
            
            # 更新持仓价值
            portfolio_value = self.strategy.get_portfolio_value(current_prices)
            self.equity_curve.append({
                'date': date,
                'value': portfolio_value
            })
            
            # 执行交易
            for idx, row in date_data.iterrows():
                if row['signal'] != 0:
                    self._execute_trade(row, current_prices)
        
        # 平仓所有持仓
        final_prices = dict(zip(data_with_signals['symbol'], data_with_signals['close']))
        # 获取最后一天日期
        last_date = data_with_signals['date'].iloc[-1]
        self._close_all_positions(final_prices, last_date)
        
        # 计算最终组合价值
        final_value = self.strategy.get_portfolio_value(final_prices)
        self.equity_curve[-1]['value'] = final_value
        
        # 计算回测结果
        return self._calculate_results(initial_cash, final_value)
    
    def _execute_trade(self, row: pd.Series, current_prices: Dict[str, float]):
        """执行交易"""
        symbol = row['symbol']
        signal = row['signal']
        industry = row.get('industry', None)
        
        # 对于行业策略，需要处理行业级别的交易
        if self.strategy.name == "Industry" and industry:
            # 获取当前日期该行业的所有股票
            current_date = row['date']
            # 优化：使用pandas的条件过滤，而不是列表推导式
            industry_stocks = self.strategy.data.loc[
                (self.strategy.data['date'] == current_date) & 
                (self.strategy.data['industry'] == industry),
                'symbol'
            ].unique().tolist()
            
            if signal == 1:  # 买入该行业所有股票
                # 计算每个股票的购买金额（平均分配资金）
                if self.strategy.cash > 0 and industry_stocks:
                    cash_per_stock = self.strategy.cash / len(industry_stocks)
                    for stock in industry_stocks:
                        if stock not in self.strategy.positions:
                            price = current_prices.get(stock, row['close']) * (1 + self.slippage)
                            max_shares = int(cash_per_stock / (price * (1 + self.commission)))
                            if max_shares > 0:
                                cost = max_shares * price * (1 + self.commission)
                                self.strategy.cash -= cost
                                self.strategy.positions[stock] = Position(
                                    symbol=stock,
                                    shares=max_shares,
                                    entry_price=price,
                                    entry_date=current_date
                                )
                                self.all_trades.append(Trade(
                                    symbol=stock,
                                    action='buy',
                                    shares=max_shares,
                                    price=price,
                                    date=current_date,
                                    commission=max_shares * price * self.commission
                                ))
            
            elif signal == -1:  # 卖出该行业所有股票
                for stock in industry_stocks:
                    if stock in self.strategy.positions:
                        position = self.strategy.positions[stock]
                        price = current_prices.get(stock, row['close']) * (1 - self.slippage)
                        revenue = position.shares * price * (1 - self.commission)
                        self.strategy.cash += revenue
                        self.all_trades.append(Trade(
                            symbol=stock,
                            action='sell',
                            shares=position.shares,
                            price=price,
                            date=current_date,
                            commission=position.shares * price * self.commission
                        ))
                        del self.strategy.positions[stock]
        else:
            # 传统股票策略交易
            price = row['close'] * (1 + self.slippage * signal)
            
            if signal == 1:  # 买入
                if symbol not in self.strategy.positions:
                    max_shares = int(self.strategy.cash / (price * (1 + self.commission)))
                    if max_shares > 0:
                        cost = max_shares * price * (1 + self.commission)
                        self.strategy.cash -= cost
                        self.strategy.positions[symbol] = Position(
                            symbol=symbol,
                            shares=max_shares,
                            entry_price=price,
                            entry_date=row['date']
                        )
                        self.all_trades.append(Trade(
                            symbol=symbol,
                            action='buy',
                            shares=max_shares,
                            price=price,
                            date=row['date'],
                            commission=max_shares * price * self.commission
                        ))
            
            elif signal == -1:  # 卖出
                if symbol in self.strategy.positions:
                    position = self.strategy.positions[symbol]
                    revenue = position.shares * price * (1 - self.commission)
                    self.strategy.cash += revenue
                    self.all_trades.append(Trade(
                        symbol=symbol,
                        action='sell',
                        shares=position.shares,
                        price=price,
                        date=row['date'],
                        commission=position.shares * price * self.commission
                    ))
                    del self.strategy.positions[symbol]
    
    def _close_all_positions(self, current_prices: Dict[str, float], close_date=None):
        """平仓所有持仓"""
        if close_date is None:
            close_date = datetime.now()
            
        for symbol, position in list(self.strategy.positions.items()):
            if symbol in current_prices:
                price = current_prices[symbol] * (1 - self.slippage)
                revenue = position.shares * price * (1 - self.commission)
                self.strategy.cash += revenue
                self.all_trades.append(Trade(
                    symbol=symbol,
                    action='sell',
                    shares=position.shares,
                    price=price,
                    date=close_date,
                    commission=position.shares * price * self.commission
                ))
                del self.strategy.positions[symbol]
    
    def _calculate_results(self, initial_cash: float, final_value: float) -> BacktestResult:
        """计算回测结果"""
        equity_series = pd.Series([e['value'] for e in self.equity_curve])
        returns = equity_series.pct_change().dropna()
        
        # 总收益率
        total_return = (final_value - initial_cash) / initial_cash
        
        # 年化收益率
        days = len(self.equity_curve)
        annual_return = (1 + total_return) ** (252 / days) - 1
        
        # 夏普比率
        if len(returns) > 1:
            std_returns = returns.std()
            if std_returns > 0:
                sharpe_ratio = returns.mean() / std_returns * np.sqrt(252)
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # 最大回撤
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdown = (cum_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 胜率和盈亏比
        win_count = 0
        total_profit = 0
        total_loss = 0
        
        # 配对买卖交易
        buy_trades = {}
        for trade in self.all_trades:
            if trade.action == 'buy':
                buy_trades[trade.symbol] = trade
            elif trade.action == 'sell' and trade.symbol in buy_trades:
                buy_trade = buy_trades[trade.symbol]
                profit = (trade.price - buy_trade.price) * trade.shares
                if profit > 0:
                    win_count += 1
                    total_profit += profit
                else:
                    total_loss += abs(profit)
                del buy_trades[trade.symbol]
        
        # 计算胜率
        sell_trades = [t for t in self.all_trades if t.action == 'sell']
        win_rate = win_count / len(sell_trades) if sell_trades else 0
        
        # 计算盈亏比
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        return BacktestResult(
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(self.all_trades),
            equity_curve=equity_series,
            trades=self.all_trades
        )


def print_backtest_results(result: BacktestResult):
    """打印回测结果"""
    print("\n" + "="*50)
    print("回测结果")
    print("="*50)
    print(f"总收益率: {result.total_return:.2%}")
    print(f"年化收益率: {result.annual_return:.2%}")
    print(f"夏普比率: {result.sharpe_ratio:.2f}")
    print(f"最大回撤: {result.max_drawdown:.2%}")
    print(f"胜率: {result.win_rate:.2%}")
    print(f"盈亏比: {result.profit_factor:.2f}")
    print(f"总交易次数: {result.total_trades}")
    print("="*50)


if __name__ == "__main__":
    # 测试回测引擎
    from data.data_provider import MockDataProvider, DataManager
    
    # 准备数据
    provider = MockDataProvider()
    data_manager = DataManager(provider)
    symbols = ['AAPL', 'MSFT']
    
    from datetime import timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    df = data_manager.load_data(symbols, start_date, end_date)
    df = data_manager.calculate_technical_indicators(df)
    
    # 创建策略
    strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)
    
    # 创建回测引擎
    engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)
    
    # 运行回测
    result = engine.run(df, initial_cash=100000)
    
    # 打印结果
    print_backtest_results(result)
