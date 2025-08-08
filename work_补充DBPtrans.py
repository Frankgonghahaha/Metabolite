# import pandas as pd
# import cobra
# import os
#
# # --- 1. 用户配置区域 ---
#
# candidate_file = '/Volumes/CC/6042MAG数据库文件/信息表/20250805物种组合候补名单.xlsx'
# # 输入和输出将使用同一个目录
# model_dir = '/Volumes/CC/6042MAG数据库文件/Final_Modified_Models/'
#
# # --- [修改] --- 输出目录现在和输入目录是同一个
# output_dir = model_dir
#
# # 基因列表
# TRANSPORT_GENES = [
#     'yvak',
#     'CUT1_2_3',
#     'dph',
#     'dphB',
#     'EstJ6',
#     'GoEst15',
#     'carEW',
#     'pehA',
#     'XtjR8'
# ]
#
#
# # --- 脚本逻辑 ---
#
# def get_transport_mags(file_path, gene_list):
#     """从候补名单中读取数据，返回一个MAG到其转运基因列表的字典。"""
#     print(f"正在读取候补名单: {file_path}")
#     try:
#         df = pd.read_excel(file_path, header=1)
#     except Exception as e:
#         print(f"读取文件时出错: {e}")
#         return None
#
#     mags_with_genes = {}
#     print(f"正在筛选与转运基因 {gene_list} 相关的MAGs...")
#
#     existing_genes = [gene for gene in gene_list if gene in df.columns]
#     missing_genes = [gene for gene in gene_list if gene not in df.columns]
#     if missing_genes:
#         print(f"警告：在Excel文件中找不到以下列（基因），将忽略它们: {missing_genes}")
#
#     relevant_df = df[existing_genes]
#
#     for gene in relevant_df.columns:
#         mags_in_col = relevant_df[gene].dropna().unique()
#         for mag_id in mags_in_col:
#             if mag_id not in mags_with_genes:
#                 mags_with_genes[mag_id] = []
#             mags_with_genes[mag_id].append(gene)
#
#     print(f"找到 {len(mags_with_genes)} 个MAGs含有指定的转运基因。")
#     return mags_with_genes
#
#
# def add_dbp_transport_reactions(model, genes_for_this_mag):
#     """向给定的模型中添加DBP简单扩散转运反应（可逆）。"""
#     reaction_id = 'DBPtex'
#     reaction_name = 'DBP simple diffusion (extracellular to cytosol)'
#     gpr_rule = ' or '.join(genes_for_this_mag)
#
#     if reaction_id in model.reactions:
#         print(f"    - 反应 '{reaction_id}' 已存在于模型中，跳过添加。")
#         return model
#
#     try:
#         reaction = cobra.Reaction(reaction_id)
#         reaction.name = reaction_name
#         reaction.gene_reaction_rule = gpr_rule
#         reaction.lower_bound = -1000.
#         reaction.upper_bound = 1000.
#
#         # 这两种写法都可以，效果完全一样，这里我们用回更简洁的字符串写法
#         reaction.build_reaction_from_string('dbp_e <=> dbp_c')
#
#         model.add_reactions([reaction])
#         print(f"    + 成功添加可逆反应 '{reaction_id}' (GPR: {gpr_rule})")
#
#     except Exception as e:
#         print(f"    - 添加反应 '{reaction_id}' 时失败: {e}")
#         print("    - 请检查代谢物ID ('dbp_e', 'dbp_c') 是否在模型中已存在。")
#
#     return model
#
#
# def main():
#     """主执行函数"""
#     if not os.path.exists(model_dir):
#         print(f"错误：输入的模型目录不存在，请检查路径: {model_dir}")
#         return
#
#     mags_to_modify = get_transport_mags(candidate_file, TRANSPORT_GENES)
#     if mags_to_modify is None: return
#
#     print("\n开始遍历MAG并修改模型(将直接覆盖原文件)...")
#     success_count, fail_count = 0, 0
#
#     for mag_id, genes in mags_to_modify.items():
#         # --- [修改] --- 输出文件名和输入文件名现在是完全一样的路径
#         model_path = os.path.join(model_dir, f"{mag_id}.xml")
#         output_path = model_path
#
#         if not os.path.exists(model_path):
#             print(f"警告：找不到模型文件 {model_path}，跳过。")
#             fail_count += 1
#             continue
#
#         try:
#             print(f"\n处理模型: {mag_id}")
#             model = cobra.io.read_sbml_model(model_path)
#             modified_model = add_dbp_transport_reactions(model, genes)
#
#             # 直接将修改后的模型写回原路径，覆盖原文件
#             cobra.io.write_sbml_model(modified_model, output_path)
#             print(f"  -> 已修改并覆盖保存模型: {output_path}")
#             success_count += 1
#         except Exception as e:
#             print(f"处理模型 {mag_id} 时发生严重错误: {e}")
#             fail_count += 1
#
#     print("\n--- 处理完毕 ---")
#     print(f"成功修改并保存了 {success_count} 个模型。")
#     print(f"失败或跳过了 {fail_count} 个模型。")
#
#
# if __name__ == "__main__":
#     main()
import pandas as pd
import cobra
import os
import re
from collections import defaultdict


