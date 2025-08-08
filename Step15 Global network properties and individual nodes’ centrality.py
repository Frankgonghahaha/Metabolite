# import pandas as pd
# import networkx as nx
# import numpy as np
# import os
#
# # --- 1. 设置：定义您的文件 ---
#
# # 输入文件：您在上一步中创建的邻接矩阵文件。
# # 脚本会假设这个文件与本脚本位于同一个文件夹下。
# INPUT_MATRIX_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step14_Construct_Network_Adjacent_Matrix.csv'
#
# # 输出文件：脚本将会生成下面这两个文件。
# OUTPUT_GLOBAL_PROPS_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step15_Global_Network_Properties.csv'
# OUTPUT_NODE_PROPS_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step15_Individual_Nodes_Properties.csv'
#
#
# # --- 2. 主分析函数 ---
#
# def analyze_network(matrix_path):
#     """
#     从邻接矩阵加载网络，并计算其全局和节点级别的属性。
#     """
#     if not os.path.exists(matrix_path):
#         print(f"❌ 错误: 找不到输入文件 '{matrix_path}'")
#         print("请确保您的矩阵文件与本脚本放在同一个文件夹下。")
#         return
#
#     print(f"正在从文件加载网络: {matrix_path}")
#     # 加载矩阵，并将第一列作为索引（行名）
#     adj_matrix = pd.read_csv(matrix_path, index_col=0)
#
#     # 从 pandas DataFrame 创建一个网络图对象
#     # 因为互补性是相互的，我们创建一个无向图（Graph）
#     G = nx.from_pandas_adjacency(adj_matrix, create_using=nx.Graph())
#
#
#     print(f"网络图创建成功，包含 {G.number_of_nodes()} 个节点和 {G.number_of_edges()} 条边。")
#
#     # --- A. 计算网络全局属性 ---
#     print("\n正在计算网络全局属性...")
#
#     global_properties = {}
#
#     # 基础属性
#     global_properties['总节点数 (Total nodes)'] = G.number_of_nodes()
#     global_properties['总连接数 (Total links)'] = G.number_of_edges()
#     global_properties['网络密度 (Density, D)'] = nx.density(G)
#     global_properties['连通性 (Connectedness, Con)'] = 1 if nx.is_connected(G) else 1 / nx.number_connected_components(
#         G)
#     global_properties['平均聚类系数 (Average clustering coefficient, avgCC)'] = nx.average_clustering(G)
#
#     # 基于度的属性
#     degrees = [d for n, d in G.degree()]
#     global_properties['平均度 (Average degree, avgK)'] = np.mean(degrees)
#     global_properties['最大度 (Maximal degree)'] = np.max(degrees)
#     # 找到拥有最大度的节点
#     max_degree_nodes = [n for n, d in G.degree() if d == global_properties['最大度 (Maximal degree)']]
#     global_properties['拥有最大度的节点 (Nodes with max degree)'] = '; '.join(max_degree_nodes)
#
#     # 传递性 (全局聚类系数)
#     global_properties['传递性 (Transitivity, Trans)'] = nx.transitivity(G)
#
#     # 将字典转换为 DataFrame 以便保存
#     global_df = pd.DataFrame([global_properties]).T
#     global_df.columns = ['数值']
#     global_df.index.name = '属性'
#
#     # --- B. 计算各节点的独立属性 ---
#     print("正在计算各节点的独立属性 (这可能需要一些时间)...")
#
#     # 节点度
#     node_degree = dict(G.degree())
#
#     # 节点介数中心性
#     node_betweenness = nx.betweenness_centrality(G)
#
#     # 节点特征向量中心性
#     # 增加了迭代次数以确保在复杂网络上也能收敛
#     try:
#         node_eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
#     except nx.PowerIterationFailedConvergence:
#         print("⚠️ 警告: 特征向量中心性计算未能收敛，结果可能为近似值。")
#         node_eigenvector = {n: np.nan for n in G.nodes()}
#
#     # 节点接近中心性
#     node_closeness = nx.closeness_centrality(G)
#
#     # 节点聚类系数
#     node_clustering = nx.clustering(G)
#
#     # 将所有节点属性合并到一个 DataFrame 中
#     node_df = pd.DataFrame({
#         '节点度 (Node degree)': node_degree,
#         '介数中心性 (Node betweenness)': node_betweenness,
#         '特征向量中心性 (Node eigenvector centrality)': node_eigenvector,
#         '接近中心性 (Node closeness)': node_closeness,
#         '聚类系数 (Clustering coefficient)': node_clustering,
#     })
#     node_df.index.name = '节点ID (Node_ID)'
#
#     # --- C. 保存结果 ---
#     global_df.to_csv(OUTPUT_GLOBAL_PROPS_FILE, encoding='utf-8-sig')
#     print(f"\n✅ 全局网络属性已保存至: {OUTPUT_GLOBAL_PROPS_FILE}")
#
#     node_df.to_csv(OUTPUT_NODE_PROPS_FILE, encoding='utf-8-sig')
#     print(f"✅ 各节点属性已保存至: {OUTPUT_NODE_PROPS_FILE}")
#
#
# # --- 3. 运行脚本 ---
#
# if __name__ == "__main__":
#     # 在运行前，检查必要的库是否已安装
#     try:
#         import networkx
#         import pandas
#         import numpy
#     except ImportError:
#         print("=" * 60)
#         print("⚠️  重要提示: 必需的库未找到。")
#         print("请先在您的终端中运行以下命令来安装它们:")
#         print("pip install pandas networkx")
#         print("=" * 60)
#         exit()
#
#     analyze_network(INPUT_MATRIX_FILE)
#     print("\n--- 所有计算已完成！ ---")
# # import pandas as pd
# # import networkx as nx
# # import numpy as np
# # import os
# #
# # # --- 1. 设置：定义您的文件 ---
# #
# # # 输入文件：您在上一步中创建的邻接矩阵文件。
# # # 脚本会假设这个文件与本脚本位于同一个文件夹下。
# # INPUT_MATRIX_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step14_Construct_Network_Adjacent_Matrix.csv'
# #
# # # 输出文件：脚本将会生成下面这两个文件。
# # OUTPUT_GLOBAL_PROPS_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Directed_Step15_Global_Network_Properties.csv'
# # OUTPUT_NODE_PROPS_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Directed_Step15_Individual_Nodes_Properties.csv'
# #
# #
# # # --- 2. 主分析函数 ---
# #
# # def analyze_network_directed(matrix_path):
# #     """
# #     从邻接矩阵加载有向网络，并计算其全局和节点级别的属性。
# #     """
# #     if not os.path.exists(matrix_path):
# #         print(f"❌ 错误: 找不到输入文件 '{matrix_path}'")
# #         print("请确保您的矩阵文件与本脚本放在同一个文件夹下。")
# #         return
# #
# #     print(f"正在从文件加载网络: {matrix_path}")
# #     # 加载矩阵，并将第一列作为索引（行名）
# #     adj_matrix = pd.read_csv(matrix_path, index_col=0)
# #
# #     # ---【核心修改】---
# #     # 关系通常具有方向性（如A→B不等于B→A），因此我们创建一个有向图（DiGraph）
# #     G = nx.from_pandas_adjacency(adj_matrix, create_using=nx.DiGraph())
# #
# #     # G.number_of_edges() 现在应该等于邻接矩阵中非零元素的数量
# #     print(f"有向网络图创建成功，包含 {G.number_of_nodes()} 个节点和 {G.number_of_edges()} 条边。")
# #
# #     # --- A. 计算网络全局属性 ---
# #     print("\n正在计算网络全局属性...")
# #
# #     global_properties = {}
# #
# #     # 基础属性
# #     global_properties['总节点数 (Total nodes)'] = G.number_of_nodes()
# #     global_properties['总连接数 (Total links/edges)'] = G.number_of_edges()
# #     global_properties['网络密度 (Density, D)'] = nx.density(G)
# #
# #     # 【修改】连通性：针对有向图计算
# #     # 弱连通：忽略方向时，网络是否是连通的
# #     global_properties['是否弱连通 (Is weakly connected)'] = nx.is_weakly_connected(G)
# #     global_properties['弱连通分量数 (Number of weakly connected components)'] = nx.number_weakly_connected_components(G)
# #     # 强连通：任意两个节点间是否可以互相到达
# #     global_properties['是否强连通 (Is strongly connected)'] = nx.is_strongly_connected(G)
# #     global_properties[
# #         '强连通分量数 (Number of strongly connected components)'] = nx.number_strongly_connected_components(G)
# #
# #     global_properties['平均聚类系数 (Average clustering coefficient, avgCC)'] = nx.average_clustering(G)
# #
# #     # 【修改】基于度的属性：区分入度和出度
# #     in_degrees = [d for n, d in G.in_degree()]
# #     out_degrees = [d for n, d in G.out_degree()]
# #     total_degrees = [d for n, d in G.degree()]
# #
# #     global_properties['平均入度 (Average in-degree)'] = np.mean(in_degrees)
# #     global_properties['平均出度 (Average out-degree)'] = np.mean(out_degrees)
# #     global_properties['平均总度 (Average total degree)'] = np.mean(total_degrees)
# #     global_properties['最大总度 (Maximal total degree)'] = np.max(total_degrees)
# #     # 找到拥有最大总度的节点
# #     max_degree_nodes = [n for n, d in G.degree() if d == global_properties['最大总度 (Maximal total degree)']]
# #     global_properties['拥有最大总度的节点 (Nodes with max total degree)'] = '; '.join(max_degree_nodes)
# #
# #     # 传递性 (全局聚类系数)
# #     global_properties['传递性 (Transitivity, Trans)'] = nx.transitivity(G)
# #
# #     # 将字典转换为 DataFrame 以便保存
# #     global_df = pd.DataFrame([global_properties]).T
# #     global_df.columns = ['数值']
# #     global_df.index.name = '属性'
# #
# #     # --- B. 计算各节点的独立属性 ---
# #     print("正在计算各节点的独立属性 (这可能需要一些时间)...")
# #
# #     # 【修改】节点度：分别计算入度、出度和总度
# #     node_in_degree = dict(G.in_degree())
# #     node_out_degree = dict(G.out_degree())
# #     node_total_degree = dict(G.degree())
# #
# #     # 节点介数中心性 (在有向图上计算)
# #     node_betweenness = nx.betweenness_centrality(G)
# #
# #     # 节点特征向量中心性 (在有向图上计算)
# #     try:
# #         # 注意：对于有向图，特征向量中心性通常使用左特征向量（in-degree based）或右特征向量（out-degree based）
# #         # networkx 默认计算的是 "in-degree" a "right eigenvector"
# #         node_eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
# #     except nx.PowerIterationFailedConvergence:
# #         print("⚠️ 警告: 特征向量中心性计算未能收敛，结果可能为近似值。")
# #         node_eigenvector = {n: np.nan for n in G.nodes()}
# #
# #     # 节点接近中心性 (在有向图上计算)
# #     node_closeness = nx.closeness_centrality(G)
# #
# #     # 节点聚类系数 (在有向图上计算)
# #     node_clustering = nx.clustering(G)
# #
# #     # 将所有节点属性合并到一个 DataFrame 中
# #     node_df = pd.DataFrame({
# #         '入度 (In-degree)': node_in_degree,
# #         '出度 (Out-degree)': node_out_degree,
# #         '总度 (Total degree)': node_total_degree,
# #         '介数中心性 (Betweenness centrality)': node_betweenness,
# #         '特征向量中心性 (Eigenvector centrality)': node_eigenvector,
# #         '接近中心性 (Closeness centrality)': node_closeness,
# #         '聚类系数 (Clustering coefficient)': node_clustering,
# #     })
# #     node_df.index.name = '节点ID (Node_ID)'
# #
# #     # --- C. 保存结果 ---
# #     global_df.to_csv(OUTPUT_GLOBAL_PROPS_FILE, encoding='utf-8-sig')
# #     print(f"\n✅ 全局网络属性已保存至: {OUTPUT_GLOBAL_PROPS_FILE}")
# #
# #     node_df.to_csv(OUTPUT_NODE_PROPS_FILE, encoding='utf-8-sig')
# #     print(f"✅ 各节点属性已保存至: {OUTPUT_NODE_PROPS_FILE}")
# #
# #
# # # --- 3. 运行脚本 ---
# #
# # if __name__ == "__main__":
# #     # 在运行前，检查必要的库是否已安装
# #     try:
# #         import networkx
# #         import pandas
# #         import numpy
# #     except ImportError:
# #         print("=" * 60)
# #         print("⚠️  重要提示: 必需的库未找到。")
# #         print("请先在您的终端中运行以下命令来安装它们:")
# #         print("pip install pandas networkx")
# #         print("=" * 60)
# #         exit()
# #
# #     analyze_network_directed(INPUT_MATRIX_FILE)
# #     print("\n--- 所有计算已完成！ ---")
import pandas as pd
import networkx as nx
import numpy as np
import os

