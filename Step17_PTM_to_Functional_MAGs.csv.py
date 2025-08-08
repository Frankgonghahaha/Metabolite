import pandas as pd
import os

# --- 1. 参数设置 ---
# 【已更新】输入文件：您刚刚筛选出来的、聚焦于功能微生物的PTM精华数据。
# 脚本会假设这个文件与本脚本位于同一个文件夹下。
INPUT_PTM_FILE = 'Step17_PTM_to_Functional_MAGs.csv'

# 输出文件：脚本将会生成下面这两个新的、用于最终可视化的Gephi文件。
OUTPUT_NODES_FILE = 'gephi_nodes_functional.csv'
OUTPUT_EDGES_FILE = 'gephi_edges_functional.csv'


# --- 2. 主执行函数 ---

def format_for_gephi_with_colors(ptm_path):
    """
    读取筛选后的PTM结果，并将其转换为Gephi兼容的、包含精确颜色信息的节点和边列表。
    """
    if not os.path.exists(ptm_path):
        print(f"❌ 错误: 找不到输入文件 '{ptm_path}'")
        print("请确保您的PTM结果文件与本脚本放在同一个文件夹下。")
        return

    print(f"正在从 '{ptm_path}' 加载筛选后的PTM数据...")
    df = pd.read_csv(ptm_path)

    # --- a. 创建节点列表 (Nodes List) ---
    print("正在创建节点列表 (包含颜色)...")

    # 定义节点颜色
    mag_color = {'r': 120, 'g': 120, 'b': 120}  # 灰色
    metabolite_color = {'r': 220, 'g': 220, 'b': 200}  # 米色

    # 创建MAG节点
    mag_nodes = pd.unique(df[['Donor', 'Receptor']].values.ravel('K'))
    mag_df = pd.DataFrame({'Id': mag_nodes, 'Label': mag_nodes, 'Type': 'MAG'})
    mag_df['r'], mag_df['g'], mag_df['b'] = mag_color['r'], mag_color['g'], mag_color['b']

    # 创建Metabolite节点
    metabolite_nodes = df['PTM_ID'].unique()
    metabolite_df = pd.DataFrame({'Id': metabolite_nodes, 'Label': metabolite_nodes, 'Type': 'Metabolite'})
    metabolite_df['r'], metabolite_df['g'], metabolite_df['b'] = metabolite_color['r'], metabolite_color['g'], \
    metabolite_color['b']

    # 合并节点并保存
    nodes_final_df = pd.concat([mag_df, metabolite_df], ignore_index=True)
    nodes_final_df.to_csv(OUTPUT_NODES_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ 节点列表创建成功: {OUTPUT_NODES_FILE}")

    # --- b. 创建边列表 (Edges List) ---
    print("正在创建边列表 (包含颜色)...")

    # 定义边的颜色
    secretion_color_str = "0;116;217"  # 鲜明的蓝色
    uptake_color_str = "255;133;27"  # 鲜明的橙色

    # 创建 "Secretion" (分泌) 类型的边
    secretion_edges = df[['Donor', 'PTM_ID']].copy()
    secretion_edges.columns = ['Source', 'Target']
    secretion_edges['Type'] = 'Directed'
    secretion_edges['Label'] = 'Secretion'
    secretion_edges['Weight'] = 1.0
    secretion_edges['color'] = secretion_color_str

    # 创建 "Uptake" (吸收) 类型的边
    uptake_edges = df[['PTM_ID', 'Receptor']].copy()
    uptake_edges.columns = ['Source', 'Target']
    uptake_edges['Type'] = 'Directed'
    uptake_edges['Label'] = 'Uptake'
    uptake_edges['Weight'] = 1.0
    uptake_edges['color'] = uptake_color_str

    # 合并边并保存
    edges_final_df = pd.concat([secretion_edges, uptake_edges], ignore_index=True)
    edges_final_df.to_csv(OUTPUT_EDGES_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ 边列表创建成功: {OUTPUT_EDGES_FILE}")


# --- 3. 运行脚本 ---
if __name__ == "__main__":
    format_for_gephi_with_colors(INPUT_PTM_FILE)
    print("\n--- 数据准备完成！现在您可以在Gephi中导入这两个新文件了。 ---")