#!/usr/bin/env python3
import os
import sys

from bdd import BDD
from layout import Layout
from simulated_annealing import SimulatedAnnealing


def create_sample_bsd_file(filename):
    """创建示例BSD文件"""
    content = """[(0,1)]
[(0,1),(2,3)]
[(-2,0),(1,-1),(2,3)]
[(-2,-1)],[(-2,-1)],[(-2,-1)],[(-2,-1)]
[0,2,1,4]"""

    with open(filename, "w") as f:
        f.write(content)
    print(f"创建示例BSD文件: {filename}")
    print("BSD结构说明:")
    print("  这是一个4层的二元决策图（BDD）")
    print("  每个节点包含左右两个晶体管:")
    print("  第0层: [(0,1)] - 1个节点 = 2个晶体管")
    print("    - T0: 左分支，var_0=0时导通，连接到第1层节点0")
    print("    - T1: 右分支，var_0=1时导通，连接到第1层节点1")
    print("  第1层: [(0,1),(2,3)] - 2个节点 = 4个晶体管")
    print("    - 节点0: T2(左,连接2-0), T3(右,连接2-1)")
    print("    - 节点1: T4(左,连接2-2), T5(右,连接2-3)")
    print("  第2层: [(-2,0),(1,-1),(2,3)] - 3个节点 = 6个晶体管")
    print("    - 节点0: T6(左,输出1), T7(右,连接3-0)")
    print("    - 节点1: T8(左,连接3-1), T9(右,输出0)")
    print("    - 节点2: T10(左,连接3-2), T11(右,连接3-3)")
    print("  第3层: [(-2,-1)]×4 - 4个节点 = 8个晶体管")
    print("    - 每个节点: 左分支输出1，右分支输出0")
    print("  变量序列: [0,2,1,4] - 决策变量的编号")
    print("  总晶体管数: 2 + 4 + 6 + 8 = 20个")


def analyze_layout_quality(initial_layout, optimized_layout):
    """分析布局质量"""
    print("初始布局质量:")
    initial_hpwl = initial_layout.calculate_half_perimeter_wire_length()
    initial_manhattan = initial_layout.calculate_manhattan_wire_length()
    print(f"  半周线长: {initial_hpwl:.2f}")
    print(f"  曼哈顿距离线长: {initial_manhattan:.2f}")
    if initial_hpwl > 0:
        print(f"  Manhattan/HPWL比率: {initial_manhattan / initial_hpwl:.2f}")

    # 显示叶子节点信息
    bdd = initial_layout.bdd
    leaf_transistors = bdd.get_leaf_transistors()
    print(f"  叶子节点数量: {len(leaf_transistors)}")

    print("\n优化后布局质量:")
    final_hpwl = optimized_layout.calculate_half_perimeter_wire_length()
    final_manhattan = optimized_layout.calculate_manhattan_wire_length()
    print(f"  半周线长: {final_hpwl:.2f}")
    print(f"  曼哈顿距离线长: {final_manhattan:.2f}")
    if final_hpwl > 0:
        print(f"  Manhattan/HPWL比率: {final_manhattan / final_hpwl:.2f}")

    print(f"\n改善情况:")
    manhattan_improvement = (
        (initial_manhattan - final_manhattan) / initial_manhattan * 100
    )
    if initial_hpwl > 0 and final_hpwl > 0:
        hpwl_improvement = (initial_hpwl - final_hpwl) / initial_hpwl * 100
        print(f"  半周线长改善: {hpwl_improvement:.1f}%")
    print(f"  曼哈顿距离线长改善: {manhattan_improvement:.1f}%")


def save_results(initial_layout, optimized_layout, filename):
    """保存优化结果到文件"""
    with open(filename, "w") as f:
        f.write("BSD布局优化结果\n")
        f.write("=" * 50 + "\n\n")

        f.write("初始布局:\n")
        f.write(f"半周线长: {initial_layout.get_cost():.2f}\n")
        f.write("晶体管位置:\n")
        for tid, pos in initial_layout.transistor_positions.items():
            f.write(f"  T{tid}: ({pos[0]:.2f}, {pos[1]:.2f})\n")

        f.write("\n优化后布局:\n")
        f.write(f"半周线长: {optimized_layout.get_cost():.2f}\n")
        f.write("晶体管位置:\n")
        for tid, pos in optimized_layout.transistor_positions.items():
            f.write(f"  T{tid}: ({pos[0]:.2f}, {pos[1]:.2f})\n")

        improvement = (
            (initial_layout.get_cost() - optimized_layout.get_cost())
            / initial_layout.get_cost()
            * 100
        )
        f.write(f"\n改善率: {improvement:.1f}%\n")

    print(f"结果已保存到: {filename}")


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <bsd_file_path>")
        print("或者: python main.py --demo  # 使用示例文件")
        return

    if sys.argv[1] == "--demo":
        bsd_file = "sample.bsd"
        create_sample_bsd_file(bsd_file)
    else:
        bsd_file = sys.argv[1]
        if not os.path.exists(bsd_file):
            print(f"错误: 文件 {bsd_file} 不存在")
            return

    try:
        # 1. 解析BSD文件并构建BDD
        print("=" * 50)
        print("1. 解析BSD文件")
        print("=" * 50)
        bdd = BDD()
        bdd.construct_from_bsd(bsd_file)

        # 显示BDD结构分析
        bdd.analyze_structure()

        # 验证结构
        print("\n" + "=" * 50)
        print("2. 结构验证")
        print("=" * 50)
        bdd.validate_structure()

        print("\n" + "=" * 50)
        print("3. 晶体管详细信息")
        print("=" * 50)
        bdd.print_transistor_info()

        print("=" * 50)
        print("4. 网络详细信息")
        print("=" * 50)
        bdd.print_net_info()

        # 2. 初始化布局
        print("\n" + "=" * 50)
        print("5. 初始化随机布局")
        print("=" * 50)
        initial_layout = Layout(bdd, area_size=(100, 100))

        print("初始布局:")
        initial_layout.print_layout()

        # 3. 执行模拟退火优化
        print("\n" + "=" * 50)
        print("6. 执行模拟退火优化")
        print("=" * 50)

        sa = SimulatedAnnealing(
            initial_layout=initial_layout,
            initial_temperature=1000,
            cooling_rate=0.95,
            min_temperature=1,
        )

        optimized_layout = sa.optimize(iterations=1000)

        # 4. 输出结果
        print("\n" + "=" * 50)
        print("7. 优化结果")
        print("=" * 50)

        print("优化后布局:")
        optimized_layout.print_layout()

        # 5. 布局质量分析
        print("\n" + "=" * 50)
        print("8. 布局质量分析")
        print("=" * 50)
        analyze_layout_quality(initial_layout, optimized_layout)

        # 6. 保存结果
        save_results(initial_layout, optimized_layout, "results.txt")

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
