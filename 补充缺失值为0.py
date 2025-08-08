import pandas as pd
import os

# --- 1. 请在这里设置您的文件路径 ---
# 【必需】您想要处理的邻接矩阵CSV文件的完整路径
INPUT_MATRIX_PATH = '/Volumes/CC/6042MAG数据库文件/6042_PhyloMInt/Step14_Construct_Network_Adjacent_Matrix.csv'

# 【可选】修改后新文件的保存路径
# 如果留空，脚本会自动在原文件名后加上 "_filled" 作为新文件名
OUTPUT_MATRIX_PATH = ''


# --- 2. 主程序 ---

def fill_nan_in_matrix(input_path, output_path):
    """
    读取一个CSV矩阵文件，将其中所有的缺失值（NaN）替换为0，并保存为新文件。
    """
    # a. 安全性检查：确保输入文件存在
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到输入文件 '{input_path}'")
        print("请确保您在脚本中设置了正确的路径。")
        return

    print(f"--- 开始处理矩阵文件 ---")
    print(f"正在读取文件: {os.path.basename(input_path)}")

    try:
        # b. 加载数据
        # index_col=0 确保第一列被用作行名（索引）
        df = pd.read_csv(input_path, index_col=0)

        # c. 核心操作：填充缺失值
        print("正在将所有缺失值 (NaN) 替换为 0 ...")
        # .fillna(0) 会返回一个新的DataFrame，其中所有NaN都被替换为0
        df_filled = df.fillna(0)

        # d. 确定输出路径
        if not output_path:
            # 如果未指定输出路径，则自动生成一个
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_filled{ext}"

        # e. 保存修改后的DataFrame到新文件
        df_filled.to_csv(output_path, encoding='utf-8-sig')

        print("\n" + "=" * 50)
        print("🎉 成功！")
        print(f"已将处理后的矩阵保存到新文件:\n{output_path}")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 处理过程中发生未知错误: {e}")


# --- 3. 运行脚本 ---
if __name__ == "__main__":
    # 运行主函数
    fill_nan_in_matrix(INPUT_MATRIX_PATH, OUTPUT_MATRIX_PATH)