import os
import glob
import pandas as pd

# --- 1. 用户配置区 ---
# 我已经根据您的要求更新了这里的路径

# (第1处修改) 输入路径：存放 .emapper.annotations 文件的目录
ANNOTATION_DIR = '/Volumes/CC/6042MAG数据库文件/全部注释文件原格式'

# (第2处修改) 输出路径：存放生成的 .csv 文件的目录
OUTPUT_DIR = '/Volumes/CC/6042MAG数据库文件/全部注释文件_csv格式'

# --- 2. 脚本执行区 ---

print("--- 开始将注释文件逐个转换为CSV ---")
print(f"输入目录: {ANNOTATION_DIR}")
print(f"输出目录: {OUTPUT_DIR}")

# (第3处修改) 自动创建输出目录（如果它不存在）
# os.makedirs() 可以创建多层目录，exist_ok=True 表示如果目录已存在则不报错
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 获取所有 .emapper.annotations 文件
annotation_files = glob.glob(os.path.join(ANNOTATION_DIR, "*.emapper.annotations"))

# 检查是否找到了文件
if not annotation_files:
    print(f"警告: 在目录 '{ANNOTATION_DIR}' 中没有找到任何 '.emapper.annotations' 文件。")
    print("请检查 ANNOTATION_DIR 路径是否正确。")
    exit()

# 循环处理每一个找到的注释文件
for file_path in annotation_files:
    # 从完整路径中获取不带后缀的文件名
    base_name = os.path.basename(file_path).split('.emapper.annotations')[0]

    # (第4处修改) 构建输出文件的完整路径，使其指向新的OUTPUT_DIR
    output_csv_path = os.path.join(OUTPUT_DIR, f"{base_name}.csv")

    print(f"正在处理: {os.path.basename(file_path)}")

    try:
        # --- 文件读取和处理逻辑 (保持不变) ---
        df = pd.read_csv(file_path, sep='\t', skiprows=4, header=0, low_memory=False)

        if '#query' in df.columns:
            df.rename(columns={'#query': 'Query'}, inplace=True)

        columns_to_extract = [
            'Query', 'evalue', 'score', 'eggNOG_OGs', 'max_annot_lvl', 'COG_category',
            'Description', 'Preferred_name', 'GOs', 'EC', 'KEGG_ko', 'KEGG_Pathway',
            'KEGG_Module', 'KEGG_Reaction', 'KEGG_rclass', 'BRITE', 'KEGG_TC',
            'CAZy', 'BiGG_Reaction', 'PFAMs'
        ]

        existing_cols = [col for col in columns_to_extract if col in df.columns]
        df_extracted = df[existing_cols].copy()

        if 'KEGG_ko' in df_extracted.columns:
            df_extracted.loc[:, 'KEGG_ko'] = df_extracted['KEGG_ko'].fillna('')
            df_extracted = df_extracted.assign(KEGG_ko=df_extracted['KEGG_ko'].str.split(',')).explode('KEGG_ko')
            df_extracted.loc[:, 'KEGG_ko'] = df_extracted['KEGG_ko'].str.strip()
            df_extracted = df_extracted[df_extracted['KEGG_ko'] != '']

        # --- 保存到新的输出路径 ---
        df_extracted.to_csv(output_csv_path, index=False)

        print(f"  -> 已成功生成: {output_csv_path}")

    except Exception as e:
        print(f"  -> 处理文件 {os.path.basename(file_path)} 时发生错误: {e}")
        continue

print("\n--- 所有文件处理完成 ---")