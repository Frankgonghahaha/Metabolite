import pandas as pd
import os


def classify_ptm_results():
    """
    读取PTM结果文件和代谢物分类文件，为PTM列表中的每个代谢物添加分类信息，
    并将最终结果保存到新的CSV文件中。
    """
    # --- 1. 定义文件路径 ---
    # TODO: 请确保这些路径在您的系统中是正确的
    base_path = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystones_PTM/'

    # 输入文件
    ptm_file = os.path.join(base_path, '83keystones_PTM_part_10.csv')
    classification_file = os.path.join(base_path, '代谢物分类表.xlsx')

    # 输出文件
    output_file = os.path.join(base_path, '83keystones_PTM_part_10_classified.csv')

    print("--- 开始执行代谢物分类脚本 ---")

    # --- 2. 读取数据文件 ---
    try:
        print(f"正在读取PTM结果文件: {os.path.basename(ptm_file)}...")
        ptm_df = pd.read_csv(ptm_file)

        print(f"正在读取代谢物分类表: {os.path.basename(classification_file)}...")
        class_df = pd.read_excel(classification_file)
    except FileNotFoundError as e:
        print(f"[错误] 文件未找到: {e}")
        print("请检查文件路径是否正确。")
        return

    print("文件读取成功！\n")

    # --- 3. 创建高效的查询字典 ---
    # 这个字典的结构是 {代谢物名称: 分类结果}
    print("正在创建代谢物分类查询字典...")

    # 指定列名
    metabolite_col = 'metabolite_name'
    class_col = 'Class.in.this.study'

    # 确保列存在
    if metabolite_col not in class_df.columns or class_col not in class_df.columns:
        print(f"[错误] 分类表中未找到必需的列: '{metabolite_col}' 或 '{class_col}'")
        return

    # 创建查询字典，并移除任何可能导致问题的空值
    class_df.dropna(subset=[metabolite_col], inplace=True)
    classification_dict = pd.Series(class_df[class_col].values, index=class_df[metabolite_col]).to_dict()
    print(f"查询字典创建完毕，包含 {len(classification_dict)} 条分类信息。\n")

    # --- 4. 核心处理流程：匹配分类信息 ---
    print("正在为PTM列表匹配分类信息...")

    # 指定要匹配的列名
    ptm_name_col = 'PTM_Name'

    if ptm_name_col not in ptm_df.columns:
        print(f"[错误] PTM结果表中未找到必需的列: '{ptm_name_col}'")
        return

    # 使用 .map() 方法进行高效匹配
    # .map() 会根据字典的键（代谢物名称）来查找值（分类）
    # 如果在字典中找不到，它会自动返回 NaN (Not a Number)
    ptm_df['Classification'] = ptm_df[ptm_name_col].map(classification_dict)

    # 使用 .fillna() 方法将所有未匹配到的 NaN 值替换为您指定的 'None'
    ptm_df['Classification'].fillna('None', inplace=True)

    print("分类匹配完成！\n")

    # --- 5. 保存最终结果 ---
    try:
        print(f"正在将结果保存到新文件: {os.path.basename(output_file)}...")
        # 将结果保存到CSV文件，使用 'utf-8-sig' 编码以确保在Excel中打开时中文无乱码
        ptm_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print("--- 🎉 脚本执行完毕 ---")
        print(f"详细结果已保存在:\n{output_file}")
    except Exception as e:
        print(f"[错误] 无法写入文件 {os.path.basename(output_file)}: {e}")


if __name__ == '__main__':
    classify_ptm_results()