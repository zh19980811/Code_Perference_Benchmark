import re
import numpy as np
from fastdtw import fastdtw
import matplotlib.pyplot as plt

# 空行 KL 散度
def compute_kl_divergence_dtw(code1, code2):
    from scipy.stats import entropy
    from fastdtw import fastdtw
    import numpy as np
    seq1 = [1 if not line.strip() else 0 for line in code1.splitlines()]
    seq2 = [1 if not line.strip() else 0 for line in code2.splitlines()]
    _, path = fastdtw(seq1, seq2, dist=lambda x, y: abs(x - y))
    aligned_seq1 = [seq1[i] for i, _ in path]
    aligned_seq2 = [seq2[j] for _, j in path]
    p1 = np.bincount(aligned_seq1, minlength=2) / len(aligned_seq1)
    p2 = np.bincount(aligned_seq2, minlength=2) / len(aligned_seq2)
    kl_div = entropy(p1 + 1e-10, p2 + 1e-10)
    return round(kl_div, 4)

# 空格 KL 散度
def calculate_kl_divergence_dtw(code1, code2):
    from scipy.stats import entropy
    from fastdtw import fastdtw
    import numpy as np
    import re

    def analyze_space_distribution(code):
        lines = code.splitlines()
        space_counts = []
        for line in lines:
            spaces = [len(match.group()) for match in re.finditer(r' +', line)]
            space_counts.append(spaces)
        mean_spaces = [np.mean(spaces) if spaces else 0 for spaces in space_counts]
        return mean_spaces

    seq1 = analyze_space_distribution(code1)
    seq2 = analyze_space_distribution(code2)
    _, path = fastdtw(seq1, seq2, dist=lambda x, y: abs(x - y))
    aligned_seq1 = [seq1[i] for i, _ in path]
    aligned_seq2 = [seq2[j] for _, j in path]
    all_values = np.union1d(aligned_seq1, aligned_seq2)
    counts1 = [aligned_seq1.count(v) for v in all_values]
    counts2 = [aligned_seq2.count(v) for v in all_values]
    prob_dist1 = np.array(counts1) / sum(counts1)
    prob_dist2 = np.array(counts2) / sum(counts2)
    kl_div = entropy(prob_dist1 + 1e-10, prob_dist2 + 1e-10)
    return round(kl_div, 4)

# 每行完整空格分布（0/1序列）表示
def get_space_binary_vector(line, max_len=30):
    vec = ['1' if c == ' ' else '0' for c in line[:max_len]]
    while len(vec) < max_len:
        vec.append('0')
    return ''.join(vec)

def code_to_binary_matrix(code, max_len=30):
    return [get_space_binary_vector(line, max_len) for line in code.splitlines()]

# 计算空行序列（1=空行，0=非空）
def get_empty_line_sequence(code):
    return [1 if not line.strip() else 0 for line in code.splitlines()]

def align_binary_space_matrix(code1, code2, max_len=30):
    mat1 = code_to_binary_matrix(code1, max_len)
    mat2 = code_to_binary_matrix(code2, max_len)

    row_sums1 = [row.count('1') for row in mat1]
    row_sums2 = [row.count('1') for row in mat2]

    _, path = fastdtw(row_sums1, row_sums2, dist=lambda x, y: abs(x - y))

    aligned1 = [mat1[i] for i, _ in path]
    aligned2 = [mat2[j] for _, j in path]
    return aligned1, aligned2

# 计算空行编码对齐

def align_empty_line_sequences(code1, code2):
    seq1 = get_empty_line_sequence(code1)
    seq2 = get_empty_line_sequence(code2)
    _, path = fastdtw(seq1, seq2, dist=lambda x, y: abs(x - y))
    aligned1 = [seq1[i] for i, _ in path]
    aligned2 = [seq2[j] for _, j in path]
    return ''.join(map(str, aligned1)), ''.join(map(str, aligned2))

# 可视化编码矩阵（调试用）
def visualize_binary_matrix(matrix, title):
    plt.figure(figsize=(10, len(matrix)*0.3))
    for i, row in enumerate(matrix):
        for j, bit in enumerate(row):
            color = 'black' if bit == '1' else 'white'
            plt.gca().add_patch(plt.Rectangle((j, len(matrix)-1-i), 1, 1, facecolor=color, edgecolor='gray'))
    plt.xlim(0, len(matrix[0]))
    plt.ylim(0, len(matrix))
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# 主函数供 demo 使用
def extract_space_alignment(code1, code2, max_len=30):
    aligned1, aligned2 = align_binary_space_matrix(code1, code2, max_len)
    empty1, empty2 = align_empty_line_sequences(code1, code2)
    return aligned1, aligned2, empty1, empty2

if __name__ == "__main__":
    code1 = '''
def test():

    x = 1
    if x > 0:
        print("Positive")
'''

    code2 = '''
def test():
    if True:

        print("Positive")
'''

    a1, a2, e1, e2 = extract_space_alignment(code1, code2)
    print("✅ Code1 空行:", e1)
    print("✅ Code2 空行:", e2)

    print("\n✅ Code1 空格分布:")
    for row in a1:
        print(row)
    print("\n✅ Code2 空格分布:")
    for row in a2:
        print(row)

    visualize_binary_matrix(a1, "Code 1 空格分布")
    visualize_binary_matrix(a2, "Code 2 空格分布")
