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


def main():
    if len(sys.argv) < 2:
        return

    if sys.argv[1] == "--sample":
        bsd_file = "sample.bsd"
        create_sample_bsd_file(bsd_file)
    else:
        bsd_file = sys.argv[1]
        if not os.path.exists(bsd_file):
            return

    w_wire = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    w_area = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    if abs((w_wire + w_area) - 1.0) > 1e-6:
        pass

    try:
        bdd = BDD()
        bdd.construct_from_bsd(bsd_file)
        bdd.analyze_structure()

        initial_layout = SingleRowLayout(bdd, w_wire, w_area)

        sa = EnhancedSimulatedAnnealing(
            initial_layout=initial_layout,
            initial_temperature=1000,
            cooling_rate=0.95,
            min_temperature=1,
        )
        optimized_layout = sa.optimize(iterations=5000)

        analyze_and_save_results(
            initial_layout, optimized_layout, "enhanced_single_row_results.txt"
        )

    except Exception as e:
        import traceback


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

    print(f"{final_total_cost}")

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


if __name__ == "__main__":
    main()
