"""
测试plotly可视化
"""

import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

# 设置plotly渲染方式为浏览器
pio.renderers.default = 'browser'

# 创建测试数据
dates = pd.date_range('2024-01-01', periods=100)
close = np.random.randn(100) + 100
open_prices = close - np.random.randn(100) * 0.5
amount = np.random.randn(100) * 1e8 + 1e9

df = pd.DataFrame({
    'date': dates,
    'close': close,
    'open': open_prices,
    'amount': amount
})

# 创建一个plotly图表
fig = go.Figure()

# 绘制收盘价曲线
fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['close'],
    mode='lines',
    name='收盘价',
    line=dict(color='blue', width=2),
    hovertemplate=
    '<b>日期:</b> %{x}<br>' +
    '<b>收盘价:</b> %{y:.2f}<br>' +
    '<b>开盘价:</b> %{customdata[0]:.2f}<br>' +
    '<b>成交额:</b> %{customdata[1]:.2f}<br>',
    customdata=list(zip(df['open'], df['amount']))
))

# 设置图表标题和标签
fig.update_layout(
    title='测试图表',
    xaxis_title='日期',
    yaxis_title='收盘价',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=80, b=40),
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

# 显示图表
fig.show()

# 保存图表为HTML文件
fig.write_html('test_plotly.html')
print("图表已保存为 test_plotly.html")
