import pandas as pd
import os
import networkx as nx
from itertools import permutations, islice
import json
import re
import csv

# --- 0. 安装依赖库 ---
# pip install python-libsbml networkx pandas

try:
    from libsbml import readSBML
except ImportError:
    print("=" * 80);
    print("❌ 致命错误: 必需的库 'python-libsbml' 未找到。");
    print("请先在您的终端中运行以下命令来安装它:");
    print("pip install python-libsbml networkx pandas");
    print("=" * 80);
    exit()

# --- 1. 参数设置 (已根据您的要求更新) ---
MODELS_DIR = '/Volumes/CC/全球+国内96s/INAP_models'
BIGG_METABOLITES_PATH = '/Volumes/CC/全球+国内96s/INAP 计算表/bigg_models_metabolites.txt'
CACHE_FILE_PATH = '/Volumes/CC/全球+国内96s/INAP 计算表/seed_set_cache.json'
OUTPUT_PTM_FILE = '/Volumes/CC/全球+国内96s/INAP 计算表/Step4_PTM_results.csv'


# --- 2. 核心算法 (无变动) ---
def buildDG(sbml_file_path):
    document = readSBML(sbml_file_path)
    if document.getNumErrors() > 0: pass
    model = document.getModel()
    if model is None: return None
    DG = nx.DiGraph()
    for r in model.getListOfReactions():
        reactants = {i.getSpecies() for i in r.getListOfReactants()}
        products = {j.getSpecies() for j in r.getListOfProducts()}
        for reactant in reactants:
            for product in products: DG.add_edge(reactant, product)
    return DG


def getSeedSet(DG, maxComponentSize=5):
    if DG is None: return set(), set()
    SeedSetConfidence = {}
    for component in nx.weakly_connected_components(DG):
        subgraph = DG.subgraph(component)
        for scc in nx.strongly_connected_components(subgraph):
            scc_list = list(scc)
            if len(scc_list) > maxComponentSize: continue
            is_seed_component = True
            for node in scc_list:
                for pred in DG.predecessors(node):
                    if pred not in scc_list: is_seed_component = False; break
                if not is_seed_component: break
            if is_seed_component:
                confidence = 1.0 / len(scc_list) if scc_list else 1.0
                for node in scc_list: SeedSetConfidence[node] = confidence
    SeedSet = set(SeedSetConfidence.keys())
    nonSeedSet = set(DG.nodes()) - SeedSet
    return SeedSet, nonSeedSet


def get_clean_bigg_id(raw_id):
    cleaned_id = raw_id[2:] if raw_id.startswith('M_') else raw_id
    cleaned_id = re.sub(r'_[a-z0-9]$', '', cleaned_id)
    return cleaned_id


# --- 3. 主执行流程 (内存安全版) ---
def main():
    # --- 步骤A: 加载或计算种子集 ---
    if not os.path.isdir(MODELS_DIR): print(f"❌ 错误: 找不到模型目录 '{MODELS_DIR}'"); return

    # 确保缓存文件所在的目录存在
    cache_dir = os.path.dirname(CACHE_FILE_PATH)
    os.makedirs(cache_dir, exist_ok=True)

    model_data = {}
    if os.path.exists(CACHE_FILE_PATH):
        print(f"✅ 发现缓存文件，正在加载种子集...");
        with open(CACHE_FILE_PATH, 'r') as f:
            cached_data = json.load(f)
            for model_id, data in cached_data.items():
                model_data[model_id] = {'seeds': set(data['seeds']), 'non_seeds': set(data['non_seeds'])}
        print("种子集加载完毕。")
    else:
        print("未找到缓存，将执行完整计算...")
        print(f"\n步骤1: 正在为 '{MODELS_DIR}' 中的所有模型计算种子集...")
        model_files = [f for f in os.listdir(MODELS_DIR) if f.lower().endswith('.xml')]
        for i, filename in enumerate(model_files):
            model_id = os.path.splitext(filename)[0]
            print(f"  处理中 ({i + 1}/{len(model_files)}): {model_id}")
            file_path = os.path.join(MODELS_DIR, filename)
            dg = buildDG(file_path)
            seed_set, non_seed_set = getSeedSet(dg)
            model_data[model_id] = {'seeds': seed_set, 'non_seeds': non_seed_set}
        print("所有模型的种子集计算完成。")
        print(f"正在将计算结果保存到缓存文件 '{os.path.basename(CACHE_FILE_PATH)}'...")
        serializable_data = {mid: {'seeds': list(d['seeds']), 'non_seeds': list(d['non_seeds'])} for mid, d in
                             model_data.items()}
        with open(CACHE_FILE_PATH, 'w') as f:
            json.dump(serializable_data, f, indent=4)
        print("缓存文件已创建。")

    # --- 步骤B: 加载代谢物名称 ---
    if not os.path.exists(BIGG_METABOLITES_PATH): print(
        f"❌ 错误: 找不到BiGG代谢物注释文件 '{BIGG_METABOLITES_PATH}'"); return
    print(f"\n正在加载代谢物名称...");
    bigg_df = pd.read_csv(BIGG_METABOLITES_PATH, sep='\t', header=0, usecols=['universal_bigg_id', 'name'], dtype=str)
    bigg_df.dropna(subset=['universal_bigg_id'], inplace=True)
    metabolite_names = pd.Series(bigg_df.name.values, index=bigg_df.universal_bigg_id).to_dict()
    print(f"  ✅ 成功加载 {len(metabolite_names)} 个代谢物名称。")

    # --- 步骤C: 流式处理和写入 ---
    print("\n步骤2: 正在比较模型配对并直接写入文件 (内存安全模式)...")

    # 确保输出目录存在
    output_dir = os.path.dirname(OUTPUT_PTM_FILE)
    os.makedirs(output_dir, exist_ok=True)

    total_pairs = len(model_data) * (len(model_data) - 1)
    processed_count = 0
    ptm_found_count = 0

    with open(OUTPUT_PTM_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Donor', 'Receptor', 'PTM_ID', 'PTM_Name'])

        for donor_id, receptor_id in permutations(model_data.keys(), 2):
            ptms = model_data[donor_id]['seeds'].intersection(model_data[receptor_id]['non_seeds'])

            if ptms:
                for ptm in ptms:
                    cleaned_id = get_clean_bigg_id(ptm)
                    name = metabolite_names.get(cleaned_id)
                    writer.writerow([donor_id, receptor_id, ptm, name if name else 'N/A'])
                    ptm_found_count += 1

            processed_count += 1
            if processed_count % 100000 == 0:
                print(f"  已处理 {processed_count} / {total_pairs} 个配对...")

    print(f"\n步骤3: 所有配对处理完毕。")
    print("\n" + "=" * 50)
    print("🎉 全部任务完成！")
    print(f"共找到并写入 {ptm_found_count} 条潜在转移关系。")
    print(f"详细结果已保存在:\n{OUTPUT_PTM_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()