def build_full_pathway_models_final_corrected():
    """
    为每个MAG加载原始模型，添加完整的DBP通路骨架，并根据其拥有的功能基因，
    为通路中的反应添加正确的GPR规则（包括条件性地添加DBP转运反应），
    最后保存功能完整的最终模型。
    """
    # --- 1. 定义文件和目录路径 ---
    base_path = '/Volumes/CC/6042MAG数据库文件/'
    info_dir = os.path.join(base_path, '信息表/')
    csv_input_dir = info_dir
    models_input_dir = os.path.join(base_path, '全部代谢模型/')
    final_output_dir = os.path.join(base_path, 'Final_Modified_Models/')
    os.makedirs(final_output_dir, exist_ok=True)

    print("--- 开始执行最终的、完整的模型构建脚本 (Final Corrected Version) ---")

    # --- 2. 定义通路所需的所有新陈代谢物和反应 (已整合您的全部修改) ---
    new_metabolites_info = [
        ('dbph_c', 'c', 'C16H22O4', 'Dibutyl phthalate (Cytosol)'),
        ('dbph_e', 'e', 'C16H22O4', 'Dibutyl phthalate (Extracellular)'),
        ('mbph_c', 'c', 'C12H14O4', 'Monobutyl phthalate'),
        ('1btol_c', 'c', 'C4H10O', 'butan-1-ol'),
        ('pht_c', 'c', 'C8H4O4', 'Phthalate (Cytosol)'),
        ('pht_e', 'e', 'C8H4O4', 'Phthalate (Extracellular)'),
        ('pht34dd_c', 'c', 'C8H8O6', 'Phthalate 3,4-cis-dihydrodiol'),
        ('34dhp_c', 'c', 'C8H6O6', '3,4-Dihydroxyphthalate'),
        ('pht45dd_c', 'c', 'C8H8O6', 'Phthalate 4,5-cis-dihydrodiol'),
        ('45dhp_c', 'c', 'C8H6O6', '4,5-Dihydroxyphthalate')
    ]

    pathway_reactions_info = [
        {'id': 'PHTt', 'name': 'Phthalate transport', 'subsystem': 'DBP degradation transport',
         'equation': 'pht_e <=> pht_c', 'gpr': 'ophF or ophH or ophD'},
        {'id': 'DBPH1', 'name': 'Dibutyl phthalate hydrolase (step 1)', 'subsystem': 'DBP degradation',
         'equation': 'dbph_c + h2o_c --> mbph_c + 1btol_c',
         'gpr': 'yvak or dphB or dph or pehA or GoEst15 or EstJ6 or XtjR8 or carEW'},
        {'id': 'MBPH1', 'name': 'Monobutyl phthalate hydrolase', 'subsystem': 'DBP degradation',
         'equation': 'mbph_c + h2o_c --> pht_c + 1btol_c',
         'gpr': 'yvak or dphB or dph or pehA or GoEst15 or EstJ6 or XtjR8 or carEW'},
        {'id': 'DBPH2', 'name': 'Dibutyl phthalate hydrolase (overall)', 'subsystem': 'DBP degradation',
         'equation': 'dbph_c + 2 h2o_c --> pht_c + 2 1btol_c', 'gpr': 'CUT1_2_3'},
        {'id': 'PHT34DO', 'name': 'Phthalate 3,4-dioxygenase', 'subsystem': 'DBP degradation',
         'equation': 'pht_c + o2_c + nadh_c + h_c <=> pht34dd_c + nad_c', 'gpr': 'phtAa and phtAc and phtAd'},
        {'id': 'PHT34DDH', 'name': 'Phthalate 3,4-dihydrodiol dehydrogenase', 'subsystem': 'DBP degradation',
         'equation': 'pht34dd_c + nad_c <=> 34dhp_c + nadh_c + h_c', 'gpr': 'phtB'},
        {'id': '34DHPDC', 'name': '3,4-Dihydroxyphthalate decarboxylase', 'subsystem': 'DBP degradation',
         'equation': '34dhp_c <=> 34dhbz_c + co2_c', 'gpr': 'phtC'},
        {'id': 'PHT45DO', 'name': 'Phthalate 4,5-dioxygenase', 'subsystem': 'DBP degradation',
         'equation': 'pht_c + o2_c + nadh_c + h_c <=> pht45dd_c + nad_c', 'gpr': 'pht3'},
        {'id': 'PHT45DDH', 'name': 'Phthalate 4,5-dihydrodiol dehydrogenase', 'subsystem': 'DBP degradation',
         'equation': 'pht45dd_c + nad_c <=> 45dhp_c + nadh_c + h_c', 'gpr': 'pht4'},
        {'id': '45DHPDC', 'name': '4,5-Dihydroxyphthalate decarboxylase', 'subsystem': 'DBP degradation',
         'equation': '45dhp_c <=> 34dhbz_c + co2_c', 'gpr': 'pht5'}
    ]

    # --- 3. 构建 MAG -> [基因列表] 的总览图 ---
    print("\n--- 步骤 1: 正在构建MAG与基因的对应总览图 ---")
    mag_to_genes = defaultdict(list)
    all_genes_in_rules = {gene for rule in pathway_reactions_info for gene in re.findall(r'\b\w+\b', rule['gpr'])}
    for gene in all_genes_in_rules:
        csv_path = os.path.join(csv_input_dir, f"{gene}.csv")
        if os.path.exists(csv_path):
            try:
                mags_df = pd.read_csv(csv_path)
                mag_id_col = mags_df.columns[0]
                for mag_id in mags_df[mag_id_col]:
                    mag_to_genes[mag_id].append(gene)
            except pd.errors.EmptyDataError:
                continue
    print(f"总览图构建完毕，共找到 {len(mag_to_genes)} 个需要修改的MAG。")

    # --- 4. 构建 基因 -> GPR规则 的反向查找表 ---
    gene_to_rule_map = {}
    for rule in pathway_reactions_info:
        genes_in_gpr = re.findall(r'\b\w+\b', rule['gpr'])
        for gene in genes_in_gpr:
            gene_to_rule_map[gene] = {'reaction_id': rule['id'], 'gpr': rule['gpr']}

    # --- 5. 遍历每个MAG，完成通路添加和GPR更新 ---
    print("\n--- 步骤 2: 正在逐个处理MAG，构建完整通路并保存 ---")
    if not mag_to_genes:
        print("未找到任何需要处理的MAG，脚本结束。")
        return

    for mag_id, owned_genes in mag_to_genes.items():
        print(f"\n-- 处理 MAG: {mag_id} --")
        model_filename = f"{mag_id}_CDS.xml"
        model_path = os.path.join(models_input_dir, model_filename)
        if not os.path.exists(model_path):
            print(f"   [警告] 原始模型文件未找到: {model_path}，已跳过。")
            continue
        try:
            model = cobra.io.read_sbml_model(model_path)

            # 步骤A: 添加通路骨架
            print(f"   -> 步骤A: 检查并添加DBP降解通路的代谢物和反应...")
            metabolites_to_add = [cobra.Metabolite(id=met_id, compartment=comp, formula=formula, name=name) for
                                  met_id, comp, formula, name in new_metabolites_info if
                                  not model.metabolites.has_id(met_id)]
            if metabolites_to_add: model.add_metabolites(metabolites_to_add)

            reactions_to_add = [cobra.Reaction(rxn_info['id'], name=rxn_info['name'], subsystem=rxn_info['subsystem'])
                                for rxn_info in pathway_reactions_info if not model.reactions.has_id(rxn_info['id'])]
            if reactions_to_add:
                model.add_reactions(reactions_to_add)
                for rxn_info in pathway_reactions_info:
                    if model.reactions.has_id(rxn_info['id']) and not model.reactions.get_by_id(
                            rxn_info['id']).reaction:
                        model.reactions.get_by_id(rxn_info['id']).build_reaction_from_string(rxn_info['equation'])

            # 步骤B: 根据基因准备GPR规则
            rules_to_apply = {(gene_to_rule_map[gene]['reaction_id'], gene_to_rule_map[gene]['gpr']) for gene in
                              owned_genes if gene in gene_to_rule_map}

            # 步骤C: 条件性添加DBP转运反应
            targeted_reaction_ids = {rule[0] for rule in rules_to_apply}
            if {'DBPH1', 'MBPH1', 'DBPH2'}.intersection(targeted_reaction_ids):
                # --- 错误修正 ---
                # 将GPR的设置从Reaction的初始化中分离出来
                if not model.reactions.has_id('DBPHt_e'):
                    print("   -> 步骤C: 条件触发，添加DBP胞外转运反应...")
                    # 1. 先只用ID创建一个基本的Reaction对象
                    rxn = cobra.Reaction('DBPHt_e')
                    # 2. 然后再分别设置它的其他属性
                    rxn.name = 'Dibutyl phthalate transport (Extracellular)'
                    rxn.subsystem = 'DBP degradation transport'
                    rxn.gene_reaction_rule = 'DBPtrans_gene'  # 单独设置GPR
                    # 3. 添加反应并构建方程式
                    model.add_reactions([rxn])
                    rxn.build_reaction_from_string('dbph_e <=> dbph_c')

            # 步骤D: 将所有GPR规则应用到模型中
            print(f"   -> 步骤D: 根据其拥有的基因 {owned_genes} 添加GPR...")
            for reaction_id, gpr_string in rules_to_apply:
                try:
                    reaction = model.reactions.get_by_id(reaction_id)
                    reaction.gene_reaction_rule = gpr_string
                except KeyError:
                    print(f"   [警告] 在模型中未找到反应 '{reaction_id}'，无法添加GPR。")

            # 保存最终模型
            output_filepath = os.path.join(final_output_dir, model_filename)
            cobra.io.write_sbml_model(model, output_filepath)
            print(f"   => 成功保存最终模型至: {output_filepath}")
        except Exception as e:
            print(f"   [错误] 处理模型 '{mag_id}' 时发生意外: {e}")

    print("\n--- 所有MAG处理完毕，脚本成功结束！ ---")


if __name__ == '__main__':
    build_full_pathway_models_final_corrected()