"""
行业周期判断策略
通过多种量化指标判断行业处于复苏阶段还是衰退阶段
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class IndustryCyclePhase(Enum):
    """行业周期阶段"""
    DEEP_RECESSION = "深度衰退"      # 深度衰退期
    EARLY_RECOVERY = "早期复苏"      # 早期复苏期
    RECOVERY = "复苏期"              # 复苏期
    EXPANSION = "扩张期"             # 扩张期
    LATE_EXPANSION = "扩张末期"      # 扩张末期
    SLOWDOWN = "放缓期"              # 放缓期
    RECESSION = "衰退期"             # 衰退期


@dataclass
class IndustrySignal:
    """行业信号"""
    industry: str
    date: pd.Timestamp
    phase: IndustryCyclePhase
    signal_score: float  # 综合评分 -1到1，正值看多，负值看空
    indicators: Dict[str, float]  # 各指标值


class IndustryCycleStrategy:
    """
    行业周期判断策略
    
    核心逻辑：
    1. 价格动量指标：判断行业价格趋势
    2. 资金流向指标：判断资金流入流出
    3. 估值指标：判断行业估值水平
    4. 情绪指标：判断市场情绪
    5. 宏观指标：结合宏观环境
    
    综合评分系统：
    - 评分 > 0.6: 强烈看多（买入）
    - 0.3 < 评分 <= 0.6: 看多
    - -0.3 <= 评分 <= 0.3: 中性
    - -0.6 <= 评分 < -0.3: 看空
    - 评分 < -0.6: 强烈看空（卖出）
    """
    
    def __init__(
        self,
        # 动量参数
        momentum_short: int = 20,
        momentum_medium: int = 60,
        momentum_long: int = 120,
        
        # RSI参数
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        
        # 资金流向参数
        volume_ma_period: int = 20,
        volume_ratio_threshold: float = 1.5,
        
        # 均线参数
        ma_short: int = 20,
        ma_medium: int = 60,
        ma_long: int = 120,
        
        # 评分阈值
        strong_buy_threshold: float = 0.6,
        buy_threshold: float = 0.3,
        sell_threshold: float = -0.3,
        strong_sell_threshold: float = -0.6,
    ):
        self.momentum_short = momentum_short
        self.momentum_medium = momentum_medium
        self.momentum_long = momentum_long
        
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        
        self.volume_ma_period = volume_ma_period
        self.volume_ratio_threshold = volume_ratio_threshold
        
        self.ma_short = ma_short
        self.ma_medium = ma_medium
        self.ma_long = ma_long
        
        self.strong_buy_threshold = strong_buy_threshold
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.strong_sell_threshold = strong_sell_threshold
        
        # 指标权重配置
        self.indicator_weights = {
            'momentum': 0.25,      # 价格动量权重
            'volume': 0.20,        # 资金流向权重
            'trend': 0.25,         # 趋势权重
            'rsi': 0.15,           # RSI权重
            'volatility': 0.15,    # 波动率权重
        }
    
    def calculate_indicators(self, industry_data: pd.DataFrame) -> pd.DataFrame:
        """
        计算行业各项指标
        
        Args:
            industry_data: 行业数据，包含date, close, amount等列
            
        Returns:
            添加了各项指标的数据框
        """
        df = industry_data.copy()
        df = df.sort_values('date').reset_index(drop=True)
        
        # 检查必要的列
        if 'amount' not in df.columns:
            print("警告: 数据中缺少'amount'列，使用默认值")
            df['amount'] = df['close'] * 100000  # 使用默认值
        
        # ========== 1. 价格动量指标 ==========
        # 短期动量（20日）
        df['momentum_short'] = df['close'].pct_change(self.momentum_short)
        # 中期动量（60日）
        df['momentum_medium'] = df['close'].pct_change(self.momentum_medium)
        # 长期动量（120日）
        df['momentum_long'] = df['close'].pct_change(self.momentum_long)
        
        # 动量得分 (-1 到 1)
        df['momentum_score'] = (
            df['momentum_short'] * 0.5 + 
            df['momentum_medium'] * 0.3 + 
            df['momentum_long'] * 0.2
        ) * 10  # 放大到合理范围
        df['momentum_score'] = df['momentum_score'].clip(-1, 1)
        
        # ========== 2. 资金流向指标 ==========
        # 成交额移动平均
        df['amount_ma'] = df['amount'].rolling(self.volume_ma_period).mean()
        # 成交额比率
        df['amount_ratio'] = df['amount'] / df['amount_ma'].replace(0, np.nan)
        
        # 量价配合度
        df['price_change'] = df['close'].pct_change()
        df['volume_price_corr'] = df['price_change'].rolling(20).corr(df['amount_ratio'])
        
        # 资金流向得分
        df['volume_score'] = np.where(
            (df['amount_ratio'] > self.volume_ratio_threshold) & (df['price_change'] > 0),
            1.0,  # 放量上涨，强烈看多
            np.where(
                (df['amount_ratio'] > self.volume_ratio_threshold) & (df['price_change'] < 0),
                -1.0,  # 放量下跌，强烈看空
                np.where(
                    df['amount_ratio'] > 1.0,
                    0.3 * np.sign(df['price_change']),  # 正常放量
                    -0.3  # 缩量
                )
            )
        )
        
        # ========== 3. 趋势指标 ==========
        # 移动平均线
        df['ma_short'] = df['close'].rolling(self.ma_short).mean()
        df['ma_medium'] = df['close'].rolling(self.ma_medium).mean()
        df['ma_long'] = df['close'].rolling(self.ma_long).mean()
        
        # 均线排列得分
        df['trend_score'] = np.where(
            (df['close'] > df['ma_short']) & 
            (df['ma_short'] > df['ma_medium']) & 
            (df['ma_medium'] > df['ma_long']),
            1.0,  # 多头排列
            np.where(
                (df['close'] < df['ma_short']) & 
                (df['ma_short'] < df['ma_medium']) & 
                (df['ma_medium'] < df['ma_long']),
                -1.0,  # 空头排列
                np.where(
                    df['close'] > df['ma_short'],
                    0.3,  # 短期向上
                    -0.3   # 短期向下
                )
            )
        )
        
        # ========== 4. RSI指标 ==========
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # RSI得分（反转思维：超卖=看多，超买=看空）
        df['rsi_score'] = np.where(
            df['rsi'] < self.rsi_oversold,
            1.0,  # 超卖，看多
            np.where(
                df['rsi'] > self.rsi_overbought,
                -1.0,  # 超买，看空
                (50 - df['rsi']) / 50  # 线性映射
            )
        )
        
        # ========== 5. 波动率指标 ==========
        df['volatility'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
        df['volatility_ma'] = df['volatility'].rolling(60).mean()
        
        # 波动率得分（低波动+上涨 = 健康上涨，高波动+下跌 = 风险）
        df['volatility_score'] = np.where(
            (df['volatility'] < df['volatility_ma']) & (df['price_change'] > 0),
            0.5,  # 低波动上涨，稳定
            np.where(
                (df['volatility'] > df['volatility_ma'] * 1.5) & (df['price_change'] < 0),
                -0.8,  # 高波动下跌，风险大
                0.0
            )
        )
        
        return df
    
    def calculate_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算综合评分
        
        Args:
            df: 包含各项指标的数据框
            
        Returns:
            添加了综合评分的数据框
        """
        # 加权计算综合评分
        df['composite_score'] = (
            df['momentum_score'] * self.indicator_weights['momentum'] +
            df['volume_score'] * self.indicator_weights['volume'] +
            df['trend_score'] * self.indicator_weights['trend'] +
            df['rsi_score'] * self.indicator_weights['rsi'] +
            df['volatility_score'] * self.indicator_weights['volatility']
        )
        
        # 平滑处理（5日移动平均）
        df['composite_score_smooth'] = df['composite_score'].rolling(5).mean()
        
        return df
    
    def determine_cycle_phase(self, score: float) -> IndustryCyclePhase:
        """
        根据评分判断行业周期阶段
        
        Args:
            score: 综合评分
            
        Returns:
            行业周期阶段
        """
        if score > 0.8:
            return IndustryCyclePhase.EARLY_RECOVERY
        elif score > 0.5:
            return IndustryCyclePhase.RECOVERY
        elif score > 0.2:
            return IndustryCyclePhase.EXPANSION
        elif score > -0.2:
            return IndustryCyclePhase.LATE_EXPANSION
        elif score > -0.5:
            return IndustryCyclePhase.SLOWDOWN
        elif score > -0.8:
            return IndustryCyclePhase.RECESSION
        else:
            return IndustryCyclePhase.DEEP_RECESSION
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成行业信号
        
        Args:
            data: 原始数据，包含industry, date, close, volume, amount等列
            
        Returns:
            添加了信号的数据框
        """
        if 'industry' not in data.columns:
            raise ValueError("数据中缺少行业字段 'industry'")
        
        all_signals = []
        
        # 按行业分别处理
        for industry in data['industry'].unique():
            industry_df = data[data['industry'] == industry].copy()
            
            # 计算行业级别指标（使用平均价格）
            agg_dict = {'close': 'mean'}
            if 'amount' in industry_df.columns:
                agg_dict['amount'] = 'sum'
            
            industry_daily = industry_df.groupby('date').agg(agg_dict).reset_index()
            
            # 如果没有amount列，创建默认值
            if 'amount' not in industry_daily.columns:
                industry_daily['amount'] = industry_daily['close'] * 100000
            
            # 计算各项指标
            industry_daily = self.calculate_indicators(industry_daily)
            
            # 计算综合评分
            industry_daily = self.calculate_composite_score(industry_daily)
            
            # 判断周期阶段
            industry_daily['cycle_phase'] = industry_daily['composite_score_smooth'].apply(
                self.determine_cycle_phase
            )
            
            # 生成交易信号
            industry_daily['signal'] = 0
            
            # 买入信号：从衰退进入复苏
            buy_condition = (
                (industry_daily['composite_score_smooth'] > self.buy_threshold) &
                (industry_daily['composite_score_smooth'].shift(1) <= self.buy_threshold)
            )
            
            # 卖出信号：从扩张进入放缓
            sell_condition = (
                (industry_daily['composite_score_smooth'] < self.sell_threshold) &
                (industry_daily['composite_score_smooth'].shift(1) >= self.sell_threshold)
            )
            
            industry_daily.loc[buy_condition, 'signal'] = 1
            industry_daily.loc[sell_condition, 'signal'] = -1
            
            # 添加行业信息
            industry_daily['industry'] = industry
            
            all_signals.append(industry_daily)
        
        # 合并所有行业信号
        signals_df = pd.concat(all_signals, ignore_index=True)
        
        # 合并回原始数据
        data = data.merge(
            signals_df[['industry', 'date', 'signal', 'composite_score_smooth', 'cycle_phase',
                       'momentum_score', 'volume_score', 'trend_score', 'rsi_score', 'volatility_score']],
            on=['industry', 'date'],
            how='left'
        )
        
        # 输出行业状态报告
        self._print_industry_report(signals_df)
        
        return data
    
    def _print_industry_report(self, signals_df: pd.DataFrame):
        """打印行业状态报告"""
        print("\n" + "="*80)
        print("行业周期分析报告")
        print("="*80)
        
        # 最新日期的各行业状态
        latest_date = signals_df['date'].max()
        latest_data = signals_df[signals_df['date'] == latest_date]
        
        print(f"\n分析日期: {latest_date.strftime('%Y-%m-%d')}")
        print("\n各行业当前状态:")
        print("-" * 80)
        print(f"{'行业':<12} {'周期阶段':<12} {'综合评分':<10} {'动量':<8} {'资金':<8} {'趋势':<8}")
        print("-" * 80)
        
        for _, row in latest_data.iterrows():
            print(f"{row['industry']:<12} {row['cycle_phase'].value:<12} "
                  f"{row['composite_score_smooth']:.2f}      "
                  f"{row['momentum_score']:.2f}    "
                  f"{row['volume_score']:.2f}    "
                  f"{row['trend_score']:.2f}")
        
        print("-" * 80)
        
        # 买入信号行业
        buy_signals = signals_df[signals_df['signal'] == 1]
        if not buy_signals.empty:
            print("\n🟢 复苏信号（买入）:")
            for _, row in buy_signals.iterrows():
                print(f"  {row['industry']} - {row['date'].strftime('%Y-%m-%d')} "
                      f"(评分: {row['composite_score_smooth']:.2f})")
        
        # 卖出信号行业
        sell_signals = signals_df[signals_df['signal'] == -1]
        if not sell_signals.empty:
            print("\n🔴 衰退信号（卖出）:")
            for _, row in sell_signals.iterrows():
                print(f"  {row['industry']} - {row['date'].strftime('%Y-%m-%d')} "
                      f"(评分: {row['composite_score_smooth']:.2f})")
        
        print("\n" + "="*80)


# 兼容旧版IndustryStrategy的接口
class IndustryStrategy(IndustryCycleStrategy):
    """
    兼容旧版接口的行业策略
    """
    
    def __init__(self, momentum_periods: list = None, rsi_period: int = 14, 
                 rsi_threshold: float = 30, exit_threshold: float = 70):
        # 调用父类初始化
        super().__init__(
            rsi_period=rsi_period,
            rsi_oversold=rsi_threshold,
            rsi_overbought=exit_threshold
        )
        self.name = "Industry"
    
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
