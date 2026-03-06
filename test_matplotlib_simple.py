"""
测试matplotlib可视化（仅保存图片）
"""

import matplotlib
matplotlib.use('Agg')  # 使用Agg后端，不需要显示窗口
import matplotlib.pyplot as plt
import numpy as np

# 创建一个简单的图表
fig, ax = plt.subplots(figsize=(12, 6))

# 绘制一条线
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax.plot(x, y, label='Sin Curve')

# 设置图表标题和标签
ax.set_title('Test Plot')
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.legend()

# 保存图表为图片
plt.savefig('test_plot.png')
print("图表已保存为 test_plot.png")
