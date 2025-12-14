import copy
import math
import random

from standard_cell_layout import StandardCellLayout


class EnhancedSimulatedAnnealing:
    def __init__(
        self, initial_layout, initial_temperature, cooling_rate, min_temperature
    ):
        self.current_layout = initial_layout
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.best_layout = initial_layout
        self.cost_history = []

    def optimize(self, iterations):
        temperature = self.initial_temperature
        current_cost = self.current_layout.get_cost()
        self.best_layout = self.current_layout
        best_cost = current_cost

        print(f"开始优化，初始成本: {current_cost:.2f}")

        for i in range(iterations):
            # --- FIX START ---
            # 修复: SingleRowLayout 类中的方法名为 get_neighbor, 而不是 generate_neighbor
            neighbor_layout = self.current_layout.get_neighbor()
            # --- FIX END ---

            neighbor_cost = neighbor_layout.get_cost()

            cost_delta = neighbor_cost - current_cost

            if cost_delta < 0 or random.uniform(0, 1) < math.exp(
                -cost_delta / temperature
            ):
                self.current_layout = neighbor_layout
                current_cost = neighbor_cost

                if current_cost < best_cost:
                    self.best_layout = self.current_layout
                    best_cost = current_cost

            self.cost_history.append(current_cost)
            temperature *= self.cooling_rate

            if temperature < self.min_temperature:
                print("温度达到下限，提前结束优化。")
                break

        print(f"优化完成，最终成本: {best_cost:.2f}")
        return self.best_layout
