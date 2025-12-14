import os
import random
import sys

from bdd import BDD
from enhanced_simulated_annealing import EnhancedSimulatedAnnealing
from layout import SingleRowLayout


def create_sample_bsd_file(filename):
    """创建示例BSD文件"""
    content = """[(0,1),(2,2)]
[(-2,0),(0,-1),(0,0)]
[(-2,-1)]
[1,2,0]
"""

    with open(filename, "w") as f:
        f.write(content)
    print(f"创建示例BSD文件: {filename}")
    print("BSD结构说明:")
    print("  第0层: [(0,1)] - 1个晶体管，缓冲器连接到第1层节点1")
    print("  第1层: [(0,1),(2,3)] - 2个晶体管")
    print("    - T1: 缓冲器，连接到第2层节点1")
    print("    - T2: 多路选择器，左分支→第2层节点2，右分支→第2层节点3")
    print("  第2层: [(-2,0),(1,-1),(2,3)] - 3个晶体管")
    print("    - T3: 多路选择器，左分支→输出1，右分支→第3层节点0")
    print("    - T4: 多路选择器，左分支→第3层节点1，右分支→输出0")
    print("    - T5: 多路选择器，左分支→第3层节点2，右分支→第3层节点3")
    print("  第3层: [(-2,-1)],[(-2,-1)],[(-2,-1)],[(-2,-1)] - 4个叶子节点")
    print("    - T6,T7,T8,T9: 叶子节点，直接输出到OUTPUT_1")
    print("  变量序列: [0,2,1,4] - 各层的控制变量")
    print("  注意: 第3层的[(-2,-1)]是叶子节点，不再有分支，直接输出")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main_enhanced.py <bsd_file_path> [w_wire] [w_area]")
        print("  <bsd_file_path>: BDD结构文件路径, 或 '--sample' 创建示例文件。")
        print("  [w_wire]: (可选) 线长成本权重, 默认为 0.5。")
        print("  [w_area]: (可选) 面积成本权重, 默认为 0.5。")
        return

    if sys.argv[1] == "--sample":
        bsd_file = "sample.bsd"
        create_sample_bsd_file(bsd_file)
    else:
        bsd_file = sys.argv[1]
        if not os.path.exists(bsd_file):
            print(f"Error: {bsd_file} not exists.")
            return

    w_wire = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    w_area = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    if abs((w_wire + w_area) - 1.0) > 1e-6:
        print("Warning: 权重之和不为1.0，可能会产生非预期的优化结果。")

    try:
        print("=" * 50)
        print(f"1. 解析BSD文件: {os.path.basename(bsd_file)}")
        print("=" * 50)
        bdd = BDD()
        bdd.construct_from_bsd(bsd_file)
        bdd.analyze_structure()

        print("\n" + "=" * 50)
        print("2. 初始化单行布局")
        print("=" * 50)
        initial_layout = SingleRowLayout(bdd, w_wire, w_area)
        print(f"成本权重: 线长={w_wire}, 面积={w_area}")
        print("初始随机布局顺序:")
        print(initial_layout.placement)

        print("\n" + "=" * 50)
        print("3. 执行增强的模拟退火优化")
        print("=" * 50)
        sa = EnhancedSimulatedAnnealing(
            initial_layout=initial_layout,
            initial_temperature=1000,
            cooling_rate=0.95,
            min_temperature=1,
        )
        optimized_layout = sa.optimize(iterations=5000)

        print("\n" + "=" * 50)
        print("4. 优化结果")
        print("=" * 50)
        print("优化后布局顺序:")
        print(optimized_layout.placement)
        analyze_and_save_results(
            initial_layout, optimized_layout, "enhanced_single_row_results.txt"
        )

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()


def analyze_and_save_results(initial_layout, optimized_layout, filename):
    """分析并保存单行布局的优化结果"""

    initial_wire_cost = initial_layout.calculate_wire_length()
    initial_area_cost = initial_layout.calculate_area_cost()
    initial_total_cost = initial_layout.get_cost()
    num_transistors = len(initial_layout.transistors)
    initial_shared_pairs = num_transistors - initial_area_cost

    final_wire_cost = optimized_layout.calculate_wire_length()
    final_area_cost = optimized_layout.calculate_area_cost()
    final_total_cost = optimized_layout.get_cost()
    final_shared_pairs = num_transistors - final_area_cost

    wire_improvement = (
        (initial_wire_cost - final_wire_cost) / initial_wire_cost * 100
        if initial_wire_cost > 0
        else 0
    )
    area_improvement = (
        (initial_area_cost - final_area_cost) / initial_area_cost * 100
        if initial_area_cost > 0
        else 0
    )

    print("\n--- 布局质量分析 ---")
    print(f"指标              | {'初始布局':<15} | {'优化后布局':<15} | {'改善率':<10}")
    print("-" * 65)
    print(
        f"总加权成本        | {initial_total_cost:<15.2f} | {final_total_cost:<15.2f} |"
    )
    print(
        f"线长 (HPWL)       | {initial_wire_cost:<15.2f} | {final_wire_cost:<15.2f} | {wire_improvement:>8.1f}%"
    )
    print(
        f"面积成本          | {initial_area_cost:<15.2f} | {final_area_cost:<15.2f} | {area_improvement:>8.1f}%"
    )
    print(
        f"可共享扩散区对数  | {initial_shared_pairs:<15} | {final_shared_pairs:<15} |"
    )
    print("-" * 65)

    with open(filename, "w") as f:
        f.write("单行布局优化结果 (线长 + 面积)\n")
        f.write("=" * 60 + "\n")
        f.write(
            f"成本权重: 线长(w_wire)={initial_layout.w_wire}, 面积(w_area)={initial_layout.w_area}\n\n"
        )

        f.write("初始布局顺序:\n")
        f.write(str(initial_layout.placement) + "\n")
        f.write(f"  - 总加权成本: {initial_total_cost:.2f}\n")
        f.write(f"  - 线长成本: {initial_wire_cost:.2f}\n")
        f.write(
            f"  - 面积成本: {initial_area_cost:.2f} (可共享扩散区对数: {initial_shared_pairs})\n\n"
        )

        f.write("优化后布局顺序:\n")
        f.write(str(optimized_layout.placement) + "\n")
        f.write(f"  - 总加权成本: {final_total_cost:.2f}\n")
        f.write(f"  - 线长成本: {final_wire_cost:.2f}\n")
        f.write(
            f"  - 面积成本: {final_area_cost:.2f} (可共享扩散区对数: {final_shared_pairs})\n\n"
        )

        f.write("优化改善率:\n")
        f.write(f"  - 线长改善率: {wire_improvement:.1f}%\n")
        f.write(f"  - 面积成本改善率: {area_improvement:.1f}%\n")
        f.write(
            f"  - 扩散区共享对数增加: {final_shared_pairs - initial_shared_pairs}\n"
        )

    print(f"详细结果已保存到: {filename}")


if __name__ == "__main__":
    main()
