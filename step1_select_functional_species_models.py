import pandas as pd
import os


def select_functional_species_models():
    """
    遍历功能基因矩阵，筛选出具有特定功能的MAG，并匹配其物种分类信息，
    最终为每个功能基因生成一个包含对应MAGs及其分类信息的CSV文件。
    """
    # --- 1. 定义文件路径 ---
    # TODO: 请确保这些路径在您的系统中是正确的
    base_path = '/Volumes/CC/6042MAG数据库文件/信息表/'

    # 输入文件
    function_matrix_file = os.path.join(base_path, 'Important_DBP降解功能微生物矩阵_20250804.xlsx')
    taxonomy_file = os.path.join(base_path, '物种信息_丰度信息.xlsx')

    # 输出目录
    output_dir = base_path

    print("--- 开始执行脚本 ---")

    # --- 2. 读取数据文件 ---
    try:
        print("正在读取功能矩阵文件...")
        func_df = pd.read_excel(function_matrix_file)

        print("正在读取物种信息文件...")
        tax_df = pd.read_excel(taxonomy_file)
    except FileNotFoundError as e:
        print(f"[错误] 文件未找到: {e}")
        print("请检查文件路径是否正确。")
        return

    print("文件读取成功！\n")

    # --- 3. 核心处理流程 ---

    # 获取MAG ID列的列名 (通常是第一列)
    mag_id_col = func_df.columns[0]

    # 获取所有功能基因的列名 (从第二列开始)
    gene_columns = func_df.columns[1:]

    # 定义需要从物种信息表中提取的列
    taxonomy_columns_to_extract = [mag_id_col, 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

    # 遍历每一个功能基因
    for gene in gene_columns:
        print(f"--- 正在处理功能基因: {gene} ---")

        # 筛选出当前基因列中值为1的行
        functional_mags = func_df[func_df[gene] == 1]

        # 如果没有任何MAG具有该基因，则跳过
        if functional_mags.empty:
            print(f"基因 '{gene}' 没有找到任何对应的MAG，已跳过。")
            continue

        # 提取这些MAG的ID列表
        mag_ids_with_function = functional_mags[mag_id_col]

        # 使用这些MAG ID去物种信息表中进行匹配和筛选
        # .isin() 是高效的匹配方法
        filtered_taxonomy = tax_df[tax_df[mag_id_col].isin(mag_ids_with_function)]

        # 只保留需要的物种分类信息列
        final_table = filtered_taxonomy[taxonomy_columns_to_extract]

        # --- 4. 输出结果到文件 ---
        # 定义输出文件名，使用.csv格式更通用
        output_filename = f"{gene}.csv"
        output_filepath = os.path.join(output_dir, output_filename)

        try:
            # 将结果保存到CSV文件，使用 'utf-8-sig' 编码以确保在Excel中打开时中文无乱码
            final_table.to_csv(output_filepath, index=False, encoding='utf-8-sig')
            print(f"成功创建文件: {output_filepath}")
        except Exception as e:
            print(f"[错误] 无法写入文件 {output_filename}: {e}")

        print("-" * 25 + "\n")

    print("--- 脚本执行完毕 ---")


if __name__ == '__main__':
    select_functional_species_models()