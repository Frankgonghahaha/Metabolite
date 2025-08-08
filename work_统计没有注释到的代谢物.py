import pandas as pd
import os


def summarize_unclassified_metabolites():
    """
    遍历10个已分类的PTM结果文件，汇总所有分类为'None'的代谢物，
    并输出一个包含唯一名单和总数的报告。
    """
    # --- 1. 定义文件路径 ---
    base_path = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystones_PTM/'
    output_file = os.path.join(base_path, 'Unclassified_Metabolites_Summary.csv')

    print("--- 开始汇总未分类的代谢物 ---")

    # --- 2. 初始化集合 ---
    unique_unclassified_metabolites = set()

    # --- 3. 循环处理10个文件 ---
    for i in range(1, 11):
        file_number = i
        input_filename = f'83keystones_PTM_part_{file_number}_classified.csv'
        input_filepath = os.path.join(base_path, input_filename)

        if not os.path.exists(input_filepath):
            print(f"警告: 文件 '{input_filename}' 未找到，已跳过。")
            continue

        try:
            print(f"正在处理文件: {input_filename}...")
            df = pd.read_csv(input_filepath)

            if 'Classification' not in df.columns or 'PTM_Name' not in df.columns:
                print(f"警告: 文件 '{input_filename}' 中缺少 'Classification' 或 'PTM_Name' 列，已跳过。")
                continue

            # ======================================================================
            # --- 4. (已优化的) 核心筛选逻辑 ---
            #
            # 旧的筛选方式:
            # unclassified_df = df[df['Classification'] == 'None']
            #
            # 新的、更健壮的筛选方式:
            # 首先，处理列中可能存在的空值(NaN)和字符串'None'（包括其两边的空格）

            # 条件1: 检查是否为真正的空值 (NaN/NoneType)
            is_null_value = df['Classification'].isnull()

            # 条件2: 检查是否为字符串 'None' (先去除两端空格，并确保是字符串类型)
            is_none_string = df['Classification'].astype(str).str.strip() == 'None'

            # 筛选出满足任一条件的行 (使用 | 代表“或”)
            unclassified_df = df[is_null_value | is_none_string]
            # ======================================================================

            if not unclassified_df.empty:
                newly_found = unclassified_df['PTM_Name'].unique()
                print(f"  -> 在此文件中找到 {len(newly_found)} 种未分类代谢物。")
                unique_unclassified_metabolites.update(newly_found)
            else:
                print("  -> 此文件中没有识别到未分类的代谢物。")

        except Exception as e:
            print(f"[错误] 处理文件 '{input_filename}' 时发生意外: {e}")

    # --- 5. 生成并保存汇总报告 ---
    print("\n--- 所有文件处理完毕，正在生成汇总报告 ---")

    total_unique_count = len(unique_unclassified_metabolites)

    if total_unique_count > 0:
        print(f"在10个文件中，共发现 {total_unique_count} 种不同的未分类代谢物。")
        summary_df = pd.DataFrame(list(unique_unclassified_metabolites), columns=['Unclassified_Metabolite_Name'])
        summary_df.sort_values(by='Unclassified_Metabolite_Name', inplace=True)
        try:
            summary_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"汇总报告已成功保存至:\n{output_file}")
        except Exception as e:
            print(f"[错误] 无法写入汇总文件: {e}")

    else:
        print("在所有文件中，未发现任何可识别的未分类代谢物。")

    print("\n--- 🎉 任务完成！ ---")


if __name__ == '__main__':
    summarize_unclassified_metabolites()