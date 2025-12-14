import ast
import math
import random


def parse_bsd_file(filepath):
    """解析BSD文件，返回层级结构和变量序列"""
    with open(filepath, "r") as file:
        lines = file.readlines()

    layers = []
    for line in lines[:-1]:  # 除了最后一行
        line = line.strip()
        if line:
            # 解析如 [(0,1),(-1,2)] 的格式
            layer_data = ast.literal_eval(line)
            layers.append(layer_data)

    # 最后一行是变量序列
    var_sequence = ast.literal_eval(lines[-1].strip())

    return layers, var_sequence


def generate_random_layout(num_transistors, area_size):
    """生成随机晶体管布局"""
    layout = {}
    for i in range(num_transistors):
        x = random.uniform(0, area_size[0])
        y = random.uniform(0, area_size[1])
        layout[i] = (x, y)
    return layout


def calculate_distance(point1, point2):
    """计算两点间的欧几里得距离"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def calculate_manhattan_distance(point1, point2):
    """计算两点间的曼哈顿距离"""
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def calculate_half_perimeter_wirelength(nets, positions):
    """计算半周线长"""
    total_length = 0
    for net in nets:
        if len(net) < 2:
            continue

        # 找到网络中所有点的坐标
        points = [positions[node] for node in net if node in positions]

        if len(points) < 2:
            continue

        # 计算包围盒
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        # 半周线长 = (width + height)
        total_length += (max_x - min_x) + (max_y - min_y)

    return total_length


def calculate_manhattan_wirelength(nets, positions):
    """计算所有连接节点之间的曼哈顿距离之和"""
    total_length = 0

    for net in nets:
        if len(net) < 2:
            continue

        # 找到网络中所有点的坐标
        points = [(node, positions[node]) for node in net if node in positions]

        if len(points) < 2:
            continue

        # 计算网络中所有节点对之间的曼哈顿距离
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                node1, pos1 = points[i]
                node2, pos2 = points[j]
                manhattan_dist = calculate_manhattan_distance(pos1, pos2)
                total_length += manhattan_dist

    return total_length


def calculate_star_manhattan_wirelength(nets, positions):
    """计算星形连接的曼哈顿距离之和（更接近实际布线）"""
    total_length = 0

    for net in nets:
        if len(net) < 2:
            continue

        # 找到网络中所有点的坐标
        points = [positions[node] for node in net if node in positions]

        if len(points) < 2:
            continue

        # 计算网络的中心点（质心）
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)
        center = (center_x, center_y)

        # 计算所有点到中心点的曼哈顿距离之和
        for point in points:
            manhattan_dist = calculate_manhattan_distance(point, center)
            total_length += manhattan_dist

    return total_length
