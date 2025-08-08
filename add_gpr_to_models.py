import pandas as pd
import cobra
import os
import re
from collections import defaultdict


def build_full_pathway_models_final():
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

    print("--- 开始执行最终的、完整的模型构建脚本 (Final Version) ---")

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
                print("   -> 步骤C: 条件触发，添加DBP胞外转运反应...")
                if not model.reactions.has_id('DBPHt_e'):
                    rxn = cobra.Reaction('DBPHt_e', name='Dibutyl phthalate transport (Extracellular)',
                                         subsystem='DBP degradation transport', gene_reaction_rule='DBPtrans_gene')
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
    build_full_pathway_models_final()
