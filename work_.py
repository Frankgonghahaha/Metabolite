import pandas as pd
import os
import shutil

# --- 1. 用户配置区域：请根据需要修改这里的路径和文件名 ---

# 输入文件路径
candidate_file = '/Volumes/CC/6042MAG数据库文件/信息表/20250805物种组合候补名单.xlsx'
species_info_file = '/Volumes/CC/6042MAG数据库文件/信息表/物种信息_丰度信息.xlsx'

# --- [修改部分] ---
# 源MAG文件目录
mags_source_dir = '/Volumes/CC/6042MAG数据库文件/全部MAG文件/'

# 输出目录和文件
# [修改部分] 目标MAG文件目录 (脚本会自动创建)
mags_dest_dir = '/Volumes/CC/6042MAG数据库文件/功能微生物系统发育树/20250806DBP降解功能微生物MAG文件/'
# --- [修改结束] ---

output_species_csv = '/Volumes/CC/6042MAG数据库文件/信息表/20250806_DBP降解功能微生物物种信息.csv'
output_matrix_csv = '/Volumes/CC/6042MAG数据库文件/信息表/20250806_DBP降解功能微生物矩阵.csv'


# --- 脚本主逻辑开始 ---

def main():
    """主函数，按顺序执行所有任务。"""
    print(f"开始处理，读取候补名单文件: {candidate_file}")

    try:
        candidate_df = pd.read_excel(candidate_file, header=1)
    except FileNotFoundError:
        print(f"错误：候补名单文件未找到！请检查路径: {candidate_file}")
        return
    except Exception as e:
        print(f"读取候补名单时发生错误: {e}")
        return

    print("从候补名单中提取所有唯一的 MAG_id...")
    unique_mags = set()
    for col in candidate_df.columns:
        unique_mags.update(candidate_df[col].dropna())

    unique_mags_list = sorted(list(unique_mags))
    print(f"提取完成，共找到 {len(unique_mags_list)} 个唯一的 MAG_id。")

    # --- 任务1: 生成物种信息表 (无变化) ---
    task_1_generate_species_info(unique_mags_list)

    # --- 任务2: 生成功能基因矩阵 (无变化) ---
    gene_columns = [col for col in candidate_df.columns if col != 'CUT1_2_3']
    task_2_generate_gene_matrix(candidate_df, unique_mags_list, gene_columns)

    # --- 任务3: 复制MAG文件 ([修改部分]) ---
    #task_3_copy_mag_files(unique_mags_list)

    print("\n所有任务已完成！")


def task_1_generate_species_info(mags_to_find):
    """从物种信息总表中筛选出目标MAG并输出为CSV。"""
    print("\n--- 开始任务1: 生成物种信息表 ---")
    try:
        print(f"读取物种总表: {species_info_file}")
        species_df = pd.read_excel(species_info_file)

        if 'MAG_id' not in species_df.columns:
            print("错误: 物种信息表中未找到'MAG_id'列。请检查列名是否正确。")
            return

        filtered_species_df = species_df[species_df['MAG_id'].isin(mags_to_find)]
        output_columns = ['MAG_id', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
        final_df = filtered_species_df[output_columns]

        final_df.to_csv(output_species_csv, index=False)
        print(f"成功！已生成物种信息文件: {output_species_csv}")
        print(f"共找到并输出了 {len(final_df)} 条物种信息。")

    except FileNotFoundError:
        print(f"错误：物种信息文件未找到！请检查路径: {species_info_file}")
    except KeyError as e:
        print(f"错误：物种信息表中缺少必要的列: {e}。请检查文件内容。")
    except Exception as e:
        print(f"任务1执行失败: {e}")


def task_2_generate_gene_matrix(candidates_df, mag_list, gene_list):
    """构建基因有无的0/1矩阵。"""
    print("\n--- 开始任务2: 生成功能基因矩阵 ---")
    try:
        matrix_df = pd.DataFrame(0, index=mag_list, columns=gene_list)

        for gene in gene_list:
            mags_with_gene = candidates_df[gene].dropna().unique()
            matrix_df.loc[mags_with_gene, gene] = 1

        matrix_df.to_csv(output_matrix_csv, index=True)
        print(f"成功！已生成基因矩阵文件: {output_matrix_csv}")
        print(f"矩阵维度: {matrix_df.shape[0]} MAGs x {matrix_df.shape[1]} Genes")

    except Exception as e:
        print(f"任务2执行失败: {e}")


# --- [函数已修改] ---
# def task_3_copy_mag_files(mag_list):
#     """根据MAG_id列表复制对应的MAG文件(.fa)。"""
#     print("\n--- 开始任务3: 复制MAG文件 ---")
#
#     if not os.path.exists(mags_dest_dir):
#         print(f"目标文件夹不存在，正在创建: {mags_dest_dir}")
#         os.makedirs(mags_dest_dir)
#
#     copied_count = 0
#     not_found_count = 0
#
#     for mag_id in mag_list:
#         # 构建源文件名 (e.g., ASMAG632.fa)
#         source_file_name = f"{mag_id}.fa"
#         source_file_path = os.path.join(mags_source_dir, source_file_name)
#         dest_file_path = os.path.join(mags_dest_dir, source_file_name)
#
#         if os.path.exists(source_file_path):
#             try:
#                 shutil.copy(source_file_path, dest_file_path)
#                 copied_count += 1
#             except Exception as e:
#                 print(f"复制文件 {source_file_name} 时出错: {e}")
#         else:
#             not_found_count += 1
#
#     print("文件复制完成。")
#     print(f"成功复制: {copied_count} 个文件")
#     if not_found_count > 0:
#         print(f"未能找到: {not_found_count} 个对应的源文件")


if __name__ == "__main__":
    main()