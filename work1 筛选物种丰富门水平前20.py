import pandas as pd

# --- 1. 定义文件路径 ---
# 请确保这个路径是您Excel文件的准确位置
input_excel_path = "/Volumes/CC/6042MAG数据库文件/信息表/20250806_DBP降解功能微生物物种信息.xlsx"
# 定义输出的新Excel文件的名称
output_excel_path = "/Volumes/CC/6042MAG数据库文件/信息表/20250806iTol_DBP降解菌物种分布.xlsx"

try:
    # --- 2. 读取Excel文件 ---
    # pandas会读取文件中的第一个工作表
    df = pd.read_excel(input_excel_path)

    # --- 3. 统计“Phylum”列中每个门的物种数量 ---
    # value_counts()会统计每个值出现的次数，并自动按降序排列
    phylum_counts = df['Phylum'].value_counts()

    print("原始数据中所有门的物种数量统计：")
    print(phylum_counts)
    print("-" * 30)  # 打印一个分隔线

    # --- 4. 确定数量排名前20的门 ---
    # .head(20) 选取前20个，.index 获取这些门的名称
    top_20_phyla = phylum_counts.head(20).index.tolist()

    print("物种数量排名前20的门是：")
    print(top_20_phyla)
    print("-" * 30)


    # --- 5. 创建新列，并进行分类和重命名 ---

    # 定义一个函数来应用到每一行
    def group_and_rename_phylum(phylum_name):
        # 检查当前行的门名称是否在我们的top_20_phyla列表中
        if phylum_name in top_20_phyla:
            # 如果在，就去除'p__'前缀
            # str.removeprefix() 是Python 3.9+ 的新功能，非常方便
            # 如果您的Python版本较低，可以使用 str.replace('p__', '')
            return phylum_name.removeprefix('p__')
        else:
            # 如果不在，就归类为'Others'
            return 'Others'


    # 使用 .apply() 方法将上面的函数应用到'Phylum'列的每一行
    # 并将结果存入一个名为 'Phylum_Grouped' 的新列
    df['Phylum_Grouped'] = df['Phylum'].apply(group_and_rename_phylum)

    # --- 6. 保存结果到新的Excel文件 ---
    # index=False 表示在保存文件时，不把DataFrame的行索引写入Excel
    df.to_excel(output_excel_path, index=False)

    print(f"处理完成！\n结果已保存到新的Excel文件中：\n{output_excel_path}")
    print("\n新创建的 'Phylum_Grouped' 列的内容统计：")
    print(df['Phylum_Grouped'].value_counts())

except FileNotFoundError:
    print(f"错误：找不到文件 '{input_excel_path}'。请检查文件路径是否正确。")
except KeyError:
    print("错误：在Excel文件中找不到名为 'Phylum' 的列。请检查列名是否正确。")
except Exception as e:
    print(f"处理过程中发生了一个未预料到的错误: {e}")