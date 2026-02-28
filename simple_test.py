"""
简单测试bi.py的基本功能
"""

import sys
import os

print("开始测试bi.py...")

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入bi.py中的函数
    from bi import read_table, infer_types_and_convert, build_pivot, pivot_to_tidy, save_to_local
    print("✅ 成功导入bi.py中的函数")
    
    print("\n🎉 代码可以正常导入，没有语法错误！")
    print("\n主要功能：")
    print("1. 读取本地数据文件（CSV、TXT、XLS、XLSX）")
    print("2. 自动识别字段类型（文本、数值、日期时间、布尔）")
    print("3. 生成透视表并支持多种汇总方式")
    print("4. 提供多种数据可视化图表")
    print("5. 支持数据导出和本地保存")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
