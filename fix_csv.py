"""
修复CSV文件格式问题
"""

# 读取原始CSV文件
with open('cs_data.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复格式问题
fixed_lines = []
for line in lines:
    # 移除行尾的逗号
    while line.strip().endswith(','):
        line = line.rstrip(',').rstrip() + '\n'
    fixed_lines.append(line)

# 写回修复后的文件
with open('cs_data_fixed.csv', 'w', encoding='utf-8-sig') as f:
    f.writelines(fixed_lines)

print("CSV文件已修复，保存为 cs_data_fixed.csv")
