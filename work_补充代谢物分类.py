# # import pandas as pd
# # import os
# #
# #
# # def update_and_reclassify_metabolites():
# #     """
# #     根据一个补充的分类表格，更新10个PTM结果文件中的代谢物分类，
# #     并将更新后的表格另存为 Excel (.xlsx) 文件。
# #     """
# #     # --- 1. 定义文件路径 ---
# #     base_path = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystones_PTM/'
# #     supplemental_file = os.path.join(base_path, '补充代谢物分类.xlsx')
# #
# #     print("--- 任务开始：更新代谢物分类信息 ---")
# #
# #     # --- 2. 加载并准备补充的分类映射表 ---
# #     try:
# #         print(f"\n--- 步骤 1: 正在从以下文件加载补充分类信息:\n{supplemental_file}")
# #         supplemental_df = pd.read_excel(supplemental_file)
# #
# #         # 检查必需的列是否存在
# #         if 'Unclassified_Metabolite_Name' not in supplemental_df.columns or 'Class.in.this.study' not in supplemental_df.columns:
# #             print(
# #                 f"[错误] 补充文件 '{supplemental_file}' 中缺少 'Unclassified_Metabolite_Name' 或 'Class.in.this.study' 列。")
# #             return
# #
# #         # 创建一个高效的查询映射: {代谢物名称: 分类信息}
# #         # .set_index() 用于将代谢物名称列设为索引
# #         # .to_dict() 用于将'Class.in.this.study'列转换为字典
# #         classification_map = supplemental_df.set_index('Unclassified_Metabolite_Name')['Class.in.this.study'].to_dict()
# #         print(f"-> 成功加载 {len(classification_map)} 条代谢物分类映射。")
# #
# #     except FileNotFoundError:
# #         print(f"[错误] 无法找到补充文件: {supplemental_file}。请检查文件路径是否正确。")
# #         return
# #     except Exception as e:
# #         print(f"[错误] 读取补充文件时发生意外: {e}")
# #         return
# #
# #     print("\n--- 步骤 2: 开始遍历和更新10个原始数据文件 ---")
# #     # --- 3. 循环处理10个原始文件 ---
# #     for i in range(11, 12):
# #         file_number = i
# #         input_filename = f'83keystones_PTM_part_{file_number}_classified.csv'
# #         input_filepath = os.path.join(base_path, input_filename)
# #
# #         # 定义新的输出文件名和路径
# #         output_filename = f'83keystones_PTM_part_{file_number}_reclassified.xlsx'
# #         output_filepath = os.path.join(base_path, output_filename)
# #
# #         if not os.path.exists(input_filepath):
# #             print(f"\n警告: 文件 '{input_filename}' 未找到，已跳过。")
# #             continue
# #
# #         try:
# #             print(f"\n正在处理文件: {input_filename}...")
# #             df = pd.read_csv(input_filepath)
# #
# #             # --- 核心更新逻辑 ---
# #             # 1. 识别需要更新的行 (与你之前的脚本逻辑相同)
# #             is_null_value = df['Classification'].isnull()
# #             is_none_string = df['Classification'].astype(str).str.strip() == 'None'
# #             rows_to_update_mask = is_null_value | is_none_string
# #
# #             num_to_update = rows_to_update_mask.sum()
# #
# #             if num_to_update > 0:
# #                 print(f"  -> 在此文件中发现 {num_to_update} 行需要更新分类。")
# #
# #                 # 2. 提取需要更新行的 'PTM_Name'
# #                 metabolite_names_to_map = df.loc[rows_to_update_mask, 'PTM_Name']
# #
# #                 # 3. 使用 .map() 函数和之前创建的字典来获取新的分类
# #                 new_classifications = metabolite_names_to_map.map(classification_map)
# #
# #                 # 4. 将新的分类信息填充回 'Classification' 列
# #                 #    使用 .fillna() 来处理在补充表格中找不到的代谢物，让它们保持原样（'None'）
# #                 #    这样可以避免将它们错误地修改为 NaN (空值)
# #                 df.loc[rows_to_update_mask, 'Classification'] = new_classifications.fillna(
# #                     df.loc[rows_to_update_mask, 'Classification'])
# #
# #                 # 计算成功更新了多少个
# #                 updated_count = df.loc[rows_to_update_mask, 'Classification'].notna().sum() - (
# #                             df.loc[rows_to_update_mask, 'Classification'] == 'None').sum()
# #                 print(f"  -> 成功更新了 {updated_count} 行的分类信息。")
# #
# #             else:
# #                 print("  -> 此文件无需更新分类信息。")
# #
# #             # --- 4. 保存更新后的DataFrame为Excel文件 ---
# #             print(f"  -> 正在将结果保存至: {output_filename}...")
# #             # 使用 to_excel 保存，index=False 表示不将DataFrame的索引写入文件
# #             df.to_excel(output_filepath, index=False, engine='openpyxl')
# #             print(f"  -> 文件已成功保存。")
# #
# #         except Exception as e:
# #             print(f"[错误] 处理或保存文件 '{input_filename}' 时发生意外: {e}")
# #
# #     print("\n--- 🎉 所有文件更新并另存为Excel格式，任务完成！ ---")
# #
# #
# # if __name__ == '__main__':
# #     update_and_reclassify_metabolites()
# import pandas as pd
# import os
#
#
# def update_and_reclassify_metabolites():
#     """
#     根据一个补充的分类表格，更新10个PTM结果文件中的代谢物分类，
#     并将更新后的表格另存为 Excel (.xlsx) 文件。
#     """
#     # --- 1. 定义文件路径 ---
#     base_path = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystones_PTM/'
#     supplemental_file = os.path.join(base_path, '补充代谢物分类.xlsx')
#
#     print("--- 任务开始：更新代谢物分类信息 ---")
#
#     # --- 2. 加载并准备补充的分类映射表 ---
#     try:
#         print(f"\n--- 步骤 1: 正在从以下文件加载补充分类信息:\n{supplemental_file}")
#         supplemental_df = pd.read_excel(supplemental_file)
#
#         # 检查必需的列是否存在
#         if 'Unclassified_Metabolite_Name' not in supplemental_df.columns or 'Class.in.this.study' not in supplemental_df.columns:
#             print(
#                 f"[错误] 补充文件 '{supplemental_file}' 中缺少 'Unclassified_Metabolite_Name' 或 'Class.in.this.study' 列。")
#             return
#
#         # 创建一个高效的查询映射: {代谢物名称: 分类信息}
#         classification_map = supplemental_df.set_index('Unclassified_Metabolite_Name')['Class.in.this.study'].to_dict()
#         print(f"-> 成功加载 {len(classification_map)} 条代谢物分类映射。")
#
#     except FileNotFoundError:
#         print(f"[错误] 无法找到补充文件: {supplemental_file}。请检查文件路径是否正确。")
#         return
#     except Exception as e:
#         print(f"[错误] 读取补充文件时发生意外: {e}")
#         return
#
#     print("\n--- 步骤 2: 开始遍历和更新10个原始数据文件 ---")
#     # --- 3. 循环处理10个原始文件 ---
#     for i in range(11, 12):
#         file_number = i
#         input_filename = f'83keystones_PTM_part_{file_number}_classified.csv'
#         input_filepath = os.path.join(base_path, input_filename)
#
#         output_filename = f'83keystones_PTM_part_{file_number}_reclassified.xlsx'
#         output_filepath = os.path.join(base_path, output_filename)
#
#         if not os.path.exists(input_filepath):
#             print(f"\n警告: 文件 '{input_filename}' 未找到，已跳过。")
#             continue
#
#         try:
#             print(f"\n正在处理文件: {input_filename}...")
#
#             # --- 这是核心修改点 ---
#             # 尝试使用不同的编码格式读取文件，以解决编码错误
#             try:
#                 # 首先尝试默认的 utf-8
#                 df = pd.read_csv(input_filepath)
#             except UnicodeDecodeError:
#                 # 如果 utf-8 失败，则尝试使用 gbk，这在处理中文CSV时很常见
#                 print(f"  -> 使用 UTF-8 编码读取失败，正在尝试使用 'gbk' 编码...")
#                 df = pd.read_csv(input_filepath, encoding='gbk')
#
#             # --- 核心更新逻辑 ---
#             is_null_value = df['Classification'].isnull()
#             is_none_string = df['Classification'].astype(str).str.strip() == 'None'
#             rows_to_update_mask = is_null_value | is_none_string
#
#             num_to_update = rows_to_update_mask.sum()
#
#             if num_to_update > 0:
#                 print(f"  -> 在此文件中发现 {num_to_update} 行需要更新分类。")
#
#                 metabolite_names_to_map = df.loc[rows_to_update_mask, 'PTM_Name']
#                 new_classifications = metabolite_names_to_map.map(classification_map)
#
#                 df.loc[rows_to_update_mask, 'Classification'] = new_classifications.fillna(
#                     df.loc[rows_to_update_mask, 'Classification'])
#
#                 updated_count = df.loc[rows_to_update_mask, 'Classification'].notna().sum() - \
#                                 (df.loc[rows_to_update_mask, 'Classification'] == 'None').sum()
#                 print(f"  -> 成功更新了 {updated_count} 行的分类信息。")
#
#             else:
#                 print("  -> 此文件无需更新分类信息。")
#
#             # --- 4. 保存更新后的DataFrame为Excel文件 ---
#             print(f"  -> 正在将结果保存至: {output_filename}...")
#             df.to_excel(output_filepath, index=False, engine='openpyxl')
#             print(f"  -> 文件已成功保存。")
#
#         except Exception as e:
#             print(f"[错误] 处理或保存文件 '{input_filename}' 时发生意外: {e}")
#
#     print("\n--- 🎉 所有文件更新并另存为Excel格式，任务完成！ ---")
#
#
# if __name__ == '__main__':
#     update_and_reclassify_metabolites()
import pandas as pd
import os


