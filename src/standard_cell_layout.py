import numpy as np
import torch
from layout import Layout


class StandardCellLayout(Layout):
    def __init__(self, bdd, area_size=(100, 100), site_width=1.0, row_height=2.0):
        self.site_width = site_width
        self.row_height = row_height
        self.num_rows = int(area_size[1] / row_height)
        self.sites_per_row = int(area_size[0] / site_width)

        # 调用父类构造函数
        super().__init__(bdd, area_size)

        # 重新初始化位置，考虑行约束
        self.initialize_with_row_constraints()

    def initialize_with_row_constraints(self):
        """初始化时考虑标准行约束"""
        num_transistors = self.bdd.get_transistor_count()

        for i in range(num_transistors):
            # 随机选择一行
            row_id = np.random.randint(0, self.num_rows)
            # 随机选择该行的一个位置
            site_id = np.random.randint(0, self.sites_per_row)

            # 计算实际坐标
            x = site_id * self.site_width
            y = row_id * self.row_height

            self.transistor_positions[i] = (x, y)

        # 使用曼哈顿距离计算线长
        self.wire_length = self.calculate_manhattan_wire_length()

    def generate_neighbor(self):
        """生成邻居解时考虑行约束"""
        new_layout = StandardCellLayout(
            self.bdd, self.area_size, self.site_width, self.row_height
        )
        new_layout.transistor_positions = self.transistor_positions.copy()

        # 随机选择一个晶体管
        transistor_id = np.random.choice(list(self.transistor_positions.keys()))
        current_pos = self.transistor_positions[transistor_id]

        # 当前位置对应的行和列
        current_row = int(current_pos[1] / self.row_height)
        current_site = int(current_pos[0] / self.site_width)

        # 生成新位置（考虑行约束）
        move_type = np.random.choice(["same_row", "different_row", "adjacent_site"])

        if move_type == "same_row":
            # 同一行内移动
            new_site = max(
                0, min(self.sites_per_row - 1, current_site + np.random.randint(-5, 6))
            )
            new_x = new_site * self.site_width
            new_y = current_row * self.row_height

        elif move_type == "different_row":
            # 移动到不同行
            new_row = np.random.randint(0, self.num_rows)
            new_site = np.random.randint(0, self.sites_per_row)
            new_x = new_site * self.site_width
            new_y = new_row * self.row_height

        else:  # adjacent_site
            # 移动到相邻位置
            dx = np.random.choice([-1, 0, 1])
            dy = np.random.choice([-1, 0, 1])

            new_row = max(0, min(self.num_rows - 1, current_row + dy))
            new_site = max(0, min(self.sites_per_row - 1, current_site + dx))

            new_x = new_site * self.site_width
            new_y = new_row * self.row_height

        new_layout.transistor_positions[transistor_id] = (new_x, new_y)
        new_layout.wire_length = new_layout.calculate_manhattan_wire_length()

        return new_layout

    def legalize_position(self, x, y):
        """将位置合法化到最近的标准行和位点"""
        # 对齐到最近的行
        legal_row = round(y / self.row_height)
        legal_row = max(0, min(self.num_rows - 1, legal_row))

        # 对齐到最近的位点
        legal_site = round(x / self.site_width)
        legal_site = max(0, min(self.sites_per_row - 1, legal_site))

        return legal_site * self.site_width, legal_row * self.row_height

    def check_legality(self):
        """检查布局的合法性"""
        for tid, (x, y) in self.transistor_positions.items():
            # 检查是否在标准行上
            if abs(y % self.row_height) > 1e-6:
                return False, f"晶体管 {tid} 不在标准行上"

            # 检查是否在标准位点上
            if abs(x % self.site_width) > 1e-6:
                return False, f"晶体管 {tid} 不在标准位点上"

            # 检查是否在布局区域内
            if x < 0 or x >= self.area_size[0] or y < 0 or y >= self.area_size[1]:
                return False, f"晶体管 {tid} 超出布局区域"

        return True, "布局合法"

    def get_row_utilization(self):
        """计算每行的利用率"""
        row_utilization = np.zeros(self.num_rows)

        for tid, (x, y) in self.transistor_positions.items():
            row_id = int(y / self.row_height)
            row_utilization[row_id] += 1

        return row_utilization / self.sites_per_row

    def print_layout(self):
        """打印布局信息（包括行信息）"""
        print(f"曼哈顿距离线长: {self.wire_length:.2f}")
        hpwl = self.calculate_half_perimeter_wire_length()
        print(f"半周线长 (对比): {hpwl:.2f}")
        print(
            f"线长比率 (Manhattan/HPWL): {self.wire_length / hpwl:.2f}"
            if hpwl > 0
            else "半周线长为0"
        )
        print(f"标准行数: {self.num_rows}")
        print(f"每行位点数: {self.sites_per_row}")

        # 检查合法性
        legal, msg = self.check_legality()
        print(f"布局合法性: {msg}")

        # 打印行利用率
        row_util = self.get_row_utilization()
        print(f"平均行利用率: {np.mean(row_util):.2f}")
        print(f"最大行利用率: {np.max(row_util):.2f}")

        print("晶体管位置:")
        for tid, pos in sorted(self.transistor_positions.items()):
            row_id = int(pos[1] / self.row_height)
            site_id = int(pos[0] / self.site_width)
            print(
                f"  T{tid}: ({pos[0]:.2f}, {pos[1]:.2f}) [Row{row_id}, Site{site_id}]"
            )
