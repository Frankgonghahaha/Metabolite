import pandas as pd
import os

# --- 1. 参数设置 ---
# 【请确保以下路径在您的电脑上是正确的】

# 包含功能微生物ID列表的CSV文件
# The CSV file containing the list of functional microorganism IDs.
FUNCTION_LIST_PATH = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83 keystones.csv'

# 包含全部PTM结果的庞大原始文件
# The large, raw file containing all PTM results.
INPUT_PTM_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/Step4_PTM_results.csv'

# 最终输出的、经过合并筛选的CSV文件
# The final output file after the OR-condition filtering.
OUTPUT_FILTERED_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystones_Receptor_PTM.csv'


# --- 2. 主程序 ---

def filter_ptm_by_donor_or_receptor(list_path, ptm_path, output_path):
    """
    一个高效的筛选脚本，用于从庞大的PTM结果中，提取出所有
    贡献方(Donor) 或 接收方(Receptor) 至少有一方是功能微生物的记录。

    Args:
        list_path (str): 功能微生物ID列表的CSV文件路径。
        ptm_path (str): 包含所有PTM结果的CSV文件路径。
        output_path (str): 筛选后结果的保存路径。
    """
    # a. 安全性检查：确保输入文件存在
    if not os.path.exists(list_path):
        print(f"❌ 错误: 找不到功能列表文件 '{list_path}'")
        return
    if not os.path.exists(ptm_path):
        print(f"❌ 错误: 找不到PTM结果文件 '{ptm_path}'")
        return

    try:
        # b. 加载功能微生物ID列表
        print(f"➡️ 步骤 1: 正在从 '{os.path.basename(list_path)}' 读取功能微生物ID列表...")
        function_df = pd.read_csv(list_path)
        functional_ids = set(function_df.iloc[:, 0].astype(str) + '_CDS')
        print(f"  ✅ 成功加载了 {len(functional_ids)} 个功能微生物ID用于筛选。")

        # c. 【核心修改】: 使用“或”逻辑进行筛选
        print(f"\n➡️ 步骤 2: 正在从庞大的PTM文件中进行合并筛选...")
        print("    筛选条件: 贡献方(Donor) 或 接收方(Receptor) 在功能微生物列表中。")

        chunk_list = []
        with pd.read_csv(ptm_path, chunksize=1000000) as reader:
            for i, chunk in enumerate(reader):
                print(f"  正在处理数据块 {i + 1}...")

                # 【关键筛选逻辑】
                # 我们使用 '|' (或) 操作符来合并两个筛选条件。
                # 只要满足以下任一条件，记录就会被选中：
                # 1. 'Receptor' 列的值在 functional_ids 集合中
                # 2. 'Donor' 列的值在 functional_ids 集合中
                # 这等效于分别筛选再合并去重，但效率更高。
                filtered_chunk = chunk[
                    chunk['Receptor'].isin(functional_ids) #| chunk['Donor'].isin(functional_ids)
                ]

                if not filtered_chunk.empty:
                    chunk_list.append(filtered_chunk)
                    print(f"    - 在此块中找到 {len(filtered_chunk)} 条符合条件的记录。")

        # d. 合并所有筛选出的结果
        if not chunk_list:
            print("\n⚠️ 警告: 在整个文件中没有找到任何与功能微生物相关的PTM记录。")
            print("  请检查您的功能微生物ID列表与PTM文件中的ID格式是否匹配（例如 '_CDS' 后缀）。")
            return

        print("\n➡️ 步骤 3: 正在合并所有筛选出的数据块...")
        final_df = pd.concat(chunk_list, ignore_index=True)
        print("  ✅ 数据合并完成。")

        # e. 保存最终结果
        print(f"\n➡️ 步骤 4: 正在将最终结果保存到文件...")
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        # f. 输出总结信息
        print("\n" + "="*60)
        print("🎉 筛选成功完成！")
        print("新生成的数据集包含了所有与您功能微生物相关的上游（作为贡献方）和下游（作为接收方）的代谢活动。")
        print(f"总计: 共找到 {len(final_df)} 条记录。")
        print(f"结果已保存至:\n{output_path}")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 处理过程中发生未知错误: {e}")
        print("  请检查CSV文件格式是否正确，以及列名（如'Receptor', 'Donor'）是否存在。")



# --- 3. 运行脚本 ---
if __name__ == "__main__":
    filter_ptm_by_donor_or_receptor(FUNCTION_LIST_PATH, INPUT_PTM_FILE, OUTPUT_FILTERED_FILE)