# --- 1. 设置：定义您的文件 ---

# 输入文件：您在上一步中创建的邻接矩阵文件。
INPUT_MATRIX_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step14_Construct_Network_Adjacent_Matrix_NoSelfLoops.csv'

# 输出文件：脚本将会生成下面这三个文件。
OUTPUT_GLOBAL_PROPS_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/3Step15_Global_Network_Properties.csv'
OUTPUT_NODE_PROPS_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/3Step15_Individual_Nodes_Properties.csv'
# 【新增】定义边列表输出文件名
OUTPUT_EDGELIST_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/3Step15_Edge_List.csv'


# --- 2. 主分析函数 ---

def analyze_network(matrix_path):
    """
    从邻接矩阵加载网络，计算其属性，并导出边列表。
    """
    if not os.path.exists(matrix_path):
        print(f"❌ 错误: 找不到输入文件 '{matrix_path}'")
        print("请确保您的矩阵文件与本脚本放在同一个文件夹下。")
        return

    print(f"正在从文件加载网络: {matrix_path}")
    # 加载矩阵，并将第一列作为索引（行名）
    adj_matrix = pd.read_csv(matrix_path, index_col=0)

    # 从 pandas DataFrame 创建一个网络图对象
    # 因为互补性是相互的，我们创建一个无向图（Graph）
    G = nx.from_pandas_adjacency(adj_matrix, create_using=nx.Graph())

    print(f"网络图创建成功，包含 {G.number_of_nodes()} 个节点和 {G.number_of_edges()} 条边。")

    # --- A. 计算网络全局属性 ---
    print("\n正在计算网络全局属性...")

    global_properties = {}
    global_properties['总节点数 (Total nodes)'] = G.number_of_nodes()
    global_properties['总连接数 (Total links)'] = G.number_of_edges()
    global_properties['网络密度 (Density, D)'] = nx.density(G)
    global_properties['连通性 (Connectedness, Con)'] = 1 if nx.is_connected(G) else 1 / nx.number_connected_components(
        G)
    global_properties['平均聚类系数 (Average clustering coefficient, avgCC)'] = nx.average_clustering(G)
    degrees = [d for n, d in G.degree()]
    global_properties['平均度 (Average degree, avgK)'] = np.mean(degrees)
    global_properties['最大度 (Maximal degree)'] = np.max(degrees)
    max_degree_nodes = [n for n, d in G.degree() if d == global_properties['最大度 (Maximal degree)']]
    global_properties['拥有最大度的节点 (Nodes with max degree)'] = '; '.join(max_degree_nodes)
    global_properties['传递性 (Transitivity, Trans)'] = nx.transitivity(G)
    global_df = pd.DataFrame([global_properties]).T
    global_df.columns = ['数值']
    global_df.index.name = '属性'

    # --- B. 计算各节点的独立属性 ---
    print("正在计算各节点的独立属性 (这可能需要一些时间)...")

    node_degree = dict(G.degree())
    node_betweenness = nx.betweenness_centrality(G)
    try:
        node_eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        print("⚠️ 警告: 特征向量中心性计算未能收敛，结果可能为近似值。")
        node_eigenvector = {n: np.nan for n in G.nodes()}
    node_closeness = nx.closeness_centrality(G)
    node_clustering = nx.clustering(G)
    node_df = pd.DataFrame({
        '节点度 (Node degree)': node_degree,
        '介数中心性 (Node betweenness)': node_betweenness,
        '特征向量中心性 (Node eigenvector centrality)': node_eigenvector,
        '接近中心性 (Node closeness)': node_closeness,
        '聚类系数 (Clustering coefficient)': node_clustering,
    })
    node_df.index.name = '节点ID (Node_ID)'

    # --- C. 保存结果 ---
    global_df.to_csv(OUTPUT_GLOBAL_PROPS_FILE, encoding='utf-8-sig')
    print(f"\n✅ 全局网络属性已保存至: {OUTPUT_GLOBAL_PROPS_FILE}")

    node_df.to_csv(OUTPUT_NODE_PROPS_FILE, encoding='utf-8-sig')
    print(f"✅ 各节点属性已保存至: {OUTPUT_NODE_PROPS_FILE}")

    # --- 新增 D. 保存所有连接（边列表） ---
    print("\n正在导出网络中的所有具体连接...")

    # 从图中获取所有边的列表
    edge_list = list(G.edges())

    # 将边列表转换为DataFrame
    # 因为是无向图，所以两列称为 'Node_1' 和 'Node_2' 更为准确
    edge_df = pd.DataFrame(edge_list, columns=['Node_1', 'Node_2'])

    # 保存到CSV文件
    edge_df.to_csv(OUTPUT_EDGELIST_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ 所有连接（边列表）已保存至: {OUTPUT_EDGELIST_FILE}")


# --- 3. 运行脚本 ---

if __name__ == "__main__":
    # 在运行前，检查必要的库是否已安装
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

    analyze_network(INPUT_MATRIX_FILE)
    print("\n--- 所有计算已完成！ ---")