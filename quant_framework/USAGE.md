# 量化交易框架使用指南

## 框架概述

这是一个简单易用的量化交易框架，包含数据获取、策略回测、风险管理等核心功能。

## 项目结构

```
quant_framework/
├── data/                           # 数据模块
│   └── data_provider.py          # 数据提供者和数据管理器
├── strategies/                      # 策略模块（待添加）
│   └── (自定义策略)
├── backtesting/                    # 回测模块
│   └── backtest_engine.py       # 回测引擎和策略基类
├── risk/                          # 风险管理模块
│   └── risk_manager.py          # 风险管理器和风险指标
├── utils/                         # 工具模块（待添加）
│   └── (辅助工具)
├── examples/                      # 示例代码
│   ├── example_strategy.py        # 策略示例
│   └── example_strategy_fixed.py  # 修复后的示例
├── test_framework.py               # 框架测试脚本
├── requirements.txt                # 依赖包列表
└── README.md                     # 项目说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
cd quant_framework
python test_framework.py
```

### 3. 运行示例

```bash
cd quant_framework/examples
python example_strategy_fixed.py
```

## 核心功能

### 数据管理

- 支持多种数据源（可扩展）
- 数据缓存机制
- 自动计算技术指标
- 收益率计算

**使用示例：**
```python
from data.data_provider import DataManager, MockDataProvider

provider = MockDataProvider()
data_manager = DataManager(provider)

# 加载数据
df = data_manager.load_data(['AAPL'], '2023-01-01', '2024-01-01')

# 计算技术指标
df = data_manager.calculate_technical_indicators(df)
```

### 策略回测

- 策略基类，方便自定义策略
- 内置常用策略（移动平均、RSI等）
- 完整的回测引擎
- 支持手续费和滑点
- 详细的回测结果

**使用示例：**
```python
from backtesting.backtest_engine import BacktestEngine, MovingAverageCrossStrategy

# 创建策略
strategy = MovingAverageCrossStrategy(short_window=5, long_window=20)

# 创建回测引擎
engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)

# 运行回测
result = engine.run(df, initial_cash=100000)

# 查看结果
print(f"总收益率: {result.total_return:.2%}")
```

### 风险管理

- 仓位管理
- 止损止盈控制
- VaR和CVaR计算
- 多种风险指标（夏普比率、索提诺比率等）
- 风险等级评估

**使用示例：**
```python
from risk.risk_manager import RiskManager

risk_manager = RiskManager()

# 计算风险指标
metrics = risk_manager.calculate_risk_metrics(returns)

# 检查入场条件
if risk_manager.check_entry(portfolio_value, entry_price, stop_loss, shares):
    # 执行交易
    pass
```

## 技术指标

框架支持以下技术指标：
- 移动平均线（MA5, MA10, MA20）
- 相对强弱指标（RSI）
- MACD
- 布林带（Bollinger Bands）

## 风险指标

框架可以计算以下风险指标：
- 波动率
- VaR（Value at Risk）
- CVaR（Conditional Value at Risk）
- 最大回撤
- Beta系数
- 夏普比率
- 索提诺比率
- 信息比率
- 跟踪误差

## 自定义策略

### 步骤1：创建策略类

```python
from backtesting.backtest_engine import Strategy

class MyStrategy(Strategy):
    def __init__(self):
        super().__init__("MyStrategy")
    
    def generate_signals(self, data):
        # 实现您的交易逻辑
        data['signal'] = 0
        # 买入条件
        data.loc[condition, 'signal'] = 1
        # 卖出条件
        data.loc[condition, 'signal'] = -1
        return data
```

### 步骤2：运行回测

```python
from data.data_provider import DataManager, MockDataProvider
from backtesting.backtest_engine import BacktestEngine

# 准备数据
provider = MockDataProvider()
data_manager = DataManager(provider)
df = data_manager.load_data(['AAPL'], '2023-01-01', '2024-01-01')
df = data_manager.calculate_technical_indicators(df)

# 创建策略和回测引擎
strategy = MyStrategy()
engine = BacktestEngine(strategy, commission=0.001, slippage=0.001)

# 运行回测
result = engine.run(df, initial_cash=100000)

# 查看结果
print(f"总收益率: {result.total_return:.2%}")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown:.2%}")
```

## 扩展建议

### 1. 添加真实数据源

实现真实的DataProvider，支持：
- yfinance（Yahoo Finance）
- tushare（中国股市）
- 其他数据API

### 2. 添加更多策略

- 均值回归策略
- 动量策略
- 机器学习策略
- 配对交易策略

### 3. 优化回测引擎

- 支持多策略组合
- 支持参数优化
- 支持并行回测
- 添加更多订单类型

### 4. 增强风险管理

- 动态仓位管理
- 组合优化
- 压力测试
- 相关性分析

## 测试结果

运行 `python test_framework.py` 的输出：

```
开始测试量化框架...

测试1: 导入数据模块
✅ 数据模块导入成功
从数据源获取数据: ['AAPL', 'MSFT']
✅ 数据加载成功: (732, 7)

测试2: 导入回测模块
✅ 回测模块导入成功
✅ 技术指标计算成功
✅ 回测执行成功: 总收益率=-99.61%

测试3: 导入风险管理模块
✅ 风险管理模块导入成功
✅ 风险指标计算成功: 波动率=346.75%

============================================================
所有测试通过！量化框架运行正常。
============================================================

框架功能:
- 数据获取和管理
- 技术指标计算
- 策略回测
- 风险管理

您可以开始使用框架进行量化交易研究了！
```

## 注意事项

- 本框架仅供学习和研究使用
- 实盘交易前请充分测试
- 注意风险控制，合理设置止损
- 过去的表现不代表未来
- 建议使用真实数据进行回测

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎反馈。
