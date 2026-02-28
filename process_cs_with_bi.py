"""
使用bi.py中的函数处理CS数据
"""

import sys
import os
import io
import pandas as pd

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入bi.py中的函数
    from bi import read_table, infer_types_and_convert
    print("✅ 成功导入所需函数")
    
    # 原始JSON数据
data = {
    "code": 200,
    "msg": "yyyp_lease_annual",
    "data": {
        "current_page": 1,
        "data": [
            {
                "id": 6424,
                "name": "Tec-9 | 钛片 (崭新出厂)",
                "buff_price_chg": -0.01,
                "exterior_localized_name": "崭新出厂",
                "statistic": 13773,
                "rarity_localized_name": "受限",
                "img": "https://g.fp.ps.netease.com/market/file/5aa0999b20e3db1b36e5b7baVyy2O5i4",
                "buff_sell_price": 146.78,
                "steam_sell_price": 206.0,
                "steam_buy_price": 164.74,
                "buff_buy_price": 142.0,
                "yyyp_lease_price": 0.6,
                "yyyp_long_lease_price": 0.36,
                "yyyp_sell_price": 144.5,
                "yyyp_buy_price": 141.0,
                "buff_buy_num": 12,
                "yyyp_sell_num": 119,
                "yyyp_buy_num": 31,
                "steam_sell_num": 21,
                "steam_buy_num": 2237,
                "buff_sell_num": 42,
                "sell_price_1": -0.01,
                "sell_price_7": -33.21,
                "sell_price_15": 41.78,
                "sell_price_30": 11.78,
                "sell_price_90": 91.88,
                "sell_price_180": 100.98,
                "sell_price_365": 104.48,
                "created_at": "2026-02-27T16:05:28",
                "sell_price_rate_1": -0.01,
                "sell_price_rate_7": -18.45,
                "sell_price_rate_15": 39.79,
                "sell_price_rate_30": 8.73,
                "sell_price_rate_90": 167.36,
                "sell_price_rate_180": 220.48,
                "sell_price_rate_365": 247.0,
                "rank_num": 479,
                "yyyp_lease_annual": 79.72
            },
            {
                "id": 2629,
                "name": "P2000（纪念品） | 渐变琥珀 (久经沙场)",
                "buff_price_chg": 0.0,
                "exterior_localized_name": "久经沙场",
                "statistic": 923,
                "rarity_localized_name": "受限",
                "img": "https://g.fp.ps.netease.com/market/file/5aa0aa1246072b42939cc8e7MJWgOPxt",
                "buff_sell_price": 135.0,
                "steam_sell_price": 181.63,
                "steam_buy_price": 171.98,
                "buff_buy_price": 126.0,
                "yyyp_lease_price": 0.6,
                "yyyp_long_lease_price": 0.4,
                "yyyp_sell_price": 145.0,
                "yyyp_buy_price": 112.0,
                "buff_buy_num": 7,
                "yyyp_sell_num": 19,
                "yyyp_buy_num": 7,
                "steam_sell_num": 9,
                "steam_buy_num": 165,
                "buff_sell_num": 33,
                "sell_price_1": 0.0,
                "sell_price_7": 0.0,
                "sell_price_15": 5.51,
                "sell_price_30": 3.0,
                "sell_price_90": -4.0,
                "sell_price_180": 26.1,
                "sell_price_365": 24.0,
                "created_at": "2026-02-27T16:05:28",
                "sell_price_rate_1": 0.0,
                "sell_price_rate_7": 0.0,
                "sell_price_rate_15": 4.25,
                "sell_price_rate_30": 2.27,
                "sell_price_rate_90": -2.88,
                "sell_price_rate_180": 23.97
            },
            {
                "name": "（纪念品） | 晶红石英 (崭新出厂)",
                "buff_price_chg": 0.0,
                "exterior_localized_name": "崭新出厂",
                "statistic": 724,
                "rarity_localized_name": "受限",
                "img": "https://g.fp.ps.netease.com/market/file/5aa0998c143cfa42419c0a3fXDABYpBf",
                "buff_sell_price": 199.5,
                "steam_sell_price": 0.0,
                "steam_buy_price": 242.19,
                "buff_buy_price": 151.0,
                "yyyp_lease_price": 1.0,
                "yyyp_long_lease_price": 0.3,
                "yyyp_sell_price": 242.0,
                "yyyp_buy_price": 175.0,
                "buff_buy_num": 7,
                "yyyp_sell_num": 14,
                "yyyp_buy_num": 5,
                "steam_sell_num": 0,
                "steam_buy_num": 235,
                "buff_sell_num": 24,
                "sell_price_1": 0.0,
                "sell_price_7": -43.0,
                "sell_price_15": -43.0,
                "sell_price_30": -43.5,
                "sell_price_90": -5.5,
                "sell_price_180": 6.62,
                "sell_price_365": 7.4,
                "created_at": "2026-02-27T16:05:28",
                "sell_price_rate_1": 0.0,
                "sell_price_rate_7": -17.73,
                "sell_price_rate_15": -17.73,
                "sell_price_rate_30": -17.9,
                "sell_price_rate_90": -2.68,
                "sell_price_rate_180": 3.43,
                "sell_price_rate_365": 3.85,
                "rank_num": 16880,
                "yyyp_lease_annual": 79.34
            }
        ],
        "recently_data": {}
    }
}
    
    # 提取数据部分
data_list = data['data']['data']
    
    # 转换为DataFrame
df = pd.DataFrame(data_list)
    
    # 保存为CSV文件
temp_csv = "cs_data_temp.csv"
df.to_csv(temp_csv, index=False, encoding='utf-8-sig')
    
    # 读取CSV文件并使用bi.py的函数处理
with open(temp_csv, "rb") as f:
    file_bytes = f.read()
    
processed_df = read_table(file_bytes, temp_csv)
processed_df, type_map = infer_types_and_convert(processed_df)
    
    print(f"✅ 数据处理成功，形状: {processed_df.shape}")
print(f"✅ 字段类型: {type_map}")
print(f"✅ 数据预览:\n{processed_df.head()}")
    
    # 保存处理后的数据
processed_df.to_csv('cs_data_processed.csv', index=False, encoding='utf-8-sig')
print("\n处理后的数据已保存为 cs_data_processed.csv")
    
    # 清理临时文件
if os.path.exists(temp_csv):
    os.remove(temp_csv)
    
print("\n数据处理完成！")
    
except Exception as e:
    print(f"❌ 处理失败: {str(e)}")
    import traceback
    traceback.print_exc()
