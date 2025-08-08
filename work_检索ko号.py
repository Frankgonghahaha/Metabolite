import os
import glob
import pandas as pd
from collections import defaultdict

# --- 1. 用户配置区 ---

# 输入目录：存放所有MAG注释CSV文件的文件夹
CSV_DIR = '/Volumes/CC/6042MAG数据库文件/全部注释文件_csv格式'

# 您想要检索的目标KO ID列表
TARGET_KOS = ['K18067','K04102']  # 这是一个例子，请替换成您自己的列表

# (第1处修改) 输出目录：将用于存放所有生成的KO结果文件
OUTPUT_DIR = '/Volumes/CC/6042MAG数据库文件/信息表'


# --- 2. 脚本执行区 ---

def find_kos_in_mag_annotations(csv_dir, target_kos, output_dir):
    """
    在指定目录的所MAG注释CSV文件中，检索目标KO，并为每个找到的KO生成独立的CSV结果文件。
    """
    print("--- 开始检索目标KO ---")
    print(f"目标KO列表: {target_kos}")
    print(f"扫描目录: {csv_dir}")

    # 检查输入目录是否存在
    if not os.path.isdir(csv_dir):
        print(f"错误: 输入目录不存在, 请检查路径 '{csv_dir}'")
        return

    # (第2处修改) 自动创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"结果将保存在: {output_dir}")

    # 使用defaultdict收集结果，key是KO，value是包含该KO的MAG列表
    found_results = defaultdict(list)

    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    if not csv_files:
        print(f"警告: 在目录 '{csv_dir}' 中没有找到任何 .csv 文件。")
        return

    target_kos_set = set(target_kos)

    # 遍历每一个CSV文件 (这部分逻辑不变)
    for file_path in csv_files:
        mag_id = os.path.basename(file_path).replace('.csv', '')
        try:
            df = pd.read_csv(file_path, usecols=['KEGG_ko'], na_filter=True)
            mag_kos = df['KEGG_ko'].dropna().astype(str).str.replace('ko:', '', regex=False).unique()
            mag_kos_set = set(mag_kos)
            found_in_this_file = target_kos_set.intersection(mag_kos_set)

            if found_in_this_file:
                print(f"  在 {mag_id} 中找到目标: {', '.join(found_in_this_file)}")
                for ko in found_in_this_file:
                    found_results[ko].append(mag_id)
        except (ValueError, KeyError):
            print(f"  -> 跳过文件 (可能为空或无KEGG_ko列): {os.path.basename(file_path)}")
            continue
        except Exception as e:
            print(f"  ! 处理文件 {os.path.basename(file_path)} 时发生未知错误: {e}")
            continue

    # --- (第3处修改) 汇总并为每个KO独立保存结果 ---
    if not found_results:
        print("\n--- 操作完成。在所有文件中均未找到指定的目标KO。 ---")
        return

    print("\n--- 检索完成，正在为每个找到的KO生成独立的CSV文件 ---")

    # 遍历收集到的结果字典
    for ko_id, mag_list in found_results.items():
        # 构建输出文件名，例如 K03928.csv
        output_filename = f"{ko_id}.csv"
        output_path = os.path.join(output_dir, output_filename)

        # 将MAG列表转换为一个单列的DataFrame，并排序
        mags_df = pd.DataFrame(sorted(mag_list), columns=['MAG_ID'])

        # 保存为CSV文件，不包含索引列
        mags_df.to_csv(output_path, index=False)

        print(f"  -> 已生成文件: {output_path} (包含 {len(mag_list)} 个MAG)")

    print("\n--- 所有文件处理完成 ---")


# --- 运行主函数 ---
if __name__ == "__main__":
    find_kos_in_mag_annotations(CSV_DIR, TARGET_KOS, OUTPUT_DIR)