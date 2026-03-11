"""
CS饰品租赁市场 BI看板可视化代码生成器
====================================
基于ECharts生成完整的BI看板图表配置
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

class BIDashboardCharts:
    """BI看板图表生成器"""

    def __init__(self, data_file='cs出租数据_处理后.csv'):
        """
        初始化图表生成器

        Parameters:
        -----------
        data_file : str
            数据文件路径
        """
        self.df = pd.read_csv(data_file)
        self.charts = []

    def generate_kpi_dashboard(self):
        """生成KPI仪表盘"""
        print("生成KPI仪表盘...")

        # 计算KPI指标
        total_items = len(self.df)
        avg_return = self.df['年化租金收益率'].mean()
        avg_price = self.df['buff在售价'].mean()
        abnormal_count = len(self.df[self.df['价格异常标签'] == '异常波动'])
        hot_items = len(self.df[self.df['热度等级'] == '超热门'])

        kpi_chart = {
            "title": {
                "text": "CS饰品租赁市场核心指标",
                "left": "center",
                "textStyle": {"fontSize": 18, "fontWeight": "bold"}
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": ["饰品总数", "平均收益率", "平均价格", "异常商品", "超热门"],
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "yAxis": {
                "type": "value",
                "name": "数值",
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "series": [{
                "name": "核心指标",
                "type": "bar",
                "data": [
                    {"value": total_items, "itemStyle": {"color": "#d97757"}},
                    {"value": round(avg_return, 2), "itemStyle": {"color": "#6a9bcc"}},
                    {"value": round(avg_price, 2), "itemStyle": {"color": "#788c5d"}},
                    {"value": abnormal_count, "itemStyle": {"color": "#c4a35a"}},
                    {"value": hot_items, "itemStyle": {"color": "#8b7cb6"}}
                ],
                "label": {"show": True, "position": "top", "formatter": "{c}"},
                "itemStyle": {"borderRadius": [5, 5, 0, 0]}
            }],
            "tooltip": {"trigger": "axis"}
        }

        self.charts.append(("KPI仪表盘", kpi_chart))
        return kpi_chart

    def generate_return_distribution(self):
        """生成收益率分布图"""
        print("生成收益率分布图...")

        # 收益率分桶
        bins = [0, 20, 40, 60, 80, 100]
        labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
        self.df['收益区间'] = pd.cut(self.df['年化租金收益率'], bins=bins, labels=labels)

        return_dist = self.df['收益区间'].value_counts().sort_index()

        chart = {
            "title": {
                "text": "年化租金收益率分布",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": return_dist.index.tolist(),
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "yAxis": {
                "type": "value",
                "name": "商品数量",
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "series": [{
                "name": "商品数量",
                "type": "bar",
                "data": return_dist.values.tolist(),
                "itemStyle": {"color": "#6a9bcc", "borderRadius": [5, 5, 0, 0]},
                "label": {"show": True, "position": "top"}
            }],
            "tooltip": {"trigger": "axis", "formatter": "{b}: {c}个"}
        }

        self.charts.append(("收益率分布", chart))
        return chart

    def generate_price_comparison(self):
        """生成平台价格对比散点图"""
        print("生成平台价格对比图...")

        # 按热度排名分组，避免数据点过多
        sample_df = self.df.sample(n=min(200, len(self.df)), random_state=42)

        chart = {
            "title": {
                "text": "Buff vs Steam 价格对比",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "grid": {"left": "8%", "right": "8%", "bottom": "10%", "containLabel": True},
            "xAxis": {
                "type": "value",
                "name": "Buff价格(元)",
                "nameLocation": "middle",
                "nameGap": 30,
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}},
                "scale": True
            },
            "yAxis": {
                "type": "value",
                "name": "Steam价格(元)",
                "nameLocation": "middle",
                "nameGap": 40,
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}},
                "scale": True
            },
            "series": [{
                "name": "饰品",
                "type": "scatter",
                "data": [
                    [row['buff在售价'], row['steam在售价']]
                    for _, row in sample_df.iterrows()
                ],
                "symbolSize": function_symbol_size(sample_df['饰品热度排名']),
                "itemStyle": {"color": "#d97757", "opacity": 0.6}
            }],
            "tooltip": {
                "trigger": "item",
                "formatter": "Buff: {c0}元<br/>Steam: {c1}元"
            }
        }

        self.charts.append(("平台价格对比", chart))
        return chart

    def generate_abnormal_monitor(self):
        """生成异常监控图"""
        print("生成异常监控图...")

        abnormal_df = self.df[self.df['价格异常标签'] == '异常波动'].copy()

        if len(abnormal_df) == 0:
            abnormal_df = self.df.nlargest(10, '近24小时变动率').copy()
            abnormal_df['异常类型'] = '24h波动'

        top_abnormal = abnormal_df.nlargest(15, '近24小时变动率')

        chart = {
            "title": {
                "text": "价格波动异常监控(Top 15)",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "15%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": top_abnormal['饰品名称'].str[:15].tolist(),
                "axisLabel": {"color": "#666", "rotate": 45},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "yAxis": {
                "type": "value",
                "name": "24h变动率(%)",
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "series": [{
                "name": "24h变动率",
                "type": "bar",
                "data": [
                    {
                        "value": row['近24小时变动率'],
                        "itemStyle": {
                            "color": "#ee6666" if row['近24小时变动率'] < 0 else "#91cc75"
                        }
                    }
                    for _, row in top_abnormal.iterrows()
                ],
                "label": {"show": True, "position": "top", "formatter": "{c}%"}
            }],
            "tooltip": {"trigger": "axis", "formatter": "{b}: {c}%"}
        }

        self.charts.append(("异常监控", chart))
        return chart

    def generate_heat_map(self):
        """生成供需平衡热力图"""
        print("生成供需平衡热力图...")

        # 创建品质x价格区间的供需比热力图
        pivot_table = self.df.pivot_table(
            values='供需比_buff',
            index='品质',
            columns='价格区间',
            aggfunc='mean'
        )

        x_data = pivot_table.columns.tolist()
        y_data = pivot_table.index.tolist()
        data = []

        for i, quality in enumerate(y_data):
            for j, price_range in enumerate(x_data):
                value = pivot_table.loc[quality, price_range]
                if pd.notna(value):
                    data.append([j, i, round(value, 2)])

        chart = {
            "title": {
                "text": "供需平衡热力图(按品质×价格区间)",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "10%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": x_data,
                "axisLabel": {"color": "#666", "rotate": 30},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "yAxis": {
                "type": "category",
                "data": y_data,
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "visualMap": {
                "min": 0,
                "max": 3,
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "0%",
                "inRange": {"color": ["#c4a35a", "#91cc75", "#6a9bcc", "#5470c6"]}
            },
            "series": [{
                "name": "供需比",
                "type": "heatmap",
                "data": data,
                "label": {"show": True, "formatter": "{c}"},
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}}
            }],
            "tooltip": {"trigger": "item", "formatter": "{b} x {a}: 供需比 {c}"}
        }

        self.charts.append(("供需热力图", chart))
        return chart

    def generate_hotness_distribution(self):
        """生成热度分布环形图"""
        print("生成热度分布环形图...")

        hot_dist = self.df['热度等级'].value_counts()

        colors = ["#d97757", "#6a9bcc", "#788c5d", "#c4a35a", "#8b7cb6"]

        data = [
            {"value": count, "name": level, "itemStyle": {"color": colors[i % len(colors)]}}
            for i, (level, count) in enumerate(hot_dist.items())
        ]

        chart = {
            "title": {
                "text": "饰品热度等级分布",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "top": "middle",
                "data": hot_dist.index.tolist()
            },
            "series": [{
                "name": "热度等级",
                "type": "pie",
                "radius": ["40%", "70%"],
                "center": ["60%", "50%"],
                "data": data,
                "label": {"show": True, "formatter": "{b}: {d}%"},
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0,0,0,0.5)"
                    }
                }
            }],
            "tooltip": {"trigger": "item", "formatter": "{b}: {c}个 ({d}%)"}
        }

        self.charts.append(("热度分布", chart))
        return chart

    def generate_top_bottom_returns(self):
        """生成Top/Bottom收益双向条形图"""
        print("生成Top/Bottom收益对比图...")

        top_returns = self.df.nlargest(10, '年化租金收益率')[['饰品名称', '年化租金收益率']]
        bottom_returns = self.df.nsmallest(10, '年化租金收益率')[['饰品名称', '年化租金收益率']]

        chart = {
            "title": {
                "text": "Top/Bottom 收益率商品对比",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "grid": [
                {"left": "3%", "right": "55%", "top": "10%", "height": "35%", "containLabel": True},
                {"left": "3%", "right": "55%", "top": "55%", "height": "35%", "containLabel": True}
            ],
            "xAxis": [
                {
                    "type": "value",
                    "inverse": False,
                    "axisLabel": {"show": False},
                    "axisLine": {"show": False},
                    "axisTick": {"show": False},
                    "splitLine": {"show": False}
                },
                {
                    "gridIndex": 1,
                    "type": "value",
                    "inverse": True,
                    "axisLabel": {"show": False},
                    "axisLine": {"show": False},
                    "axisTick": {"show": False},
                    "splitLine": {"show": False}
                }
            ],
            "yAxis": [
                {
                    "type": "category",
                    "data": top_returns['饰品名称'].str[:20].tolist(),
                    "axisLabel": {"color": "#666"},
                    "axisLine": {"lineStyle": {"color": "#666"}},
                    "position": "right"
                },
                {
                    "gridIndex": 1,
                    "type": "category",
                    "data": bottom_returns['饰品名称'].str[:20].tolist(),
                    "axisLabel": {"color": "#666"},
                    "axisLine": {"lineStyle": {"color": "#666"}},
                    "position": "right"
                }
            ],
            "series": [
                {
                    "name": "高收益",
                    "type": "bar",
                    "data": [
                        {"value": row['年化租金收益率'], "itemStyle": {"color": "#91cc75"}}
                        for _, row in top_returns.iterrows()
                    ],
                    "label": {"show": True, "position": "right", "formatter": "{c}%"}
                },
                {
                    "name": "低收益",
                    "type": "bar",
                    "xAxisIndex": 1,
                    "yAxisIndex": 1,
                    "data": [
                        {"value": row['年化租金收益率'], "itemStyle": {"color": "#ee6666"}}
                        for _, row in bottom_returns.iterrows()
                    ],
                    "label": {"show": True, "position": "right", "formatter": "{c}%"}
                }
            ],
            "tooltip": {"trigger": "axis", "formatter": "{b}: {c}%"}
        }

        self.charts.append(("Top/Bottom收益", chart))
        return chart

    def generate_price_return_correlation(self):
        """生成价格与收益率散点图"""
        print("生成价格收益率关系图...")

        sample_df = self.df.sample(n=min(300, len(self.df)), random_state=42)

        # 按收益等级着色
        color_map = {
            '低收益': '#b0aea5',
            '中低收益': '#c4a35a',
            '中等收益': '#6a9bcc',
            '中高收益': '#91cc75',
            '高收益': '#d97757'
        }

        data = [
            {
                "value": [row['buff在售价'], row['年化租金收益率']],
                "itemStyle": {"color": color_map.get(row['收益等级'], '#b0aea5')}
            }
            for _, row in sample_df.iterrows()
        ]

        chart = {
            "title": {
                "text": "价格与收益率关系分析",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "grid": {"left": "8%", "right": "8%", "bottom": "10%", "containLabel": True},
            "xAxis": {
                "type": "value",
                "name": "Buff价格(元)",
                "nameLocation": "middle",
                "nameGap": 30,
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}},
                "scale": True
            },
            "yAxis": {
                "type": "value",
                "name": "年化收益率(%)",
                "nameLocation": "middle",
                "nameGap": 40,
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}},
                "scale": True
            },
            "series": [{
                "name": "饰品",
                "type": "scatter",
                "data": data,
                "symbolSize": 8
            }],
            "tooltip": {
                "trigger": "item",
                "formatter": "价格: {c0}元<br/>收益率: {c1}%"
            }
        }

        self.charts.append(("价格收益率关系", chart))
        return chart

    def generate_rental_price_comparison(self):
        """生成租赁价格对比图"""
        print("生成租赁价格对比图...")

        # 按价格区间分组
        rental_data = self.df.groupby('价格区间').agg({
            'yyyp短租价格': 'mean',
            'yyyp长租价格': 'mean'
        }).round(2)

        chart = {
            "title": {
                "text": "不同价格区间的租赁价格对比",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "legend": {
                "data": ["短租价格", "长租价格"],
                "top": "top"
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": rental_data.index.tolist(),
                "axisLabel": {"color": "#666", "rotate": 30},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "yAxis": {
                "type": "value",
                "name": "租赁价格(元/天)",
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "series": [
                {
                    "name": "短租价格",
                    "type": "bar",
                    "data": rental_data['yyyp短租价格'].tolist(),
                    "itemStyle": {"color": "#6a9bcc", "borderRadius": [5, 5, 0, 0]}
                },
                {
                    "name": "长租价格",
                    "type": "bar",
                    "data": rental_data['yyyp长租价格'].tolist(),
                    "itemStyle": {"color": "#d97757", "borderRadius": [5, 5, 0, 0]}
                }
            ],
            "tooltip": {"trigger": "axis", "formatter": "{b}<br/>{a}: {c}元/天"}
        }

        self.charts.append(("租赁价格对比", chart))
        return chart

    def generate_three_platform_matrix(self):
        """生成三平台价格矩阵"""
        print("生成三平台价格矩阵...")

        # 创建价格区间交叉表
        self.df['buff价格区间'] = pd.cut(
            self.df['buff在售价'],
            bins=[0, 100, 200, 300, 500, float('inf')],
            labels=['0-100', '100-200', '200-300', '300-500', '500+']
        )

        self.df['steam价格区间'] = pd.cut(
            self.df['steam在售价'],
            bins=[0, 150, 250, 400, 600, float('inf')],
            labels=['0-150', '150-250', '250-400', '400-600', '600+']
        )

        pivot_table = self.df.pivot_table(
            values='饰品id',
            index='buff价格区间',
            columns='steam价格区间',
            aggfunc='count'
        ).fillna(0)

        x_data = pivot_table.columns.tolist()
        y_data = pivot_table.index.tolist()
        data = []

        for i, buff_range in enumerate(y_data):
            for j, steam_range in enumerate(x_data):
                value = pivot_table.loc[buff_range, steam_range]
                data.append([j, i, int(value)])

        chart = {
            "title": {
                "text": "三平台价格区间分布矩阵",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "10%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": ["Steam " + x for x in x_data],
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "yAxis": {
                "type": "category",
                "data": ["Buff " + y for y in y_data],
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "visualMap": {
                "min": 0,
                "max": pivot_table.values.max(),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "0%",
                "inRange": {"color": ["#f0f0f0", "#c4a35a", "#d97757", "#5470c6"]}
            },
            "series": [{
                "name": "商品数量",
                "type": "heatmap",
                "data": data,
                "label": {"show": True, "formatter": "{c}"},
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}}
            }],
            "tooltip": {"trigger": "item", "formatter": "{b} x {a}: {c}个"}
        }

        self.charts.append(("价格区间矩阵", chart))
        return chart

    def generate_quality_return_analysis(self):
        """生成品质收益率分析图"""
        print("生成品质收益率分析图...")

        quality_return = self.df.groupby('品质')['年化租金收益率'].agg(['mean', 'count']).round(2)
        quality_return = quality_return.sort_values('mean', ascending=False)

        chart = {
            "title": {
                "text": "不同品质的收益率水平",
                "left": "center",
                "textStyle": {"fontSize": 16}
            },
            "legend": {"data": ["平均收益率", "商品数量"], "top": "top"},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": quality_return.index.tolist(),
                "axisLabel": {"color": "#666"},
                "axisLine": {"lineStyle": {"color": "#666"}}
            },
            "yAxis": [
                {
                    "type": "value",
                    "name": "平均收益率(%)",
                    "position": "left",
                    "axisLabel": {"color": "#666"},
                    "axisLine": {"lineStyle": {"color": "#666"}}
                },
                {
                    "type": "value",
                    "name": "商品数量",
                    "position": "right",
                    "axisLabel": {"color": "#666"},
                    "axisLine": {"lineStyle": {"color": "#666"}}
                }
            ],
            "series": [
                {
                    "name": "平均收益率",
                    "type": "bar",
                    "data": quality_return['mean'].tolist(),
                    "itemStyle": {"color": "#6a9bcc", "borderRadius": [5, 5, 0, 0]}
                },
                {
                    "name": "商品数量",
                    "type": "line",
                    "yAxisIndex": 1,
                    "data": quality_return['count'].tolist(),
                    "itemStyle": {"color": "#d97757"},
                    "symbol": "circle",
                    "symbolSize": 8
                }
            ],
            "tooltip": {"trigger": "axis", "formatter": "{b}<br/>平均收益率: {c0}%<br/>商品数量: {c1}"}
        }

        self.charts.append(("品质收益率分析", chart))
        return chart

    def _convert_to_serializable(self, data):
        """将数据转换为可序列化格式"""
        if isinstance(data, dict):
            return {k: self._convert_to_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_serializable(item) for item in data]
        elif isinstance(data, pd.Series):
            return self._convert_to_serializable(data.tolist())
        elif isinstance(data, (pd.DataFrame, pd.Series)):
            return data.to_dict(orient='records')
        elif isinstance(data, np.generic):
            return data.item()
        elif pd.isna(data):
            return None
        elif isinstance(data, np.ndarray):
            return data.tolist()
        else:
            return data

    def generate_all_charts(self):
        """生成所有图表"""
        print("\n" + "=" * 70)
        print("开始生成BI看板图表")
        print("=" * 70 + "\n")

        # 生成所有图表
        self.generate_kpi_dashboard()
        self.generate_return_distribution()
        self.generate_price_comparison()
        self.generate_abnormal_monitor()
        self.generate_heat_map()
        self.generate_hotness_distribution()
        self.generate_top_bottom_returns()
        self.generate_price_return_correlation()
        self.generate_rental_price_comparison()
        self.generate_three_platform_matrix()
        self.generate_quality_return_analysis()

        print(f"\n✓ 共生成 {len(self.charts)} 个图表")

        return self.charts

    def export_charts_to_html(self, output_file='bi_dashboard.html'):
        """导出所有图表到HTML文件"""
        print(f"\n正在生成HTML文件...")

        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CS饰品租赁市场 BI看板</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            margin: 5px 0;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .chart-full {{
            grid-column: 1 / -1;
        }}
        .chart {{
            width: 100%;
            height: 400px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #999;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CS饰品租赁市场 BI看板</h1>
        <p>更新时间: {update_time}</p>
        <p>数据来源: cs日出租排行</p>
    </div>

    <div class="dashboard-grid">
        {chart_divs}
    </div>

    <div class="footer">
        <p>数据可视化 powered by ECharts</p>
    </div>

    <script>
        {chart_scripts}
    </script>
</body>
</html>
        """

        # 生成图表容器和脚本
        chart_divs = ""
        chart_scripts = ""

        for i, (chart_name, chart_config) in enumerate(self.charts):
            chart_id = f"chart_{i}"

            # 确定容器类
            container_class = "chart-container"
            if chart_name in ["KPI仪表盘", "平台价格对比", "价格收益率关系", "价格区间矩阵"]:
                container_class += " chart-full"

            chart_divs += f"""
        <div class="{container_class}">
            <div id="{chart_id}" class="chart"></div>
        </div>
"""

            chart_scripts += f"""
        // {chart_name}
        var {chart_id}_chart = echarts.init(document.getElementById('{chart_id}'));
        {chart_id}_chart.setOption({json.dumps(self._convert_to_serializable(chart_config), ensure_ascii=False, indent=12)});
"""

        # 填充模板
        html_content = html_template.format(
            update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            chart_divs=chart_divs,
            chart_scripts=chart_scripts
        )

        # 保存HTML文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ HTML文件已生成: {output_file}")
        return output_file

    def export_charts_to_json(self, output_file='bi_charts_config.json'):
        """导出图表配置到JSON文件"""
        charts_dict = {}
        for chart_name, chart_config in self.charts:
            charts_dict[chart_name] = self._convert_to_serializable(chart_config)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(charts_dict, f, ensure_ascii=False, indent=2)

        print(f"✓ 图表配置已导出: {output_file}")
        return output_file


def function_symbol_size(rank_data):
    """根据热度排名生成散点大小（辅助函数，实际在代码中会内联）"""
    # 这个函数只是为了说明，实际使用时会在生成图表时直接计算
    pass


def main():
    """主函数"""
    # 创建图表生成器
    generator = BIDashboardCharts('cs出租数据_处理后.csv')

    # 生成所有图表
    generator.generate_all_charts()

    # 导出到HTML
    generator.export_charts_to_html()

    # 导出到JSON
    generator.export_charts_to_json()

    print("\n" + "=" * 70)
    print("图表生成完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
