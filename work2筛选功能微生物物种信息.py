import os
import pandas as pd

# --- 1. 设置文件和文件夹路径 ---

# 包含功能微生物XML文件的文件夹
xml_folder_path = "/Volumes/CC/6042MAG数据库文件/20250704 分开降解和非降解/DBP降解菌/"

# 包含物种注释信息的Excel总表
taxonomy_excel_path = "/Volumes/CC/6042MAG数据库文件/信息表/物种信息_丰度信息.xlsx"

# 定义输出结果的新Excel文件名
output_excel_path = "/Volumes/CC/6042MAG数据库文件/信息表/DBP降解菌物种分布.xlsx"


# --- 2. 脚本核心逻辑 ---

def process_functional_microbes():
    """
    主函数，执行所有处理步骤。
    """
    try:
        # --- 步骤 1: 从文件名中提取所有功能的 MAG_id ---
        print(f"正在遍历文件夹: {xml_folder_path}")

        # os.listdir() 获取文件夹下所有文件名
        all_files = os.listdir(xml_folder_path)

        # 使用列表推导式高效提取ID
        # 我们假设文件名格式为 'MAG_id_CDS.xml'
        functional_mag_ids = [
            filename.removesuffix('_CDS.xml')
            for filename in all_files
            if filename.endswith('_CDS.xml')
        ]

        if not functional_mag_ids:
            print("错误：在指定文件夹中没有找到任何 '_CDS.xml' 文件。请检查路径。")
            return

        print(f"成功提取到 {len(functional_mag_ids)} 个功能微生物的MAG ID。")
        print("-" * 30)

        # --- 步骤 2: 读取物种信息总表 ---
        print(f"正在读取物种信息总表: {taxonomy_excel_path}")
        taxonomy_df = pd.read_excel(taxonomy_excel_path)
        print("总表读取成功。")
        print("-" * 30)

        # --- 步骤 3: 根据MAG_id列表筛选总表 ---
        print("正在根据MAG ID列表筛选物种信息...")
        # .isin() 是一个非常高效的筛选方法
        functional_tax_df = taxonomy_df[taxonomy_df['MAG_id'].isin(functional_mag_ids)].copy()

        if functional_tax_df.empty:
            print("警告：在物种信息总表中，没有找到任何与功能MAG ID匹配的条目。")
            return

        print(f"成功匹配到 {len(functional_tax_df)} 条物种信息。")
        print("-" * 30)

        # --- 步骤 4: 提取所需列并处理Phylum列 ---
        columns_to_extract = [
            'MAG_id',  # 同时保留MAG_id方便核对
            'Kingdom',
            'Phylum',
            'Class',
            'Order',
            'Family',
            'Genus',
            'Species'
        ]

        # 检查所需列是否存在
        missing_cols = [col for col in columns_to_extract if col not in functional_tax_df.columns]
        if missing_cols:
            print(f"错误：总表中缺少以下必需的列: {', '.join(missing_cols)}")
            return

        result_df = functional_tax_df[columns_to_extract].copy()

        # 使用 .str.removeprefix() 安全地移除Phylum列的前缀
        # .loc[:, 'Phylum'] 是推荐的赋值方式，可以避免警告
        result_df.loc[:, 'Phylum'] = result_df['Phylum'].str.removeprefix('p__')
        print("已提取所需列，并完成Phylum前缀去除。")
        print("-" * 30)

        # --- 步骤 5: 保存结果到新的Excel文件 ---
        result_df.to_excel(output_excel_path, index=False)
        print(f"处理完成！\n结果已成功保存到新文件中:\n{output_excel_path}")

    except FileNotFoundError as e:
        print(f"错误：文件未找到。请检查路径是否正确。\n详细信息: {e}")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


# --- 运行主函数 ---
if __name__ == "__main__":
    process_functional_microbes()