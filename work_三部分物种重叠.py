import pandas as pd

# --- 1. 配置 ---
# 输入的 Excel 文件路径
file_path = '/Volumes/CC/6042MAG数据库文件/ABC.xlsx'
# 定义输出的 Excel 文件名
output_filename = '/Volumes/CC/6042MAG数据库文件/ABC_Analysis_Output.xlsx'

try:
    # --- 步骤 2: 读取 Excel 文件 ---
    # 假设第一行是列标题 (A, B, C)
    print(f"正在读取文件: {file_path}")
    df = pd.read_excel(file_path)

    # 确认表格包含 A, B, C 三列
    required_columns = {'A', 'B', 'C'}
    if not required_columns.issubset(df.columns):
        print(f"错误：文件缺少必要的列。需要 A, B, C 三列，但只找到了: {list(df.columns)}")
        exit()

    # --- 步骤 3: 提取每列唯一的 MAG 编号 ---
    # 使用集合(set)来自动去重，并使用 .dropna() 忽略空值
    print("正在提取并分析 MAG 编号...")
    set_a = set(df['A'].dropna().astype(str))
    set_b = set(df['B'].dropna().astype(str))
    set_c = set(df['C'].dropna().astype(str))

    # --- 步骤 4: 分析重合情况 ---

    # 4.1 计算两两之间的重合
    overlap_ab = set_a.intersection(set_b)
    overlap_ac = set_a.intersection(set_c)
    overlap_bc = set_b.intersection(set_c)

    # 4.2 计算三者之间的重合
    overlap_abc = set_a.intersection(set_b, set_c)

    # --- 步骤 5: 准备输出数据 ---

    # 5.1 准备“分析结果汇总”表格
    summary_data = {
        '分析项': [
            'A列 (唯一MAG数量)',
            'B列 (唯一MAG数量)',
            'C列 (唯一MAG数量)',
            'A 和 B 重合数量',
            'A 和 C 重合数量',
            'B 和 C 重合数量',
            'A, B, C 全部重合数量'
        ],
        '数量': [
            len(set_a),
            len(set_b),
            len(set_c),
            len(overlap_ab),
            len(overlap_ac),
            len(overlap_bc),
            len(overlap_abc)
        ],
        '重合的MAG编号': [
            '-',
            '-',
            '-',
            ', '.join(sorted(list(overlap_ab))) or '-',
            ', '.join(sorted(list(overlap_ac))) or '-',
            ', '.join(sorted(list(overlap_bc))) or '-',
            ', '.join(sorted(list(overlap_abc))) or '-'
        ]
    }
    summary_df = pd.DataFrame(summary_data)

    # 5.2 准备“Venn图数据”表格
    venn_data_dict = {
        'A': sorted(list(set_a)),
        'B': sorted(list(set_b)),
        'C': sorted(list(set_c))
    }
    # 创建一个能处理不同长度列表的DataFrame
    venn_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in venn_data_dict.items()]))


    # --- 步骤 6: 将结果写入一个新的 Excel 文件 ---
    print(f"正在将结果写入文件: {output_filename}")
    with pd.ExcelWriter(output_filename) as writer:
        summary_df.to_excel(writer, sheet_name='分析结果汇总', index=False)
        venn_df.to_excel(writer, sheet_name='Venn图数据', index=False)

    print("\n✓ 分析完成！")
    print(f"✓ 结果已成功导出到 Excel 文件: '{output_filename}'")
    print("\n文件包含两个工作表 (Sheets):")
    print("  1. '分析结果汇总': 详细的统计和重合MAG列表。")
    print("  2. 'Venn图数据': 可直接用于绘图软件的数据列表。")


except FileNotFoundError:
    print(f"错误：文件未找到！请检查您的文件路径是否正确: '{file_path}'")
except Exception as e:
    print(f"处理文件时发生了一个意料之外的错误: {e}")