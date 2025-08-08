import pandas as pd
import numpy as np
import os

# --- 1. 设置文件路径 ---

# 输入文件：您需要修改的原始邻接矩阵文件。
INPUT_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step14_Construct_Network_Adjacent_Matrix.csv'

# 输出文件：程序将创建一个新的、修改过的文件，文件名中会包含 "NoSelfLoops"。
# 这样做可以保留您的原始文件，避免数据丢失。
OUTPUT_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step14_Construct_Network_Adjacent_Matrix_NoSelfLoops.csv'


# --- 2. 主函数：读取、修改并保存矩阵 ---

def set_diagonal_to_zero(input_path, output_path):
    """
    读取一个CSV格式的邻接矩阵，将其对角线元素设置为0，然后保存为新文件。
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到输入文件 '{input_path}'")
        print("请确保文件路径和名称正确无误。")
        return

    print(f"➡️ 正在读取文件: {input_path}")

    # 读取CSV文件。index_col=0确保第一列被用作矩阵的行索引（节点名称）。
    try:
        adj_matrix_df = pd.read_csv(input_path, index_col=0)
    except Exception as e:
        print(f"❌ 读取文件时发生错误: {e}")
        return

    print("矩阵加载成功，原始尺寸: ", adj_matrix_df.shape)

    # 核心操作：将对角线值设置为0
    # 我们使用numpy的fill_diagonal函数，效率很高。
    # 首先获取DataFrame中的数值部分作为一个numpy数组
    matrix_values = adj_matrix_df.values

    # 将这个数组的对角线（从左上到右下）所有元素填充为0
    np.fill_diagonal(matrix_values, 0)

    # 将修改后的numpy数组转换回pandas DataFrame，并保持原有的行和列名
    new_adj_matrix_df = pd.DataFrame(matrix_values, index=adj_matrix_df.index, columns=adj_matrix_df.columns)

    print("✅ 对角线值已成功设置为 0。")

    # 保存修改后的DataFrame到新的CSV文件
    # 使用 encoding='utf-8-sig' 来确保最好的兼容性（特别是用Excel打开时）
    try:
        new_adj_matrix_df.to_csv(output_path, encoding='utf-8-sig')
        print(f"💾 新文件已成功保存至: {output_path}")
    except Exception as e:
        print(f"❌ 保存文件时发生错误: {e}")


# --- 3. 运行脚本 ---

if __name__ == "__main__":
    set_diagonal_to_zero(INPUT_FILE, OUTPUT_FILE)
    print("\n--- 操作完成！ ---")