# 量化交易框架

一个简单易用的量化交易框架，包含数据获取、策略回测、风险管理等核心功能。

## 项目结构

```
quant_framework/
├── data/                    # 数据模块
│   └── data_provider.py   # 数据提供者和数据管理器
├── strategies/              # 策略模块
│   └── (待添加)          # 自定义策略
├── backtesting/            # 回测模块
│   └── backtest_engine.py  # 回测引擎和策略基类
├── risk/                  # 风险管理模块
│   └── risk_manager.py    # 风险管理器和风险指标
├── utils/                 # 工具模块
│   └── (待添加)          # 辅助工具
└── examples/              # 示例代码
    └── example_strategy.py # 策略示例
```

## 功能特性

### 1. 数据管理
- 支持多种数据源（可扩展）
- 数据缓存机制
- 自动计算技术指标
- 收益率计算

### 2. 策略回测
- 策略基类，方便自定义策略
- 内置常用策略（移动平均、RSI等）
- 完整的回测引擎
- 支持手续费和滑点
- 详细的回测结果

### 3. 风险管理
- 仓位管理
- 止损止盈控制
- VaR和CVaR计算
- 多种风险指标（夏普比率、索提诺比率等）
- 风险等级评估

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行示例

```bash
cd quant_framework/examples
python example_strategy.py
```

### 3. 自定义策略

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

### 4. 运行回测

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
```

## 核心模块说明

### DataProvider（数据提供者）
- `fetch_data()`: 获取历史数据
- `get_stock_list()`: 获取股票列表

### DataManager（数据管理器）
- `load_data()`: 加载数据（支持缓存）
- `calculate_returns()`: 计算收益率
- `calculate_technical_indicators()`: 计算技术指标

### Strategy（策略基类）
- `initialize()`: 初始化策略
- `generate_signals()`: 生成交易信号
- `on_bar()`: 每个bar的回调

### BacktestEngine（回测引擎）
- `run()`: 运行回测
- 返回详细的回测结果

### RiskManager（风险管理器）
- `check_entry()`: 检查入场条件
- `check_exit()`: 检查出场条件
- `calculate_risk_metrics()`: 计算风险指标

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

## 扩展建议

1. **添加真实数据源**
   - 实现真实的DataProvider
   - 支持yfinance、tushare等数据源

2. **添加更多策略**
   - 均值回归策略
   - 动量策略
   - 机器学习策略

3. **优化回测引擎**
   - 支持多策略组合
   - 支持参数优化
   - 支持并行回测

4. **增强风险管理**
   - 动态仓位管理
   - 组合优化
   - 压力测试

## 注意事项

- 本框架仅供学习和研究使用
- 实盘交易前请充分测试
- 注意风险控制，合理设置止损
- 过去的表现不代表未来

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎反馈。