def update_and_reclassify_metabolites():
    """
    根据一个补充的分类表格，更新PTM结果文件中的代谢物分类，
    并自动检测和处理 .csv 或 .xlsx 格式的输入文件。
    """
    # --- 1. 定义文件路径 ---
    base_path = '/Volumes/CC/全球+国内96s/INAP 计算表/20250802/83keystones_PTM/'
    supplemental_file = os.path.join(base_path, '补充代谢物分类.xlsx')

    print("--- 任务开始：更新代谢物分类信息 ---")

    # --- 2. 加载并准备补充的分类映射表 ---
    try:
        print(f"\n--- 步骤 1: 正在从以下文件加载补充分类信息:\n{supplemental_file}")
        supplemental_df = pd.read_excel(supplemental_file)
        if 'Unclassified_Metabolite_Name' not in supplemental_df.columns or 'Class.in.this.study' not in supplemental_df.columns:
            print(f"[错误] 补充文件 '{supplemental_file}' 中缺少必需的列。")
            return
        classification_map = supplemental_df.set_index('Unclassified_Metabolite_Name')['Class.in.this.study'].to_dict()
        print(f"-> 成功加载 {len(classification_map)} 条代谢物分类映射。")

    except FileNotFoundError:
        print(f"[错误] 无法找到补充文件: {supplemental_file}。请检查文件路径是否正确。")
        return
    except Exception as e:
        print(f"[错误] 读取补充文件时发生意外: {e}")
        return

    print("\n--- 步骤 2: 开始遍历和更新原始数据文件 ---")
    # --- 3. 循环处理文件 ---
    for i in range(11, 12):  # 循环仍然是处理编号11的文件
        file_number = i

        # --- 核心修改部分：自动检测文件格式 ---
        # 1. 定义两种可能的文件名和路径
        csv_input_filename = f'83keystones_PTM_part_{file_number}_classified.csv'
        xlsx_input_filename = f'83keystones_PTM_part_{file_number}_classified.xlsx'  # 这是你新保存的文件

        csv_filepath = os.path.join(base_path, csv_input_filename)
        xlsx_filepath = os.path.join(base_path, xlsx_input_filename)

        # 定义统一的输出文件名
        output_filename = f'83keystones_PTM_part_{file_number}_reclassified.xlsx'
        output_filepath = os.path.join(base_path, output_filename)

        df = None
        input_filename = None

        # 2. 检查 .xlsx 文件是否存在，如果存在则优先读取
        if os.path.exists(xlsx_filepath):
            try:
                print(f"\n检测到并正在处理 XLSX 文件: {xlsx_input_filename}...")
                df = pd.read_excel(xlsx_filepath)
                input_filename = xlsx_input_filename
            except Exception as e:
                print(f"[错误] 读取 XLSX 文件 '{xlsx_input_filename}' 时发生意外: {e}")
                continue  # 跳过这个文件，继续下一个循环

        # 3. 如果 .xlsx 不存在，则回退尝试读取 .csv 文件
        elif os.path.exists(csv_filepath):
            try:
                print(f"\n未找到XLSX文件，正在处理 CSV 文件: {csv_input_filename}...")
                df = pd.read_csv(csv_filepath, encoding='gbk')  # 假设可能还是gbk编码问题
                input_filename = csv_input_filename
            except UnicodeDecodeError:
                print(f"  -> 使用 GBK 编码读取失败，尝试使用 UTF-8...")
                df = pd.read_csv(csv_filepath, encoding='utf-8')
                input_filename = csv_input_filename
            except Exception as e:
                print(f"[错误] 读取 CSV 文件 '{csv_input_filename}' 时发生意外: {e}")
                continue

        # 4. 如果两种文件都不存在，则警告并跳过
        else:
            print(f"\n[警告] 文件 '{xlsx_input_filename}' 或 '{csv_input_filename}' 均未找到，已跳过。")
            continue
        # --- 修改结束 ---

        try:
            # --- 核心更新逻辑 (这部分无需改动) ---
            is_null_value = df['Classification'].isnull()
            is_none_string = df['Classification'].astype(str).str.strip() == 'None'
            rows_to_update_mask = is_null_value | is_none_string

            num_to_update = rows_to_update_mask.sum()

            if num_to_update > 0:
                print(f"  -> 在此文件中发现 {num_to_update} 行需要更新分类。")
                metabolite_names_to_map = df.loc[rows_to_update_mask, 'PTM_Name']
                new_classifications = metabolite_names_to_map.map(classification_map)
                df.loc[rows_to_update_mask, 'Classification'] = new_classifications.fillna(
                    df.loc[rows_to_update_mask, 'Classification'])
                updated_count = df.loc[rows_to_update_mask, 'Classification'].notna().sum() - (
                            df.loc[rows_to_update_mask, 'Classification'] == 'None').sum()
                print(f"  -> 成功更新了 {updated_count} 行的分类信息。")
            else:
                print("  -> 此文件无需更新分类信息。")

            # --- 4. 保存更新后的DataFrame为Excel文件 ---
            print(f"  -> 正在将结果保存至: {output_filename}...")
            df.to_excel(output_filepath, index=False, engine='openpyxl')
            print(f"  -> 文件已成功保存。")

        except Exception as e:
            # 使用变量 input_filename 来显示当前处理的是哪个文件
            print(f"[错误] 处理或保存文件 '{input_filename}' 时发生意外: {e}")

    print("\n--- 🎉 所有文件更新并另存为Excel格式，任务完成！ ---")


if __name__ == '__main__':
    update_and_reclassify_metabolites()