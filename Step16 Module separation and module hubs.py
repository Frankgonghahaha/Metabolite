import pandas as pd
import networkx as nx
import numpy as np
import os

# --- 1. 设置：定义您的文件和参数 ---

# 输入文件：您在上一步中创建的邻接矩阵文件。
# 脚本会假设这个文件与本脚本位于同一个文件夹下。
INPUT_MATRIX_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step14_Construct_Network_Adjacent_Matrix_NoSelfLoops.csv'

# 输出文件：脚本将会生成这个包含模块和节点角色信息的文件。
OUTPUT_NODE_ROLES_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/3Step16_Module_and_Node_Roles.csv'

# Z-P图的角色划分阈值 (根据您的描述设定)
Z_THRESHOLD = 2.5
P_THRESHOLD = 0.62


# --- 2. 主分析函数 ---

def analyze_modules_and_roles(matrix_path):
    """
    加载网络，执行模块划分，并计算每个节点的zi和pi值以确定其网络角色。
    """
    if not os.path.exists(matrix_path):
        print(f"❌ 错误: 找不到输入文件 '{matrix_path}'")
        print("请确保您的矩阵文件与本脚本放在同一个文件夹下。")
        return

    print(f"正在从文件加载网络: {matrix_path}")
    adj_matrix = pd.read_csv(matrix_path, index_col=0)
    G = nx.from_pandas_adjacency(adj_matrix, create_using=nx.Graph())
    # 我们需要边的权重（互补值）来计算zi和pi
    G_weighted = nx.from_pandas_adjacency(adj_matrix, create_using=nx.Graph())

    # 移除权重为0的边，以防它们影响计算
    edges_to_remove = [(u, v) for u, v, d in G_weighted.edges(data=True) if d['weight'] == 0]
    G_weighted.remove_edges_from(edges_to_remove)

    print(f"网络图创建成功，包含 {G_weighted.number_of_nodes()} 个节点和 {G_weighted.number_of_edges()} 条有效连接。")

    # --- A. 模块划分 ---
    print("\n步骤1: 正在使用贪心算法进行模块划分...")

    # 使用Greedy Modularity Optimization方法找到最佳的社群划分
    # networkx > 2.4 版本推荐使用 nx.community.greedy_modularity_communities
    communities_generator = nx.community.greedy_modularity_communities(G_weighted, weight='weight')

    # 将结果转换为节点到模块ID的字典
    #  {node: module_id, ...}
    partition = {node: i for i, comm in enumerate(communities_generator) for node in comm}

    print(f"模块划分完成，共找到 {len(set(partition.values()))} 个模块。")

    # --- B. 计算 Z-P 值 ---
    print("步骤2: 正在计算每个节点的zi和pi值...")

    zi_pi_values = {}

    # 计算每个模块内部的度数均值和标准差，用于后续zi计算
    module_degrees = {}
    for module_id in set(partition.values()):
        nodes_in_module = [n for n, m_id in partition.items() if m_id == module_id]
        subgraph = G_weighted.subgraph(nodes_in_module)
        degrees_in_module = [d for n, d in subgraph.degree(weight='weight')]
        module_degrees[module_id] = {
            'mean': np.mean(degrees_in_module) if degrees_in_module else 0,
            'std': np.std(degrees_in_module) if degrees_in_module else 0
        }

    for node in G_weighted.nodes():
        module_id = partition[node]

        # 计算 Ki (模块内度数): 该节点到同一模块内其他节点的连接权重之和
        ki = sum(G_weighted[node][neighbor]['weight'] for neighbor in G_weighted.neighbors(node) if
                 partition[neighbor] == module_id)

        # 计算 zi (模块内标准化度)
        mean_k = module_degrees[module_id]['mean']
        std_k = module_degrees[module_id]['std']
        zi = (ki - mean_k) / std_k if std_k > 0 else 0

        # 计算 Pi (模块间参与系数)
        total_degree = G_weighted.degree(node, weight='weight')
        pi = 1 - (ki / total_degree) ** 2 if total_degree > 0 else 0

        zi_pi_values[node] = {'zi': zi, 'pi': pi}

    # --- C. 分配节点角色 ---
    print("步骤3: 正在根据Z-P阈值为节点分配角色...")

    def assign_role(row):
        if row['zi'] >= Z_THRESHOLD and row['pi'] >= P_THRESHOLD:
            return '网络核心 (Network hub)'
        elif row['zi'] >= Z_THRESHOLD and row['pi'] < P_THRESHOLD:
            return '模块核心 (Module hub)'
        elif row['zi'] < Z_THRESHOLD and row['pi'] >= P_THRESHOLD:
            return '连接者 (Connector)'
        else:
            return '外围设备 (Peripheral)'

    # --- D. 整合并保存结果 ---
    # 创建最终的DataFrame
    results_df = pd.DataFrame.from_dict(zi_pi_values, orient='index')
    results_df['Module_ID'] = results_df.index.map(partition)
    results_df['Role'] = results_df.apply(assign_role, axis=1)

    # 调整列顺序，使其更易读
    results_df = results_df[['Module_ID', 'zi', 'pi', 'Role']]
    results_df.index.name = 'Node_ID'

    # 保存到CSV文件
    results_df.to_csv(OUTPUT_NODE_ROLES_FILE, encoding='utf-8-sig')
    print(f"\n✅ 分析完成！详细的节点角色信息已保存至: {OUTPUT_NODE_ROLES_FILE}")


# --- 3. 运行脚本 ---

if __name__ == "__main__":
    # 检查依赖库
    try:
        import networkx
        import pandas
        import numpy
    except ImportError:
        print("=" * 60)
        print("⚠️  重要提示: 必需的库未找到。")
        print("请先在您的终端中运行以下命令来安装它们:")
        print("pip install pandas networkx")
        print("=" * 60)
        exit()

    analyze_modules_and_roles(INPUT_MATRIX_FILE)
    print("\n--- 所有计算已完成！ ---")