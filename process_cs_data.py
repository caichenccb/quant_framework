"""
处理和分析CS数据
"""

import pandas as pd

# 读取CSV文件
df = pd.read_csv('cs_data_clean.csv')

# 清理数据
# 1. 清理img字段中的空格和反引号
df['img'] = df['img'].str.strip().str.replace('`', '')

# 2. 处理缺失值
print("\n缺失值统计:")
print(df.isnull().sum())

# 3. 格式化日期字段
df['created_at'] = pd.to_datetime(df['created_at'])

# 4. 计算一些衍生指标
# 计算不同平台价格差异
df['price_diff_buff_steam'] = df['buff_sell_price'] - df['steam_sell_price']
df['price_diff_yyyp_buff'] = df['yyyp_sell_price'] - df['buff_sell_price']

# 计算租赁回报率
df['lease_return_rate'] = (df['yyyp_lease_price'] * 365) / df['yyyp_sell_price'] * 100

# 显示处理后的数据
print("\n处理后的数据形状:", df.shape)
print("\n处理后的数据前5行:")
print(df.head())

# 基本统计分析
print("\n数值字段统计:")
num_cols = df.select_dtypes(include=['float64', 'int64']).columns
print(df[num_cols].describe())

# 保存处理后的数据
df.to_csv('cs_data_processed.csv', index=False, encoding='utf-8-sig')
print("\n处理后的数据已保存为 cs_data_processed.csv")

print("\n数据处理完成！")
