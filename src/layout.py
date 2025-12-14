import copy
import random

import numpy as np
from utils import calculate_manhattan_wirelength, generate_random_layout


class Layout:
    def __init__(self, bdd, area_size=(100, 100)):
        self.bdd = bdd
        self.area_size = area_size
        self.transistor_positions = {}
        self.wire_length = 0
        self.initialize_random_positions()

    def initialize_random_positions(self):
        """初始化随机晶体管位置"""
        num_transistors = self.bdd.get_transistor_count()
        # 为所有晶体管（包括叶子节点）分配位置
        self.transistor_positions = generate_random_layout(
            num_transistors, self.area_size
        )
        self.wire_length = self.calculate_manhattan_wire_length()

    def calculate_manhattan_wire_length(self, debug=False):
        """计算曼哈顿距离线长"""
        nets = self.bdd.get_nets()
        total_length = 0

        if debug:
            print(f"\n调试信息: 计算曼哈顿距离线长")
            print(f"网络数量: {len(nets)}")

        for net_idx, net in enumerate(nets):
            if len(net) < 2:
                if debug:
                    print(f"  Net{net_idx}: 跳过（只有{len(net)}个晶体管）")
                continue

            # 获取网络中所有晶体管的位置
            positions = []
            for transistor_id in net:
                if transistor_id in self.transistor_positions:
                    positions.append(self.transistor_positions[transistor_id])

            if len(positions) < 2:
                if debug:
                    print(f"  Net{net_idx}: 跳过（只有{len(positions)}个有效位置）")
                continue

            if debug:
                print(f"  Net{net_idx}: 晶体管{net}, 位置{positions}")

            # 计算所有晶体管对之间的曼哈顿距离
            net_length = 0
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    pos1, pos2 = positions[i], positions[j]
                    manhattan_dist = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                    net_length += manhattan_dist
                    if debug:
                        print(
                            f"    T{net[i]} <-> T{net[j]}: {pos1} <-> {pos2} = {manhattan_dist}"
                        )

            if debug:
                print(f"    Net{net_idx}总长度: {net_length}")
            total_length += net_length

        if debug:
            print(f"总曼哈顿距离: {total_length}")
        return total_length

    def calculate_half_perimeter_wire_length(self, debug=False):
        """计算半周线长"""
        nets = self.bdd.get_nets()
        total_length = 0

        if debug:
            print(f"\n调试信息: 计算半周线长")
            print(f"网络数量: {len(nets)}")

        for net_idx, net in enumerate(nets):
            if len(net) < 2:
                if debug:
                    print(f"  Net{net_idx}: 跳过（只有{len(net)}个晶体管）")
                continue

            # 获取网络中所有晶体管的位置
            positions = []
            for transistor_id in net:
                if transistor_id in self.transistor_positions:
                    positions.append(self.transistor_positions[transistor_id])

            if len(positions) < 2:
                if debug:
                    print(f"  Net{net_idx}: 跳过（只有{len(positions)}个有效位置）")
                continue

            if debug:
                print(f"  Net{net_idx}: 晶体管{net}, 位置{positions}")

            # 计算包围盒
            min_x = min(pos[0] for pos in positions)
            max_x = max(pos[0] for pos in positions)
            min_y = min(pos[1] for pos in positions)
            max_y = max(pos[1] for pos in positions)

            # 半周线长
            hpwl = (max_x - min_x) + (max_y - min_y)
            if debug:
                print(f"    包围盒: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
                print(f"    Net{net_idx}半周线长: {hpwl}")
            total_length += hpwl

        if debug:
            print(f"总半周线长: {total_length}")
        return total_length

    def generate_neighbor(self):
        """生成邻居解"""
        new_layout = Layout(self.bdd, self.area_size)
        new_layout.transistor_positions = copy.deepcopy(self.transistor_positions)

        # 随机选择一个晶体管并移动其位置
        if not self.transistor_positions:
            return new_layout

        transistor_id = random.choice(list(self.transistor_positions.keys()))

        # 在当前位置附近生成新位置
        current_pos = self.transistor_positions[transistor_id]
        move_range = min(self.area_size) * 0.1  # 移动范围为区域大小的10%

        new_x = max(
            0,
            min(
                self.area_size[0],
                current_pos[0] + random.uniform(-move_range, move_range),
            ),
        )
        new_y = max(
            0,
            min(
                self.area_size[1],
                current_pos[1] + random.uniform(-move_range, move_range),
            ),
        )

        new_layout.transistor_positions[transistor_id] = (new_x, new_y)
        # 不需要调试信息的快速计算
        new_layout.wire_length = new_layout.calculate_manhattan_wire_length(debug=False)

        return new_layout

    def get_cost(self):
        """获取布局成本 - 使用半周线长"""
        return self.calculate_half_perimeter_wire_length(debug=False)

    def get_layout(self):
        """获取布局信息"""
        return self.transistor_positions, self.wire_length

    def print_layout(self):
        """打印布局信息"""
        # 只在打印时显示调试信息
        manhattan_length = self.calculate_manhattan_wire_length(debug=True)
        hpwl = self.calculate_half_perimeter_wire_length(debug=True)

        print(f"\n线长统计:")
        print(f"  曼哈顿距离线长: {manhattan_length:.2f}")
        print(f"  半周线长 (HPWL): {hpwl:.2f}")

        if hpwl > 0:
            print(f"  线长比率 (Manhattan/HPWL): {manhattan_length / hpwl:.2f}")
        else:
            print("  半周线长为0，无法计算比率")

        # 分析为什么两者相同
        nets = self.bdd.get_nets()
        net_sizes = [len(net) for net in nets if len(net) >= 2]
        size_counts = {}
        for size in net_sizes:
            size_counts[size] = size_counts.get(size, 0) + 1

        print(f"\n网络大小分析:")
        print(f"  有效网络数: {len(net_sizes)}")
        print(f"  网络大小分布: {size_counts}")

        # 如果大部分是2个晶体管的网络，解释为什么线长相同
        if size_counts.get(2, 0) == len(net_sizes):
            print(f"  解释: 所有网络都只有2个晶体管，因此曼哈顿距离 = 半周线长")
        elif size_counts.get(2, 0) > len(net_sizes) * 0.8:
            print(
                f"  解释: {size_counts.get(2, 0)}/{len(net_sizes)}个网络只有2个晶体管，主要影响线长计算"
            )

        # 显示晶体管类型统计
        transistors = self.bdd.get_transistors()
        type_counts = {}
        for t in transistors:
            t_type = t["type"]
            type_counts[t_type] = type_counts.get(t_type, 0) + 1

        print(f"\n晶体管类型统计:")
        for t_type, count in type_counts.items():
            print(f"  {t_type.upper()}: {count}个")

        print(f"\n晶体管位置 (前10个):")
        for tid, pos in sorted(list(self.transistor_positions.items())[:10]):
            # 获取晶体管详细信息
            transistor = next((t for t in transistors if t["id"] == tid), None)
            if transistor:
                print(
                    f"  T{tid} ({transistor['type'].upper()}): ({pos[0]:.2f}, {pos[1]:.2f})"
                )
            else:
                print(f"  T{tid}: ({pos[0]:.2f}, {pos[1]:.2f})")

        if len(self.transistor_positions) > 10:
            print(f"  ... 还有 {len(self.transistor_positions) - 10} 个晶体管")


import random

import numpy as np


class SingleRowLayout:
    """
    表示和评估一个单行的晶体管布局。
    优化目标是线长和面积（通过扩散区共享）的加权和。
    """

    def __init__(self, bdd, w_wire=0.5, w_area=0.5):
        """
        初始化单行布局。
        :param bdd: BDD对象，包含晶体管和网络信息。
        :param w_wire: 线长成本的权重。
        :param w_area: 面积成本的权重。
        """
        self.bdd = bdd
        self.w_wire = w_wire
        self.w_area = w_area

        # bdd.transistors 是一个字典列表，例如 [{'id': 0, ...}, {'id': 1, ...}]
        if isinstance(bdd.transistors, list):
            self.transistor_map = {t["id"]: t for t in bdd.transistors}
            self.transistors = list(self.transistor_map.keys())
        elif isinstance(bdd.transistors, dict):
            self.transistor_map = bdd.transistors
            self.transistors = list(bdd.transistors.keys())
        else:
            raise TypeError(
                f"Unsupported type for bdd.transistors: {type(bdd.transistors)}"
            )

        self.placement = list(self.transistors)
        random.shuffle(self.placement)

        self.pos_map = {
            transistor_id: i for i, transistor_id in enumerate(self.placement)
        }

    def get_cost(self):
        """计算布局的总成本（线长 + 面积）"""
        cost_wire = self.calculate_wire_length()
        cost_area = self.calculate_area_cost()

        total_cost = self.w_wire * cost_wire + self.w_area * cost_area
        return total_cost

    def calculate_wire_length(self):
        """计算总线长（HPWL的1D形式）"""
        total_wire_length = 0
        if not isinstance(self.bdd.nets, list):
            raise TypeError(f"self.bdd.nets is not a list, but {type(self.bdd.nets)}")

        # bdd.nets 是一个列表的列表, e.g., [[pin1, pin2], [pin3, pin4]]
        for net in self.bdd.nets:
            positions = [self.pos_map[pin] for pin in net if pin in self.pos_map]
            if len(positions) > 1:
                total_wire_length += max(positions) - min(positions)
        return total_wire_length

    def calculate_area_cost(self):
        """
        计算面积成本。成本定义为 (总晶体管数 - 可共享扩散区的邻居对数)。
        最小化此成本等同于最大化扩散区共享。
        """
        shared_pairs = 0
        # --- FIX START ---
        # 修复: 不再依赖 'source_net'/'drain_net' 键。
        # 而是检查相邻的两个晶体管是否出现在同一个网络中。
        for i in range(len(self.placement) - 1):
            t1_id = self.placement[i]
            t2_id = self.placement[i + 1]

            # 遍历所有网络，查找是否有网络同时包含 t1_id 和 t2_id
            is_shared = False
            for net in self.bdd.nets:
                # 如果一个网络同时包含这两个相邻的晶体管，则它们可以共享扩散区
                if t1_id in net and t2_id in net:
                    # 排除全局网络（如Vdd/GND），这里假设它们不被列为普通网络
                    # 或者假设共享任何网络都有助于减少面积
                    is_shared = True
                    break  # 找到一个共享网络就足够了

            if is_shared:
                shared_pairs += 1
        # --- FIX END ---

        return len(self.transistors) - shared_pairs

    def get_neighbor(self):
        """
        生成一个新的邻居布局。
        采用随机交换两个晶体管位置的方式。
        """
        new_layout = self.copy()

        if len(new_layout.placement) < 2:
            return new_layout

        i, j = random.sample(range(len(new_layout.placement)), 2)

        t1_id, t2_id = new_layout.placement[i], new_layout.placement[j]
        new_layout.placement[i], new_layout.placement[j] = t2_id, t1_id
        new_layout.pos_map[t1_id], new_layout.pos_map[t2_id] = j, i

        return new_layout

    def copy(self):
        """创建当前布局的深拷贝"""
        new_layout = object.__new__(SingleRowLayout)
        new_layout.bdd = self.bdd
        new_layout.w_wire = self.w_wire
        new_layout.w_area = self.w_area
        new_layout.transistor_map = self.transistor_map
        new_layout.transistors = self.transistors
        new_layout.placement = self.placement[:]
        new_layout.pos_map = self.pos_map.copy()
        return new_layout

    def __str__(self):
        return f"SingleRowLayout(Placement: {self.placement})"
