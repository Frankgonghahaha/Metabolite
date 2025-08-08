import os
import subprocess
import sys
import concurrent.futures

# --- 1. 用户配置区 ---
CDS_DIR = "/Volumes/CC/6042MAG数据库文件/全部MAG_CDS文件"
GENE_DIR = "/Volumes/CC/6042MAG数据库文件/功能基因序列"
OUTPUT_DIR = "/Volumes/CC/6042MAG数据库文件/blast_results"

try:
    NUM_THREADS = os.cpu_count()
    print(f"检测到CPU核心数: {NUM_THREADS}，将作为默认线程数。")
except NotImplementedError:
    NUM_THREADS = 8
    print("无法检测到CPU核心数，将使用默认线程数: 4。")

EVALUE_THRESHOLD = 1e-5
IDENTITY_THRESHOLD = 50.0
MIN_ALIGNMENT_LENGTH = 50


# --- 2. 脚本执行区 ---

def setup_directories(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"结果将保存在: {output_dir}")


def run_single_blast_job(query_path, subject_path):
    """
    (已修复) 执行单次BLASTp比对任务。
    """
    cmd = [
        "blastp",
        "-query", query_path,
        "-subject", subject_path,
        "-outfmt", "6 pident length",
        "-evalue", str(EVALUE_THRESHOLD),
        "-max_target_seqs", "1",
        "-task", "blastp-fast"
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)

        # --- !! 关键修复 !! ---
        # 不再假设只有一行输出，而是逐行进行处理
        # 这样可以正确处理有多个HSPs的情况
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue  # 跳过空行

            parts = line.split('\t')
            # 增加一个检查，确保分割后的部分是两个
            if len(parts) != 2:
                continue

            identity = float(parts[0])
            alignment_length = int(parts[1])

            if identity >= IDENTITY_THRESHOLD and alignment_length >= MIN_ALIGNMENT_LENGTH:
                return True  # 只要找到任何一个满足条件的行，就立即返回True

        # 如果所有行都不满足条件，则返回False
        return False

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


# 后续的主函数 run_parallel_blast 和 __main__ 部分无需任何修改
def run_parallel_blast(cds_dir, gene_dir, output_dir, num_threads):
    print("\n--- 开始执行(已修复版)并行的遍历比对 ---")

    try:
        gene_files = [f for f in os.listdir(gene_dir) if f.endswith(".fasta")]
        mag_files = [f for f in os.listdir(cds_dir) if f.endswith("_prodigal.aa")]
    except FileNotFoundError as e:
        print(f"错误: 找不到目录, 请检查路径配置。 {e}")
        sys.exit(1)

    if not gene_files or not mag_files:
        print("警告: 基因目录或CDS目录为空，无法执行比对。")
        return

    for gene_file in gene_files:
        gene_name = os.path.splitext(gene_file)[0]
        query_path = os.path.join(gene_dir, gene_file)
        output_csv_path = os.path.join(output_dir, f"{gene_name}.csv")

        print(f"\n正在处理基因: {gene_name} (使用 {num_threads} 个线程)")

        found_mag_ids_for_this_gene = set()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_mag = {}
            for mag_file in mag_files:
                mag_id = mag_file.split("_prodigal.aa")[0]
                subject_path = os.path.join(cds_dir, mag_file)
                future = executor.submit(run_single_blast_job, query_path, subject_path)
                future_to_mag[future] = mag_id

            for future in concurrent.futures.as_completed(future_to_mag):
                mag_id = future_to_mag[future]
                try:
                    hit_found = future.result()
                    if hit_found:
                        print(f"  -> 在 {mag_id} 中找到匹配！")
                        found_mag_ids_for_this_gene.add(mag_id)
                except Exception as exc:
                    print(f"  ! 处理 {mag_id} 时产生了一个错误: {exc}")

        if found_mag_ids_for_this_gene:
            with open(output_csv_path, 'w', newline='') as csvfile:
                for mag_id in sorted(list(found_mag_ids_for_this_gene)):
                    csvfile.write(f"{mag_id}\n")
            print(f"基因'{gene_name}'的比对完成，找到 {len(found_mag_ids_for_this_gene)} 个匹配的MAG。结果已保存。")
        else:
            print(f"基因'{gene_name}'的比对完成，没有找到符合条件的匹配项。")


if __name__ == "__main__":
    setup_directories(OUTPUT_DIR)
    run_parallel_blast(CDS_DIR, GENE_DIR, OUTPUT_DIR, NUM_THREADS)
    print("\n--- 所有分析完成 ---")