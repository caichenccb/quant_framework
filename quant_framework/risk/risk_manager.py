"""
风险管理模块
提供风险控制和风险指标计算功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    EXTREME = "极高"


@dataclass
class RiskMetrics:
    """风险指标"""
    volatility: float  # 波动率
    var_95: float  # 95%置信度的VaR
    var_99: float  # 99%置信度的VaR
    cvar_95: float  # 95%置信度的CVaR
    max_drawdown: float  # 最大回撤
    beta: float  # Beta系数
    sharpe_ratio: float  # 夏普比率
    sortino_ratio: float  # 索提诺比率
    information_ratio: float  # 信息比率
    tracking_error: float  # 跟踪误差
    risk_level: RiskLevel  # 风险等级


class PositionSizing:
    """仓位管理"""
    
    def __init__(self, max_position_size: float = 0.2, max_portfolio_risk: float = 0.02):
        """
        初始化仓位管理
        
        Args:
            max_position_size: 单个股票最大仓位比例 (0-1)
            max_portfolio_risk: 组合最大风险敞口 (0-1)
        """
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
    
    def calculate_position_size(self, portfolio_value: float, price: float, 
                           volatility: float, confidence: float = 0.95) -> int:
        """
        计算仓位大小
        
        Args:
            portfolio_value: 组合价值
            price: 股票价格
            volatility: 股票波动率
            confidence: 置信度
        
        Returns:
            建议的持仓数量
        """
        # 基于波动率的仓位调整
        risk_adjustment = 1 / (1 + volatility * 10)
        
        # 计算最大可投资金额
        max_investment = portfolio_value * self.max_position_size * risk_adjustment
        
        # 计算股数
        shares = int(max_investment / price)
        
        return max(0, shares)
    
    def calculate_portfolio_risk(self, positions: Dict[str, int], 
                            prices: Dict[str, float], 
                            volatilities: Dict[str, float],
                            correlations: Optional[pd.DataFrame] = None) -> float:
        """
        计算组合风险
        
        Args:
            positions: 持仓字典 {symbol: shares}
            prices: 当前价格字典
            volatilities: 波动率字典
            correlations: 相关系数矩阵
        
        Returns:
            组合风险值
        """
        if not positions:
            return 0.0
        
        # 计算各股票的市值
        market_values = {}
        total_value = 0
        for symbol, shares in positions.items():
            if symbol in prices:
                market_value = shares * prices[symbol]
                market_values[symbol] = market_value
                total_value += market_value
        
        if total_value == 0:
            return 0.0
        
        # 计算权重
        weights = {symbol: value / total_value for symbol, value in market_values.items()}
        
        # 如果没有相关系数矩阵，假设不相关
        if correlations is None:
            portfolio_variance = sum(
                (weights[symbol] ** 2) * (volatilities.get(symbol, 0) ** 2)
                for symbol in positions.keys()
            )
        else:
            # 考虑相关性的组合方差
            symbols = list(positions.keys())
            weight_array = np.array([weights[s] for s in symbols])
            vol_array = np.array([volatilities.get(s, 0) for s in symbols])
            cov_matrix = correlations.loc[symbols, symbols].values * np.outer(vol_array, vol_array)
            portfolio_variance = np.dot(weight_array, np.dot(cov_matrix, weight_array))
        
        return np.sqrt(portfolio_variance)


class RiskManager:
    """风险管理器"""
    
    def __init__(self, max_drawdown: float = 0.15, max_loss_per_trade: float = 0.02,
                 daily_var_limit: float = 0.05):
        """
        初始化风险管理器
        
        Args:
            max_drawdown: 最大回撤限制
            max_loss_per_trade: 单笔交易最大亏损比例
            daily_var_limit: 每日VaR限制
        """
        self.max_drawdown = max_drawdown
        self.max_loss_per_trade = max_loss_per_trade
        self.daily_var_limit = daily_var_limit
        self.peak_equity = 0
        self.current_drawdown = 0
    
    def check_entry(self, portfolio_value: float, entry_price: float, 
                  stop_loss: float, shares: int) -> bool:
        """
        检查是否可以入场
        
        Args:
            portfolio_value: 组合价值
            entry_price: 入场价格
            stop_loss: 止损价格
            shares: 交易数量
        
        Returns:
            是否允许入场
        """
        # 计算潜在亏损
        potential_loss = (entry_price - stop_loss) * shares / portfolio_value
        
        # 检查单笔交易风险
        if potential_loss > self.max_loss_per_trade:
            print(f"风险控制: 单笔交易风险 {potential_loss:.2%} 超过限制 {self.max_loss_per_trade:.2%}")
            return False
        
        return True
    
    def check_exit(self, current_price: float, entry_price: float, 
                 stop_loss: float, take_profit: float) -> Tuple[bool, str]:
        """
        检查是否需要出场
        
        Args:
            current_price: 当前价格
            entry_price: 入场价格
            stop_loss: 止损价格
            take_profit: 止盈价格
        
        Returns:
            (是否出场, 原因)
        """
        if current_price <= stop_loss:
            return True, "止损"
        elif current_price >= take_profit:
            return True, "止盈"
        return False, ""
    
    def update_drawdown(self, current_equity: float) -> float:
        """
        更新回撤
        
        Args:
            current_equity: 当前权益
        
        Returns:
            当前回撤比例
        """
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        if self.peak_equity > 0:
            self.current_drawdown = (self.peak_equity - current_equity) / self.peak_equity
        else:
            self.current_drawdown = 0
        
        return self.current_drawdown
    
    def check_drawdown_limit(self) -> bool:
        """
        检查是否超过回撤限制
        
        Returns:
            是否超过限制
        """
        return self.current_drawdown >= self.max_drawdown
    
    def calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        计算VaR (Value at Risk)
        
        Args:
            returns: 收益率序列
            confidence: 置信度
        
        Returns:
            VaR值
        """
        return np.percentile(returns, (1 - confidence) * 100)
    
    def calculate_cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        计算CVaR (Conditional Value at Risk)
        
        Args:
            returns: 收益率序列
            confidence: 置信度
        
        Returns:
            CVaR值
        """
        var = self.calculate_var(returns, confidence)
        tail_losses = returns[returns <= var]
        return tail_losses.mean() if len(tail_losses) > 0 else var
    
    def calculate_risk_metrics(self, returns: pd.Series, 
                          benchmark_returns: Optional[pd.Series] = None,
                          risk_free_rate: float = 0.03) -> RiskMetrics:
        """
        计算风险指标
        
        Args:
            returns: 收益率序列
            benchmark_returns: 基准收益率序列
            risk_free_rate: 无风险利率
        
        Returns:
            风险指标对象
        """
        # 波动率
        volatility = returns.std() * np.sqrt(252)
        
        # VaR和CVaR
        var_95 = self.calculate_var(returns, 0.95)
        var_99 = self.calculate_var(returns, 0.99)
        cvar_95 = self.calculate_cvar(returns, 0.95)
        
        # 最大回撤
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdown = (cum_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Beta系数
        if benchmark_returns is not None and len(returns) == len(benchmark_returns):
            covariance = np.cov(returns, benchmark_returns)[0, 1]
            benchmark_variance = benchmark_returns.var()
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        else:
            beta = 1.0
        
        # 夏普比率
        excess_returns = returns - risk_free_rate / 252
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
        
        # 索提诺比率
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() if len(negative_returns) > 0 else 0.001
        sortino_ratio = excess_returns.mean() / downside_std * np.sqrt(252) if downside_std > 0 else 0
        
        # 信息比率
        if benchmark_returns is not None and len(returns) == len(benchmark_returns):
            active_returns = returns - benchmark_returns
            information_ratio = active_returns.mean() / active_returns.std() * np.sqrt(252) if active_returns.std() > 0 else 0
            tracking_error = active_returns.std() * np.sqrt(252)
        else:
            information_ratio = 0
            tracking_error = 0
        
        # 风险等级
        if volatility < 0.15:
            risk_level = RiskLevel.LOW
        elif volatility < 0.25:
            risk_level = RiskLevel.MEDIUM
        elif volatility < 0.35:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.EXTREME
        
        return RiskMetrics(
            volatility=volatility,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            max_drawdown=max_drawdown,
            beta=beta,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            information_ratio=information_ratio,
            tracking_error=tracking_error,
            risk_level=risk_level
        )


def print_risk_metrics(metrics: RiskMetrics):
    """打印风险指标"""
    print("\n" + "="*50)
    print("风险指标分析")
    print("="*50)
    print(f"波动率: {metrics.volatility:.2%}")
    print(f"95% VaR: {metrics.var_95:.2%}")
    print(f"99% VaR: {metrics.var_99:.2%}")
    print(f"95% CVaR: {metrics.cvar_95:.2%}")
    print(f"最大回撤: {metrics.max_drawdown:.2%}")
    print(f"Beta系数: {metrics.beta:.2f}")
    print(f"夏普比率: {metrics.sharpe_ratio:.2f}")
    print(f"索提诺比率: {metrics.sortino_ratio:.2f}")
    print(f"信息比率: {metrics.information_ratio:.2f}")
    print(f"跟踪误差: {metrics.tracking_error:.2%}")
    print(f"风险等级: {metrics.risk_level.value}")
    print("="*50)


if __name__ == "__main__":
    # 测试风险管理
    np.random.seed(42)
    
    # 生成模拟收益率
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))
    benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, 252))
    
    # 创建风险管理器
    risk_manager = RiskManager(
        max_drawdown=0.15,
        max_loss_per_trade=0.02,
        daily_var_limit=0.05
    )
    
    # 计算风险指标
    metrics = risk_manager.calculate_risk_metrics(returns, benchmark_returns)
    
    # 打印结果
    print_risk_metrics(metrics)
    
    # 测试仓位管理
    position_sizing = PositionSizing(max_position_size=0.2, max_portfolio_risk=0.02)
    
    portfolio_value = 100000
    price = 50
    volatility = 0.25
    
    shares = position_sizing.calculate_position_size(portfolio_value, price, volatility)
    print(f"\n仓位管理建议:")
    print(f"组合价值: {portfolio_value:,.2f}")
    print(f"股票价格: {price:.2f}")
    print(f"波动率: {volatility:.2%}")
    print(f"建议持仓数量: {shares} 股")
    print(f"持仓金额: {shares * price:,.2f}")
    print(f"仓位比例: {(shares * price) / portfolio_value:.2%}")
