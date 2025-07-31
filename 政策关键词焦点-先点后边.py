import csv
import itertools
from collections import defaultdict
import os


def calculate_h_index(values):
    """计算给定列表的h指数"""
    sorted_vals = sorted(values, reverse=True)
    h = 0
    for i, val in enumerate(sorted_vals):
        if val >= i + 1:
            h = i + 1
        else:
            break
    return h


# 读取CSV文件并处理关键词
def process_csv(filename):
    nested_keywords = []
    with open(filename, 'r', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'keywords' in row and row['keywords']:
                # 分割关键词并去除首尾空格
                keywords = [kw.strip() for kw in row['keywords'].split(';')]
                nested_keywords.append(keywords)
    return nested_keywords


# 构建共现网络
def build_co_occurrence_network(nested_keywords):
    co_occurrence = defaultdict(int)
    node_frequency = defaultdict(int)

    for keywords in nested_keywords:
        # 更新节点出现频率
        for kw in set(keywords):  # 每个文档内去重
            node_frequency[kw] += 1

        # 生成两两组合（无重复、无序）
        for pair in itertools.combinations(sorted(set(keywords)), 2):
            # 保持元组有序以便统一表示
            ordered_pair = tuple(sorted(pair))
            co_occurrence[ordered_pair] += 1

    return dict(co_occurrence), dict(node_frequency)


# 计算节点度中心性
def calculate_degree_centrality(co_occurrence):
    degree_centrality = defaultdict(int)
    for (u, v), count in co_occurrence.items():
        degree_centrality[u] += 1
        degree_centrality[v] += 1
    return dict(degree_centrality)


# 第一次h截断（节点级）
def first_h_cut(co_occurrence, degree_centrality):
    degrees = list(degree_centrality.values())
    h_index = calculate_h_index(degrees)

    # 找出需要保留的节点
    keep_nodes = {node for node, deg in degree_centrality.items() if deg >= h_index}

    # 构建新的共现网络（仅保留符合条件的节点）
    new_co_occurrence = {}
    for (u, v), count in co_occurrence.items():
        if u in keep_nodes and v in keep_nodes:
            new_co_occurrence[(u, v)] = count

    return new_co_occurrence, keep_nodes, h_index


# 第二次h截断（边级）
def second_h_cut(co_occurrence):
    weights = list(co_occurrence.values())
    h_index = calculate_h_index(weights)

    # 构建新的共现网络（仅保留符合条件的边）
    new_co_occurrence = {
        pair: count for pair, count in co_occurrence.items() if count >= h_index
    }
    return new_co_occurrence, h_index


# 输出共现关系到CSV
def save_co_occurrence_to_csv(co_occurrence, filename):
    sorted_edges = sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['node1', 'node2', 'weight'])
        for (node1, node2), weight in sorted_edges:
            writer.writerow([node1, node2, weight])


# 输出节点数据到CSV
def save_nodes_to_csv(nodes_data, filename, header):
    sorted_nodes = sorted(nodes_data.items(), key=lambda x: x[1], reverse=True)
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['node', header])
        for node, value in sorted_nodes:
            writer.writerow([node, value])


# 主函数
def main(csv_file):

    # 1. 处理CSV文件
    nested_keywords = process_csv(csv_file)
    print(f"处理文档数: {len(nested_keywords)}")

    # 2. 构建共现网络
    co_occurrence, node_frequency = build_co_occurrence_network(nested_keywords)
    print(f"原始共现关系数量: {len(co_occurrence)}")
    print(f"原始节点数量: {len(node_frequency)}")

    # 3. 计算度中心性
    degree_centrality = calculate_degree_centrality(co_occurrence)

    # 保存原始数据到CSV
    save_co_occurrence_to_csv(co_occurrence, 'E:\edges.csv')
    save_nodes_to_csv(node_frequency, 'E:\odes.csv', 'frequency')
    save_nodes_to_csv(degree_centrality, 'E:\degree.csv', 'degree')
    print("原始数据已保存到output目录")

    # 4. 第一次h截断
    co_occurrence_after_first, keep_nodes, h_node = first_h_cut(co_occurrence, degree_centrality)

    print("\n===== 第一次h截断 =====")
    print(f"节点级h指数: {h_node}")
    print(f"截断后保留边数: {len(co_occurrence_after_first)}")

    # 输出截断后的共现关系
    print("截断后保留的共现关系:")
    sorted_first_cut = sorted(co_occurrence_after_first.items(), key=lambda x: x[1], reverse=True)
    for (node1, node2), weight in sorted_first_cut[:10]:
        print(f"{node1}-{node2}: {weight}")

    # 保存第一次截断结果
    save_co_occurrence_to_csv(co_occurrence_after_first, 'E:\edges_after_first_cut.csv')

    # 5. 第二次h截断
    final_co_occurrence, h_edge = second_h_cut(co_occurrence_after_first)

    print("\n===== 第二次h截断 =====")
    print(f"边权重h指数: {h_edge}")
    print(f"最终保留边数: {len(final_co_occurrence)}")

    # 输出最终的共现关系
    print("最终保留的共现关系:")
    sorted_final_cut = sorted(final_co_occurrence.items(), key=lambda x: x[1], reverse=True)
    for (node1, node2), weight in sorted_final_cut:
        print(f"{node1}-{node2}: {weight}")

    # 保存最终结果
    save_co_occurrence_to_csv(final_co_occurrence, 'E:\edges_after_second_cut.csv')


if __name__ == "__main__":
    csv_file = "E:\hhh.csv"  # 替换为你的CSV文件路径
    main(csv_file)