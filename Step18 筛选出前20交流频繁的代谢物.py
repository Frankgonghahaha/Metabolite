import pandas as pd
import os

# --- 1. 参数设置 ---
# 【请确保以下路径在您的电脑上是正确的】

# 输入文件：您已经筛选过一次的、包含名称的PTM结果文件
INPUT_PTM_FILE = '/Volumes/CC/6042MAG数据库文件/6042_PhyloMInt/Step17_PTM_to_Functional_MAGs.csv'

# 【新增】“代谢物排行榜”的输出路径
OUTPUT_METABOLITE_RANKING_FILE = '/Volumes/CC/6042MAG数据库文件/6042_PhyloMInt/Step17_Metabolite_Received_Ranking.csv'

# 最终二次筛选后的PTM列表的输出路径
OUTPUT_FINAL_FILTERED_PTM_FILE = '/Volumes/CC/6042MAG数据库文件/6042_PhyloMInt/Step17_PTM_Top10_metabolites.csv'

# 【关键可调参数】
# 您可以先运行一次，查看排行榜文件，然后再回来修改这个值以获得最佳结果
TOP_N_METABOLITES_RECEIVED = 10


# --- 2. 主程序 ---

def rank_and_filter(ptm_path, rank_output_path, final_output_path):
    """
    读取已注释的PTM数据，先生成频率排行榜，再根据排行榜进行二次筛选。
    """
    # a. 安全性检查
    if not os.path.exists(ptm_path):
        print(f"❌ 错误: 找不到输入文件 '{ptm_path}'")
        return

    try:
        # b. 加载已注释的PTM数据
        print(f"步骤1: 正在从 '{os.path.basename(ptm_path)}' 加载数据...")
        df = pd.read_csv(ptm_path)
        print(f"  ✅ 数据加载成功，共 {len(df)} 条记录。")

        # c. 【第二步】: 统计频率并生成排行榜
        print(f"\n步骤2: 正在统计代谢物接收频率并生成排行榜...")

        # 直接使用 groupby 统计每个 PTM_ID 和 PTM_Name 组合出现的次数
        metabolite_counts = df.groupby(['PTM_ID', 'PTM_Name']).size().reset_index(name='Received_Count')

        # 按接收次数降序排序
        metabolite_counts = metabolite_counts.sort_values(by='Received_Count', ascending=False)

        # 【新增】保存排行榜文件
        metabolite_counts.to_csv(rank_output_path, index=False, encoding='utf-8-sig')
        print(f"  ✅ 【新功能】代谢物接收频率排行榜已保存至:\n  {rank_output_path}")

        # d. 【第三步】: 根据排行榜进行最终筛选
        print(f"\n步骤3: 正在根据排行榜筛选 Top {TOP_N_METABOLITES_RECEIVED} 的代谢物...")

        # 获取排名前N的代谢物ID列表
        top_metabolites_list = metabolite_counts['PTM_ID'].head(TOP_N_METABOLITES_RECEIVED).tolist()

        # 使用 .isin() 方法从原始（已注释）的DataFrame中筛选出最终结果
        final_df = df[df['PTM_ID'].isin(top_metabolites_list)]

        # e. 保存最终结果
        print("\n步骤4: 正在保存最终筛选的PTM列表...")
        final_df.to_csv(final_output_path, index=False, encoding='utf-8-sig')

        print("\n" + "=" * 60)
        print("🎉 筛选成功！")
        print(f"最终精简后的PTM列表 (共 {len(final_df)} 条) 已保存至:\n{final_output_path}")
        print("您可以先查看排行榜文件，以决定是否需要调整 'TOP_N_METABOLITES_RECEIVED' 参数后重新运行。")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 处理过程中发生未知错误: {e}")


# --- 3. 运行脚本 ---
if __name__ == "__main__":
    rank_and_filter(INPUT_PTM_FILE, OUTPUT_METABOLITE_RANKING_FILE, OUTPUT_FINAL_FILTERED_PTM_FILE)