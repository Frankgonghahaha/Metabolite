import pandas as pd
import os

# --- 1. 参数设置 ---
# 【请将这里的路径修改为您电脑上的正确路径】

# 包含功能微生物ID列表的CSV文件
FUNCTION_LIST_PATH = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83 keystones.csv'

# 包含全部PTM结果的庞大原始文件
INPUT_PTM_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/Step4_PTM_results.csv'

# 最终输出的、仅按Receptor筛选的CSV文件
OUTPUT_FILTERED_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Final_Receptor_Filtered_List.csv'


# --- 2. 主程序 ---

def filter_by_receptor_only(list_path, ptm_path, output_path):
    """
    一个简单直接的筛选脚本，仅用于提取出所有
    接收方(Receptor)为功能微生物的记录。

    Args:
        list_path (str): 功能微生物ID列表的CSV文件路径。
        ptm_path (str): 包含所有PTM结果的CSV文件路径。
        output_path (str): 筛选后结果的保存路径。
    """
    # 检查输入文件是否存在
    if not os.path.exists(list_path):
        print(f"❌ 错误: 找不到功能列表文件 '{list_path}'")
        return
    if not os.path.exists(ptm_path):
        print(f"❌ 错误: 找不到PTM结果文件 '{ptm_path}'")
        return

    try:
        # 步骤 1: 加载功能微生物ID列表
        print(f"➡️ 步骤 1: 正在读取功能微生物ID...")
        function_df = pd.read_csv(list_path)
        functional_ids = set(function_df.iloc[:, 0].astype(str) + '_CDS')
        print(f"  ✅ 成功加载 {len(functional_ids)} 个功能ID。")

        # 步骤 2: 从大文件中分块筛选记录
        print(f"\n➡️ 步骤 2: 正在筛选Receptor为功能微生物的记录...")

        chunk_list = []
        with pd.read_csv(ptm_path, chunksize=1000000) as reader:
            for i, chunk in enumerate(reader):
                print(f"  - 正在处理数据块 {i + 1}...")

                # 【核心筛选逻辑】
                # 只保留 'Receptor' 列的值在 functional_ids 集合中的记录
                filtered_chunk = chunk[chunk['Receptor'].isin(functional_ids)]

                if not filtered_chunk.empty:
                    chunk_list.append(filtered_chunk)

        if not chunk_list:
            print("\n⚠️ 警告: 未找到任何由功能微生物接收的记录。脚本将退出。")
            return

        # 步骤 3: 合并结果
        print("\n➡️ 步骤 3: 正在合并筛选结果...")
        final_df = pd.concat(chunk_list, ignore_index=True)

        # 步骤 4: 保存到文件
        print(f"\n➡️ 步骤 4: 正在将结果保存至 '{os.path.basename(output_path)}'...")
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        # 完成
        print("\n" + "=" * 50)
        print("🎉 操作成功！")
        print(f"已成功筛选出 {len(final_df)} 条记录。")
        print(f"结果已保存至: {output_path}")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 处理过程中发生未知错误: {e}")


# --- 3. 运行脚本 ---
if __name__ == "__main__":
    filter_by_receptor_only(FUNCTION_LIST_PATH, INPUT_PTM_FILE, OUTPUT_FILTERED_FILE)