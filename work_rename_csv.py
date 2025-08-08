import os

# --- 1. 用户配置区 ---
# 请确认这个路径是您想要操作的文件夹的正确路径
TARGET_DIR = '/Volumes/CC/6042MAG数据库文件/RWMAG_注释文件csv格式'


# --- 2. 脚本执行区 ---

def batch_rename_files(directory):
    """
    批量重命名指定目录下的文件。
    将 $MAG_id_annotations.csv 重命名为 $MAG_id.csv
    """
    print(f"--- 开始扫描目录: {directory} ---")

    # 检查目标目录是否存在
    if not os.path.isdir(directory):
        print(f"错误: 目录不存在, 请检查路径。")
        print(f"路径: {directory}")
        return

    # 获取目录下的所有文件名
    try:
        all_files = os.listdir(directory)
    except OSError as e:
        print(f"错误: 无法访问目录内容。 {e}")
        return

    rename_count = 0
    # 遍历所有文件
    for filename in all_files:
        # 检查文件名是否符合需要重命名的格式
        if filename.endswith('_annotations.csv'):
            # 构建旧的完整路径
            old_path = os.path.join(directory, filename)

            # 构建新的文件名
            new_filename = filename.replace('_annotations.csv', '.csv')

            # 构建新的完整路径
            new_path = os.path.join(directory, new_filename)

            try:
                # 执行重命名操作
                os.rename(old_path, new_path)
                print(f"  已重命名: '{filename}' -> '{new_filename}'")
                rename_count += 1
            except OSError as e:
                print(f"  ! 错误: 无法重命名文件 '{filename}'. 详细信息: {e}")

    if rename_count > 0:
        print(f"\n--- 操作完成！总共重命名了 {rename_count} 个文件。 ---")
    else:
        print("\n--- 操作完成。没有找到符合 `_annotations.csv` 结尾的文件进行重命名。 ---")


# --- 运行主函数 ---
if __name__ == "__main__":
    batch_rename_files(TARGET_DIR)