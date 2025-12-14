import copy
import math
import random


class SimulatedAnnealing:
    def __init__(
        self,
        initial_layout,
        initial_temperature=1000,
        cooling_rate=0.95,
        min_temperature=1,
    ):
        self.current_layout = initial_layout
        self.best_layout = copy.deepcopy(initial_layout)
        self.temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature

    def optimize(self, iterations=1000):
        """执行模拟退火优化"""
        print(f"开始优化，初始成本: {self.current_layout.get_cost():.2f}")

        for i in range(iterations):
            # 生成邻居解
            new_layout = self.current_layout.generate_neighbor()

            current_cost = self.current_layout.get_cost()
            new_cost = new_layout.get_cost()

            # 决定是否接受新解
            if self._acceptance_probability(current_cost, new_cost) > random.random():
                self.current_layout = new_layout

            # 更新最优解
            if new_cost < self.best_layout.get_cost():
                self.best_layout = copy.deepcopy(new_layout)

            # 降温
            self.temperature = max(
                self.min_temperature, self.temperature * self.cooling_rate
            )

            # 打印进度
            if (i + 1) % 100 == 0:
                print(
                    f"迭代 {i + 1}: 当前成本 = {current_cost:.2f}, "
                    f"最优成本 = {self.best_layout.get_cost():.2f}, "
                    f"温度 = {self.temperature:.2f}"
                )

        print(f"优化完成，最终成本: {self.best_layout.get_cost():.2f}")
        return self.best_layout

    def _acceptance_probability(self, current_cost, new_cost):
        """计算接受概率"""
        if new_cost < current_cost:
            return 1.0
        else:
            if self.temperature <= 0:
                return 0.0
            return math.exp((current_cost - new_cost) / self.temperature)
