"""
CS饰品租赁市场 BI看板数据处理系统
====================================
功能：
1. 读取Excel数据（支持大数据量）
2. 数据清洗与格式转换
3. 创建衍生分析指标
4. 异常检测与分类
5. 数据质量检查
6. 导出处理后的数据
7. 生成BI看板所需的数据摘要
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

class CSDataProcessor:
    """CS饰品数据处理类"""

    def __init__(self, file_path):
        """
        初始化数据处理器

        Parameters:
        -----------
        file_path : str
            Excel文件路径
        """
        self.file_path = file_path
        self.df_raw = None
        self.df_clean = None
        self.summary_stats = {}

    def read_data(self):
        """读取Excel数据，支持大数据量"""
        print("=" * 70)
        print("步骤1: 数据读取")
        print("=" * 70)

        try:
            # 读取Excel文件
            self.df_raw = pd.read_excel(self.file_path, sheet_name='cs日出租排行')

            print(f"✓ 数据读取成功")
            print(f"  数据维度: {self.df_raw.shape[0]}行 x {self.df_raw.shape[1]}列")
            print(f"  字段数量: {len(self.df_raw.columns)}")
            print(f"  内存占用: {self.df_raw.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

            # 显示前3行数据预览
            print(f"\n前3行数据预览:")
            print(self.df_raw.head(3).to_string())

            # 显示字段列表
            print(f"\n字段列表:")
            for i, col in enumerate(self.df_raw.columns, 1):
                print(f"  {i:2d}. {col}")

            return True

        except Exception as e:
            print(f"✗ 数据读取失败: {str(e)}")
            return False

    def clean_and_transform(self):
        """数据清洗与格式转换"""
        print("\n" + "=" * 70)
        print("步骤2: 数据清洗与格式转换")
        print("=" * 70)

        if self.df_raw is None:
            print("✗ 请先读取数据")
            return False

        self.df_clean = self.df_raw.copy()

        # 2.1 转换时间字段（处理T分隔符格式）
        print("\n[2.1] 时间字段转换")
        try:
            self.df_clean['排行榜更新时间'] = pd.to_datetime(
                self.df_clean['排行榜更新时间'],
                format='ISO8601'  # 自动识别T分隔符的ISO格式
            )
            self.df_clean['更新日期'] = self.df_clean['排行榜更新时间'].dt.date
            self.df_clean['更新时间_小时'] = self.df_clean['排行榜更新时间'].dt.hour
            self.df_clean['更新时间_星期'] = self.df_clean['排行榜更新时间'].dt.dayofweek
            self.df_clean['更新时间_星期名称'] = self.df_clean['排行榜更新时间'].dt.day_name()

            print(f"✓ 时间字段转换成功")
            print(f"  时间范围: {self.df_clean['排行榜更新时间'].min()} ~ {self.df_clean['排行榜更新时间'].max()}")

        except Exception as e:
            print(f"✗ 时间字段转换失败: {str(e)}")
            return False

        # 2.2 数值型字段验证与清洗
        print("\n[2.2] 数值型字段清洗")

        numeric_columns = [
            '饰品id', '近24小时变动率', '统计数量', 'buff在售价', 'steam在售价',
            'steam求购价', 'buff求购价', 'yyyp短租价格', 'yyyp长租价格',
            'yyyp在售价', 'yyyp求购价', 'buff求购数量', 'yyyp在售数量',
            'yyyp求购数量', 'steam在售数量', 'steam求购数量', 'buff在售数量',
            '近1天价格变动', '近7天价格变动', '近15天价格变动', '近30天价格变动',
            '近90天价格变动', '近180天价格变动', '近365天价格变动',
            '近1天价格变动率', '近7天价格变动率', '近15天价格变动率',
            '近30天价格变动率', '近90天价格变动率', '近180天价格变动率',
            '近365天价格变动率', '饰品热度排名', '年化租金收益率'
        ]

        for col in numeric_columns:
            if col in self.df_clean.columns:
                # 转换为数值类型，无效值转为NaN
                self.df_clean[col] = pd.to_numeric(self.df_clean[col], errors='coerce')

        print(f"✓ 数值型字段转换完成")

        # 2.3 处理缺失值和异常值
        print("\n[2.3] 缺失值与异常值处理")

        # 统计缺失值
        missing_stats = self.df_clean.isnull().sum()
        missing_pct = (missing_stats / len(self.df_clean) * 100).round(2)

        print(f"\n缺失值统计:")
        for col in self.df_clean.columns:
            if missing_stats[col] > 0:
                print(f"  {col}: {missing_stats[col]}条 ({missing_pct[col]}%)")

        # 处理关键字段的缺失值
        # 价格字段缺失值用0填充或中位数填充（根据业务逻辑）
        price_columns = ['buff在售价', 'steam在售价', 'yyyp短租价格', 'yyyp长租价格']
        for col in price_columns:
            if col in self.df_clean.columns:
                median_val = self.df_clean[col].median()
                self.df_clean[col] = self.df_clean[col].fillna(median_val)

        print(f"\n✓ 缺失值处理完成")

        return True

    def create_derived_metrics(self):
        """创建衍生分析指标"""
        print("\n" + "=" * 70)
        print("步骤3: 创建衍生分析指标")
        print("=" * 70)

        metrics_created = []

        # 3.1 价格相关指标
        print("\n[3.1] 价格维度指标")

        # 价格平台差异
        if 'buff在售价' in self.df_clean.columns and 'steam在售价' in self.df_clean.columns:
            self.df_clean['价格平台差异'] = self.df_clean['steam在售价'] - self.df_clean['buff在售价']
            self.df_clean['价格平台差异率'] = (
                (self.df_clean['价格平台差异'] / self.df_clean['buff在售价'].replace(0, np.nan)) * 100
            ).round(2)
            metrics_created.extend(['价格平台差异', '价格平台差异率'])
            print("  ✓ 价格平台差异及差异率")

        # 短租长租比
        if 'yyyp短租价格' in self.df_clean.columns and 'yyyp长租价格' in self.df_clean.columns:
            self.df_clean['短租长租比'] = (
                self.df_clean['yyyp短租价格'] / self.df_clean['yyyp长租价格'].replace(0, np.nan)
            ).round(2)
            metrics_created.append('短租长租比')
            print("  ✓ 短租长租价格比")

        # 3.2 供需平衡指标
        print("\n[3.2] 供需维度指标")

        # Buff供需比
        if 'buff在售数量' in self.df_clean.columns and 'buff求购数量' in self.df_clean.columns:
            self.df_clean['供需比_buff'] = (
                self.df_clean['buff在售数量'] / self.df_clean['buff求购数量'].replace(0, np.nan)
            ).replace([np.inf, -np.inf], np.nan).round(2)
            metrics_created.append('供需比_buff')
            print("  ✓ Buff供需比")

        # Steam供需比
        if 'steam在售数量' in self.df_clean.columns and 'steam求购数量' in self.df_clean.columns:
            self.df_clean['供需比_steam'] = (
                self.df_clean['steam在售数量'] / self.df_clean['steam求购数量'].replace(0, np.nan)
            ).replace([np.inf, -np.inf], np.nan).round(2)
            metrics_created.append('供需比_steam')
            print("  ✓ Steam供需比")

        # YYYP供需比
        if 'yyyp在售数量' in self.df_clean.columns and 'yyyp求购数量' in self.df_clean.columns:
            self.df_clean['供需比_yyyp'] = (
                self.df_clean['yyyp在售数量'] / self.df_clean['yyyp求购数量'].replace(0, np.nan)
            ).replace([np.inf, -np.inf], np.nan).round(2)
            metrics_created.append('供需比_yyyp')
            print("  ✓ YYYP供需比")

        # 3.3 价格综合波动指标
        print("\n[3.3] 价格波动指标")

        # 综合价格变动率（近期权重）
        if all(col in self.df_clean.columns for col in ['近1天价格变动率', '近7天价格变动率', '近30天价格变动率']):
            self.df_clean['综合价格变动率'] = (
                self.df_clean['近1天价格变动率'] * 0.5 +
                self.df_clean['近7天价格变动率'] * 0.3 +
                self.df_clean['近30天价格变动率'] * 0.2
            ).round(2)
            metrics_created.append('综合价格变动率')
            print("  ✓ 综合价格变动率")

        # 3.4 分类维度指标
        print("\n[3.4] 分类维度指标")

        # 热度等级分类
        if '饰品热度排名' in self.df_clean.columns:
            self.df_clean['热度等级'] = pd.cut(
                self.df_clean['饰品热度排名'],
                bins=[0, 500, 2000, 5000, 10000, np.inf],
                labels=['超热门', '热门', '中热度', '低热度', '冷门']
            )
            metrics_created.append('热度等级')
            print("  ✓ 热度等级分类 (超热门/热门/中热度/低热度/冷门)")

        # 收益等级分类
        if '年化租金收益率' in self.df_clean.columns:
            self.df_clean['收益等级'] = pd.cut(
                self.df_clean['年化租金收益率'],
                bins=[0, 20, 40, 60, 80, np.inf],
                labels=['低收益', '中低收益', '中等收益', '中高收益', '高收益']
            )
            metrics_created.append('收益等级')
            print("  ✓ 收益等级分类 (低收益~高收益)")

        # 价格区间分类
        if 'buff在售价' in self.df_clean.columns:
            self.df_clean['价格区间'] = pd.cut(
                self.df_clean['buff在售价'],
                bins=[0, 50, 100, 200, 500, 1000, np.inf],
                labels=['低价位(0-50)', '中低价(50-100)', '中价位(100-200)',
                        '中高价(200-500)', '高价位(500-1000)', '超高价位(1000+)']
            )
            metrics_created.append('价格区间')
            print("  ✓ 价格区间分类")

        # 3.5 异常检测指标
        print("\n[3.5] 异常检测指标")

        # 价格异常检测
        if '近24小时变动率' in self.df_clean.columns and '近7天价格变动率' in self.df_clean.columns:
            conditions = (
                (abs(self.df_clean['近24小时变动率']) > 10) |
                (abs(self.df_clean['近7天价格变动率']) > 30)
            )
            self.df_clean['价格异常标签'] = np.where(conditions, '异常波动', '正常')
            self.df_clean['异常类型'] = np.where(
                (abs(self.df_clean['近24小时变动率']) > 10) & (abs(self.df_clean['近7天价格变动率']) <= 30),
                '24h剧烈波动',
                np.where(
                    (abs(self.df_clean['近24小时变动率']) <= 10) & (abs(self.df_clean['近7天价格变动率']) > 30),
                    '7天剧烈波动',
                    np.where(
                        (abs(self.df_clean['近24小时变动率']) > 10) & (abs(self.df_clean['近7天价格变动率']) > 30),
                        '持续剧烈波动',
                        '正常'
                    )
                )
            )
            metrics_created.extend(['价格异常标签', '异常类型'])
            print("  ✓ 价格异常检测 (24h变动>10% 或 7天变动>30%)")

        # 收益异常检测
        if '年化租金收益率' in self.df_clean.columns:
            self.df_clean['收益异常标签'] = np.where(
                (self.df_clean['年化租金收益率'] > 100) | (self.df_clean['年化租金收益率'] < 10),
                '异常收益',
                '正常收益'
            )
            metrics_created.append('收益异常标签')
            print("  ✓ 收益异常检测 (收益率>100% 或 <10%)")

        print(f"\n✓ 衍生指标创建完成，共创建 {len(metrics_created)} 个指标")

        return True

    def generate_summary_stats(self):
        """生成数据摘要统计"""
        print("\n" + "=" * 70)
        print("步骤4: 生成数据摘要统计")
        print("=" * 70)

        if self.df_clean is None:
            print("✗ 请先进行数据处理")
            return False

        # 4.1 基础KPI指标
        print("\n[4.1] 基础KPI指标")

        kpi_stats = {
            '数据统计': {
                '饰品总数': len(self.df_clean),
                '有价格数据商品数': self.df_clean['buff在售价'].notna().sum() if 'buff在售价' in self.df_clean.columns else 0,
                '有收益率数据商品数': self.df_clean['年化租金收益率'].notna().sum() if '年化租金收益率' in self.df_clean.columns else 0,
            },
            '价格指标': {
                '平均Steam价格': self.df_clean['steam在售价'].mean() if 'steam在售价' in self.df_clean.columns else None,
                '平均Buff价格': self.df_clean['buff在售价'].mean() if 'buff在售价' in self.df_clean.columns else None,
                '平均YYYP短租价格': self.df_clean['yyyp短租价格'].mean() if 'yyyp短租价格' in self.df_clean.columns else None,
                '平均YYYP长租价格': self.df_clean['yyyp长租价格'].mean() if 'yyyp长租价格' in self.df_clean.columns else None,
            },
            '收益指标': {
                '平均年化收益率': self.df_clean['年化租金收益率'].mean() if '年化租金收益率' in self.df_clean.columns else None,
                '最高年化收益率': self.df_clean['年化租金收益率'].max() if '年化租金收益率' in self.df_clean.columns else None,
                '最低年化收益率': self.df_clean['年化租金收益率'].min() if '年化租金收益率' in self.df_clean.columns else None,
                '年化收益率中位数': self.df_clean['年化租金收益率'].median() if '年化租金收益率' in self.df_clean.columns else None,
            },
            '异常指标': {
                '价格异常商品数': len(self.df_clean[self.df_clean['价格异常标签'] == '异常波动']) if '价格异常标签' in self.df_clean.columns else 0,
                '收益异常商品数': len(self.df_clean[self.df_clean['收益异常标签'] == '异常收益']) if '收益异常标签' in self.df_clean.columns else 0,
            }
        }

        # 打印KPI
        print(f"\n数据规模:")
        print(f"  饰品总数: {kpi_stats['数据统计']['饰品总数']:,}")
        print(f"  有价格数据: {kpi_stats['数据统计']['有价格数据商品数']:,}")
        print(f"  有收益率数据: {kpi_stats['数据统计']['有收益率数据商品数']:,}")

        print(f"\n价格指标:")
        for key, value in kpi_stats['价格指标'].items():
            if value is not None:
                print(f"  {key}: {value:.2f}")

        print(f"\n收益指标:")
        for key, value in kpi_stats['收益指标'].items():
            if value is not None:
                print(f"  {key}: {value:.2f}%")

        print(f"\n异常指标:")
        print(f"  价格异常商品: {kpi_stats['异常指标']['价格异常商品数']:,}")
        print(f"  收益异常商品: {kpi_stats['异常指标']['收益异常商品数']:,}")

        self.summary_stats = kpi_stats

        # 4.2 分类分布统计
        print("\n[4.2] 分类分布统计")

        # 品质分布
        if '品质' in self.df_clean.columns:
            print(f"\n按品质分布:")
            quality_dist = self.df_clean['品质'].value_counts().sort_values(ascending=False)
            for quality, count in quality_dist.items():
                pct = round(count / len(self.df_clean) * 100, 1)
                print(f"  {quality}: {count:,}个 ({pct}%)")

        # 热度等级分布
        if '热度等级' in self.df_clean.columns:
            print(f"\n热度等级分布:")
            hot_dist = self.df_clean['热度等级'].value_counts().sort_values(ascending=False)
            for level, count in hot_dist.items():
                pct = round(count / len(self.df_clean) * 100, 1)
                print(f"  {level}: {count:,}个 ({pct}%)")

        # 收益等级分布
        if '收益等级' in self.df_clean.columns:
            print(f"\n收益等级分布:")
            return_dist = self.df_clean['收益等级'].value_counts().sort_values(ascending=False)
            for level, count in return_dist.items():
                pct = round(count / len(self.df_clean) * 100, 1)
                print(f"  {level}: {count:,}个 ({pct}%)")

        # 价格区间分布
        if '价格区间' in self.df_clean.columns:
            print(f"\n价格区间分布:")
            price_dist = self.df_clean['价格区间'].value_counts().sort_values(ascending=False)
            for level, count in price_dist.items():
                pct = round(count / len(self.df_clean) * 100, 1)
                print(f"  {level}: {count:,}个 ({pct}%)")

        # 4.3 Top/Bottom 商品统计
        print("\n[4.3] Top/Bottom 商品统计")

        if '年化租金收益率' in self.df_clean.columns and '饰品名称' in self.df_clean.columns:
            top_returns = self.df_clean.nlargest(10, '年化租金收益率')[['饰品名称', '年化租金收益率', 'buff在售价']]
            bottom_returns = self.df_clean.nsmallest(10, '年化租金收益率')[['饰品名称', '年化租金收益率', 'buff在售价']]

            print(f"\nTop 10 高收益商品:")
            for idx, row in top_returns.iterrows():
                print(f"  {row['饰品名称'][:30]:30s} - 收益率: {row['年化租金收益率']:.2f}% - 价格: {row['buff在售价']:.2f}")

            print(f"\nBottom 10 低收益商品:")
            for idx, row in bottom_returns.iterrows():
                print(f"  {row['饰品名称'][:30]:30s} - 收益率: {row['年化租金收益率']:.2f}% - 价格: {row['buff在售价']:.2f}")

        # 4.4 价格异常商品统计
        if '价格异常标签' in self.df_clean.columns and '饰品名称' in self.df_clean.columns:
            abnormal_items = self.df_clean[self.df_clean['价格异常标签'] == '异常波动']
            if len(abnormal_items) > 0:
                print(f"\n价格异常商品 (Top 10):")
                top_abnormal = abnormal_items.nlargest(10, '近24小时变动率')[['饰品名称', '近24小时变动率', '近7天价格变动率', '异常类型']]
                for idx, row in top_abnormal.iterrows():
                    print(f"  {row['饰品名称'][:30]:30s} - 24h: {row['近24小时变动率']:.2f}% - 7天: {row['近7天价格变动率']:.2f}% - 类型: {row['异常类型']}")
            else:
                print(f"\n✓ 无价格异常商品")

        return True

    def export_data(self, output_file='cs出租数据_处理后.csv'):
        """导出处理后的数据"""
        print("\n" + "=" * 70)
        print("步骤5: 数据导出")
        print("=" * 70)

        if self.df_clean is None:
            print("✗ 请先进行数据处理")
            return False

        try:
            # 导出完整数据
            self.df_clean.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"✓ 完整数据已导出至: {output_file}")
            print(f"  数据维度: {self.df_clean.shape[0]}行 x {self.df_clean.shape[1]}列")
            print(f"  文件大小: {self.df_clean.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

            # 导出数据摘要JSON（供BI看板使用）
            summary_file = 'bi_dashboard_summary.json'
            summary_data = {
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_source': self.file_path,
                'kpi_stats': self._convert_to_serializable(self.summary_stats),
                'field_list': self.df_clean.columns.tolist(),
                'data_shape': {
                    'rows': int(self.df_clean.shape[0]),
                    'columns': int(self.df_clean.shape[1])
                }
            }

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)

            print(f"✓ 数据摘要已导出至: {summary_file}")

            # 导出异常商品清单
            if '价格异常标签' in self.df_clean.columns:
                abnormal_file = '异常商品清单.csv'
                abnormal_data = self.df_clean[self.df_clean['价格异常标签'] == '异常波动']
                if len(abnormal_data) > 0:
                    abnormal_data.to_csv(abnormal_file, index=False, encoding='utf-8-sig')
                    print(f"✓ 异常商品清单已导出至: {abnormal_file} ({len(abnormal_data)}条)")

            return True

        except Exception as e:
            print(f"✗ 数据导出失败: {str(e)}")
            return False

    def _convert_to_serializable(self, data):
        """将数据转换为可序列化格式"""
        if isinstance(data, dict):
            return {k: self._convert_to_serializable(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._convert_to_serializable(item) for item in data]
        elif isinstance(data, (np.integer, np.int64, np.int32)):
            return int(data)
        elif isinstance(data, (np.floating, np.float64, np.float32)):
            return float(data)
        elif isinstance(data, pd.Series):
            return data.tolist()
        elif pd.isna(data):
            return None
        else:
            return data

    def run(self, output_file='cs出租数据_处理后.csv'):
        """执行完整的数据处理流程"""
        print("\n" + "=" * 70)
        print("CS饰品租赁市场 BI数据处理系统")
        print("=" * 70)

        # 步骤1: 读取数据
        if not self.read_data():
            return False

        # 步骤2: 数据清洗与转换
        if not self.clean_and_transform():
            return False

        # 步骤3: 创建衍生指标
        if not self.create_derived_metrics():
            return False

        # 步骤4: 生成摘要统计
        if not self.generate_summary_stats():
            return False

        # 步骤5: 导出数据
        if not self.export_data(output_file):
            return False

        print("\n" + "=" * 70)
        print("数据处理完成！")
        print("=" * 70)

        return True


def main():
    """主函数"""
    # 配置参数
    input_file = 'cs日出租排行.xlsx'
    output_file = 'cs出租数据_处理后.csv'

    # 创建处理器实例
    processor = CSDataProcessor(input_file)

    # 执行处理流程
    processor.run(output_file)


if __name__ == '__main__':
    main()
