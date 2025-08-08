import pandas as pd
import os


def analyze_received_metabolites():
    """
    遍历一系列PTM文件，筛选出特定MAG作为Receptor（接收方）的
    所有代谢交换记录，并汇总结果。
    """
    # --- 1. 配置参数 ---

    # 包含11个子表格的文件夹路径
    base_path = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystones_PTM/补充代谢物分类/'

    # 您想研究的、作为接收方的MAG列表
    target_mags_as_receptor = {
        'ASMAG294_CDS', 'MAG1330_CDS', 'MAG356_CDS', 'MAG817_CDS', 'MAG890_CDS',
        'MAG851_CDS', 'MAG1319_CDS', 'MAG59_CDS', 'MAG744_CDS', 'MAG1008_CDS',
        's91bin18.1_re_CDS'
    }

    # 输出结果保存的文件名
    output_file = os.path.join(base_path, 'Target_MAGs_Received_Metabolites.xlsx')

    print("--- 任务开始：分析特定MAG作为Receptor的代谢记录 ---")

    # --- 2. 遍历文件并提取数据 ---

    # 用于存储从每个文件中筛选出的DataFrame
    list_of_dfs = []

    # 循环处理 part_1.xlsx 到 part_11.xlsx
    for i in range(1, 12):
        file_name = f'83keystones_PTM_part_{i}.xlsx'
        file_path = os.path.join(base_path, file_name)

        if not os.path.exists(file_path):
            print(f"\n[警告] 文件 '{file_name}' 未找到，已跳过。")
            continue

        try:
            print(f"\n正在处理文件: {file_name}...")
            df = pd.read_excel(file_path)

            # 检查'Receptor'列是否存在
            if 'Receptor' not in df.columns:
                print(f"  -> [错误] 文件中缺少 'Receptor' 列，已跳过。")
                continue

            # 核心筛选逻辑：查找'Receptor'列的值在目标MAG集合中的所有行
            filtered_df = df[df['Receptor'].isin(target_mags_as_receptor)]

            if not filtered_df.empty:
                print(f"  -> 找到 {len(filtered_df)} 条相关记录。")
                list_of_dfs.append(filtered_df)
            else:
                print("  -> 未找到相关记录。")

        except Exception as e:
            print(f"[错误] 处理文件 '{file_name}' 时发生意外: {e}")

    # --- 3. 整合、排序并输出结果 ---

    if not list_of_dfs:
        print("\n--- 任务完成，但在任何文件中都未找到目标MAG作为接收方的记录。 ---")
        return

    print("\n--- 步骤 3: 正在汇总和排序所有找到的记录 ---")

    # 将所有找到的DataFrame合并成一个
    final_result_df = pd.concat(list_of_dfs, ignore_index=True)

    # 去除可能存在的完全重复的记录
    final_result_df.drop_duplicates(inplace=True)

    # 关键排序：先按Receptor分组，再按代谢物名称排序，方便查看
    final_result_df.sort_values(by=['Receptor', 'PTM_Name'], inplace=True, ignore_index=True)

    print("\n--- 筛选和汇总结果 ---")
    # 使用 to_string() 确保在控制台中打印所有行，而不是省略号
    print(final_result_df.to_string())

    # --- 4. 保存到新的Excel文件 ---
    try:
        final_result_df.to_excel(output_file, index=False)
        print(f"\n\n--- 🎉 任务完成！详细结果已保存至:\n{output_file} ---")
    except Exception as e:
        print(f"\n[错误] 保存结果文件时发生意外: {e}")


if __name__ == '__main__':
    analyze_received_metabolites()