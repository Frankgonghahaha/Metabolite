import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. 参数设置 ---
# 【请确保以下路径在您的电脑上是正确的】

# 输入文件：您在上一步中生成的PTM结果文件。
# 脚本会假设这个文件与本脚本位于同一个文件夹下。
INPUT_PTM_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step4_PTM_results_final_v2.csv'

# 输出文件：最终生成的交互式HTML图表。
OUTPUT_HTML_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step17_PTM_Chord_Diagram.html'

# 【重要可调参数】
# 为了让图表清晰，我们只展示PTM数量排名前N的连接。
# 您可以调整这个数字，数字越大，图中的连接越多。建议从50-100开始尝试。
TOP_N_CONNECTIONS = 100


# --- 2. 主执行函数 ---

def create_chord_diagram(ptm_path):
    """
    读取PTM结果，处理数据，并生成一个交互式的弦图HTML文件。
    """
    if not os.path.exists(ptm_path):
        print(f"❌ 错误: 找不到输入文件 '{ptm_path}'")
        print("请确保您的PTM结果文件与本脚本放在同一个文件夹下。")
        return

    print(f"正在从 '{ptm_path}' 加载PTM数据...")
    df = pd.read_csv(ptm_path)

    # --- a. 数据聚合 ---
    # 按 (Donor, Receptor) 分组，并计算每对之间的PTM数量
    ptm_counts = df.groupby(['Donor', 'Receptor']).size().reset_index(name='PTM_Count')
    print(f"共找到 {len(ptm_counts)} 对独特的转移关系。")

    # 按PTM数量降序排序，并筛选出前N个最强的连接
    top_connections = ptm_counts.sort_values(by='PTM_Count', ascending=False).head(TOP_N_CONNECTIONS)
    print(f"已筛选出PTM数量排名前 {TOP_N_CONNECTIONS} 的连接进行可视化。")

    if top_connections.empty:
        print("❌ 错误: 未找到任何PTM连接，无法生成图表。")
        return

    # --- b. 准备绘图所需的数据格式 ---
    # 找出所有涉及到的唯一模型ID
    all_nodes = pd.concat([top_connections['Donor'], top_connections['Receptor']]).unique()

    # 创建一个从模型ID到数字索引的映射
    node_map = {node: i for i, node in enumerate(all_nodes)}

    # 创建Plotly需要的'source', 'target', 和 'value'列表
    source = top_connections['Donor'].map(node_map)
    target = top_connections['Receptor'].map(node_map)
    value = top_connections['PTM_Count']

    # 为每个连接创建标签，用于鼠标悬停时显示
    link_labels = [f"{donor} → {receptor}: {count} PTMs"
                   for donor, receptor, count in
                   zip(top_connections['Donor'], top_connections['Receptor'], top_connections['PTM_Count'])]

    # --- c. 创建并保存图表 ---
    print("正在生成交互式弦图...")
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            # 自定义悬停信息
            hovertemplate='%{label} 有连接<extra></extra>'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            # 自定义悬停信息
            hovertemplate='%{customdata}<extra></extra>',
            customdata=link_labels
        )
    )])

    fig.update_layout(
        title_text=f"潜在可转移代谢物 (PTM) 网络 (Top {TOP_N_CONNECTIONS} Connections)",
        font_size=10,
        width=1000,
        height=1000
    )

    # 保存为HTML文件
    fig.write_html(OUTPUT_HTML_FILE)

    print("\n" + "=" * 60)
    print("🎉 图表生成成功！")
    print(f"请用您的网络浏览器打开以下文件来进行交互式查看:\n{os.path.abspath(OUTPUT_HTML_FILE)}")
    print("=" * 60)


# --- 3. 运行脚本 ---
if __name__ == "__main__":
    # 检查依赖库
    try:
        import plotly
        import pandas
    except ImportError:
        print("=" * 60)
        print("⚠️  重要提示: 必需的库未找到。")
        print("请先在您的终端中运行以下命令来安装它们:")
        print("pip install pandas plotly")
        print("=" * 60)
        exit()

    create_chord_diagram(INPUT_PTM_FILE)