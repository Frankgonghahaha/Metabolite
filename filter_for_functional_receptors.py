import pandas as pd
import os

# --- 1. 参数设置 ---
# 【请确保以下路径在您的电脑上是正确的】

# 包含功能微生物ID列表的CSV文件
FUNCTION_LIST_PATH = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83 keystones.csv'

# 包含全部PTM结果的庞大文件
INPUT_PTM_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/Step4_PTM_results.csv'

# 最终输出的、经过双重筛选的CSV文件
OUTPUT_FILTERED_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystone_PTM.csv'

# 【关键可调参数】
# 您想重点关注的最常被接收的代谢物的数量。
# 这是一个非常重要的参数，决定了最终图表的复杂度。建议从100-200开始尝试。
TOP_N_METABOLITES_RECEIVED = 100


# --- 2. 主程序 ---

def filter_for_receptors(list_path, ptm_path, output_path):
    """
    一个多层筛选脚本，专门用于找出功能微生物接收的最重要代谢物。
    """
    # a. 安全性检查
    if not os.path.exists(list_path):
        print(f"❌ 错误: 找不到功能列表文件 '{list_path}'")
        return
    if not os.path.exists(ptm_path):
        print(f"❌ 错误: 找不到PTM结果文件 '{ptm_path}'")
        return

    try:
        # b. 加载功能ID列表
        print(f"正在从 '{os.path.basename(list_path)}' 读取功能ID列表...")
        function_df = pd.read_csv(list_path)
        # 假设ID在第一列，且主数据表中的ID带有 "_CDS" 后缀
        functional_ids = set(function_df.iloc[:, 0].astype(str) + '_CDS')
        print(f"  ✅ 加载了 {len(functional_ids)} 个功能ID用于筛选。")

        # c. 【第一层筛选】: 按功能微生物作为“受体”进行筛选
        print(f"\n步骤1: 正在从庞大的PTM文件中筛选出功能微生物作为受体的记录...")

        # 为了处理超大文件，我们使用分块读取 (chunking) 的方法，避免内存耗尽
        chunk_list = []
        with pd.read_csv(ptm_path, chunksize=1000000) as reader:  # 每次读取一百万行
            for i, chunk in enumerate(reader):
                print(f"  正在处理数据块 {i + 1}...")
                # 在每个小数据块中执行筛选
                filtered_chunk = chunk[chunk['Receptor'].isin(functional_ids)]
                chunk_list.append(filtered_chunk)

        # 合并所有筛选出的结果
        df_to_functional = pd.concat(chunk_list, ignore_index=True)

        if df_to_functional.empty:
            print("⚠️ 警告: 没有找到任何由功能微生物接收的PTM记录。脚本将提前退出。")
            return

        print(f"  ✅ 第一层筛选完成，共找到 {len(df_to_functional)} 条相关记录。")

        # d. 【第二层筛选】: 找出最重要的代谢物
        print(f"\n步骤2: 正在统计并筛选出被功能微生物接收得最频繁的 Top {TOP_N_METABOLITES_RECEIVED} 种代谢物...")

        # 对第一步的结果进行统计
        top_metabolite_counts = df_to_functional['PTM_ID'].value_counts()

        # 获取排名前N的代谢物ID列表
        top_metabolites_list = top_metabolite_counts.head(TOP_N_METABOLITES_RECEIVED).index.tolist()

        print(f"  ✅ 明星代谢物列表已确定。")

        # e. 【最终精简】: 使用明星代谢物列表进行最后筛选
        print("\n步骤3: 正在根据明星代谢物列表精简数据...")
        final_df = df_to_functional[df_to_functional['PTM_ID'].isin(top_metabolites_list)]

        # f. 保存最终结果
        print("\n步骤4: 正在保存最终筛选结果...")
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print("\n" + "=" * 60)
        print("🎉 筛选成功！")
        print("最终生成的数据集是您原始数据的精华，完美聚焦于您的研究问题。")
        print(f"共包含 {len(final_df)} 条记录，涉及 {len(final_df['PTM_ID'].unique())} 种核心代谢物。")
        print(f"结果已保存至:\n{output_path}")
        print("现在，您可以用这个精简后的文件去进行可视化了！")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 处理过程中发生未知错误: {e}")


# --- 3. 运行脚本 ---
if __name__ == "__main__":
    filter_for_receptors(FUNCTION_LIST_PATH, INPUT_PTM_FILE, OUTPUT_FILTERED_FILE)