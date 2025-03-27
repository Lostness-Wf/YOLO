import os

def count_py_lines(directory):
    total_lines = 0
    file_line_counts = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        file_line_counts.append((file_path, lines))
                        total_lines += lines
                except Exception as e:
                    print(f"无法读取文件 {file_path}: {e}")

    # 打印每个文件的行数
    for path, lines in file_line_counts:
        print(f"{path}: {lines} 行")

    # 打印总行数
    print(f"\n总代码行数: {total_lines} 行")

# 使用示例
if __name__ == "__main__":
    print(f"代码行数统计：")
    target_dir = r"/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP"
    count_py_lines(target_dir)
