import ast


class BDD:
    def __init__(self):
        self.layers = []
        self.var_sequence = []
        self.transistors = []
        self.nets = []

    def construct_from_bsd(self, bsd_file):
        """从BSD文件构建BDD"""
        self.layers, self.var_sequence = self._parse_bsd_file(bsd_file)
        self._build_transistor_network()

    def _parse_bsd_file(self, filepath):
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

    def _build_transistor_network(self):
        """根据BSD结构构建晶体管网络"""
        transistor_id = 0

        for layer_idx, layer in enumerate(self.layers):
            # 每个layer中的每个元素代表一个BDD节点
            for node_idx, node_data in enumerate(layer):
                # 处理不同类型的节点数据
                if isinstance(node_data, tuple) and len(node_data) == 2:
                    # 标准的分支节点 (left_target, right_target)
                    left_target, right_target = node_data

                    # 获取控制变量
                    control_var = (
                        self.var_sequence[layer_idx]
                        if layer_idx < len(self.var_sequence)
                        else None
                    )

                    # 创建左分支晶体管 (当控制变量=0时导通)
                    left_transistor = {
                        "id": transistor_id,
                        "layer": layer_idx,
                        "node": node_idx,
                        "branch": 0,  # 左分支
                        "type": "switch",
                        "source": (layer_idx, node_idx),
                        "target": self._format_target(left_target, layer_idx),
                        "control": control_var,
                        "activation_condition": f"var_{control_var} == 0",
                        "description": f"Switch T{transistor_id}: ({layer_idx},{node_idx}) → {self._format_target(left_target, layer_idx)} when var_{control_var}=0",
                    }
                    self.transistors.append(left_transistor)
                    transistor_id += 1

                    # 创建右分支晶体管 (当控制变量=1时导通)
                    right_transistor = {
                        "id": transistor_id,
                        "layer": layer_idx,
                        "node": node_idx,
                        "branch": 1,  # 右分支
                        "type": "switch",
                        "source": (layer_idx, node_idx),
                        "target": self._format_target(right_target, layer_idx),
                        "control": control_var,
                        "activation_condition": f"var_{control_var} == 1",
                        "description": f"Switch T{transistor_id}: ({layer_idx},{node_idx}) → {self._format_target(right_target, layer_idx)} when var_{control_var}=1",
                    }
                    self.transistors.append(right_transistor)
                    transistor_id += 1

                elif isinstance(node_data, list) and len(node_data) == 1:
                    # 叶子节点 [value] 或 [(-2,-1)]
                    value = node_data[0]

                    if isinstance(value, tuple) and len(value) == 2:
                        # 叶子节点 [(-2,-1)] - 仍然是左右两个晶体管
                        left_output, right_output = value

                        # 获取控制变量
                        control_var = (
                            self.var_sequence[layer_idx]
                            if layer_idx < len(self.var_sequence)
                            else None
                        )

                        # 创建左分支晶体管
                        left_transistor = {
                            "id": transistor_id,
                            "layer": layer_idx,
                            "node": node_idx,
                            "branch": 0,
                            "type": "leaf_switch",
                            "source": (layer_idx, node_idx),
                            "target": self._format_target(left_output, layer_idx),
                            "control": control_var,
                            "activation_condition": f"var_{control_var} == 0",
                            "description": f"LeafSwitch T{transistor_id}: ({layer_idx},{node_idx}) → {self._format_target(left_output, layer_idx)} when var_{control_var}=0",
                        }
                        self.transistors.append(left_transistor)
                        transistor_id += 1

                        # 创建右分支晶体管
                        right_transistor = {
                            "id": transistor_id,
                            "layer": layer_idx,
                            "node": node_idx,
                            "branch": 1,
                            "type": "leaf_switch",
                            "source": (layer_idx, node_idx),
                            "target": self._format_target(right_output, layer_idx),
                            "control": control_var,
                            "activation_condition": f"var_{control_var} == 1",
                            "description": f"LeafSwitch T{transistor_id}: ({layer_idx},{node_idx}) → {self._format_target(right_output, layer_idx)} when var_{control_var}=1",
                        }
                        self.transistors.append(right_transistor)
                        transistor_id += 1
                    else:
                        # 单值叶子节点 [value] - 只有一个晶体管
                        transistor = {
                            "id": transistor_id,
                            "layer": layer_idx,
                            "node": node_idx,
                            "branch": None,
                            "type": "leaf",
                            "source": (layer_idx, node_idx),
                            "target": self._format_target(value, layer_idx),
                            "control": None,
                            "activation_condition": "always",
                            "description": f"Leaf T{transistor_id}: ({layer_idx},{node_idx}) → {self._format_target(value, layer_idx)}",
                        }
                        self.transistors.append(transistor)
                        transistor_id += 1

                else:
                    print(
                        f"警告: 无法识别的节点数据格式: {node_data} (类型: {type(node_data)})"
                    )
                    print(f"  位置: Layer{layer_idx}, Node{node_idx}")

        self._build_nets()

    def _format_target(self, target, layer_idx):
        """格式化目标节点"""
        if target >= 0:
            return (layer_idx + 1, target)
        elif target == -1:
            return "OUTPUT_0"
        elif target == -2:
            return "OUTPUT_1"
        else:
            return f"OUTPUT_{target}"

    def _build_nets(self):
        """构建网络连接"""
        # 网络连接基于节点位置
        node_connections = {}

        for transistor in self.transistors:
            source = transistor["source"]

            # 处理源节点连接
            if source not in node_connections:
                node_connections[source] = []
            node_connections[source].append(transistor["id"])

            # 处理目标节点连接
            target = transistor["target"]
            if isinstance(target, tuple):  # 非终端节点
                if target not in node_connections:
                    node_connections[target] = []
                node_connections[target].append(transistor["id"])

        # 只保留有多个连接的节点作为网络
        self.nets = [
            connections
            for connections in node_connections.values()
            if len(connections) > 1
        ]

    def get_transistor_count(self):
        """获取晶体管数量"""
        return len(self.transistors)

    def get_nets(self):
        """获取网络连接"""
        return self.nets

    def get_transistors(self):
        """获取晶体管信息"""
        return self.transistors

    def print_transistor_info(self):
        """打印晶体管信息（调试用）"""
        print("晶体管信息:")
        for t in self.transistors:
            print(f"  {t['description']}")
            print(f"    类型: {t['type'].upper()}")
            print(f"    位置: Layer{t['layer']}, Node{t['node']}")
            if t["branch"] is not None:
                print(f"    分支: {t['branch']} ({'左' if t['branch'] == 0 else '右'})")
            if t["control"] is not None:
                print(f"    控制变量: var_{t['control']}")
                print(f"    激活条件: {t['activation_condition']}")
            print(f"    目标: {t['target']}")
            print()

    def print_net_info(self):
        """打印网络信息"""
        print("网络连接详情:")
        if not self.nets:
            print("  没有检测到网络连接")
            return

        print(f"  总网络数: {len(self.nets)}")

        # 统计网络大小
        net_sizes = [len(net) for net in self.nets]
        size_counts = {}
        for size in net_sizes:
            size_counts[size] = size_counts.get(size, 0) + 1

        print(f"  网络大小分布: {size_counts}")

        # 只显示前5个网络的详细信息
        print(f"  前5个网络详情:")
        for i, net in enumerate(self.nets[:5]):
            # 显示网络中晶体管的详细信息
            transistor_info = []
            for tid in net:
                if tid < len(self.transistors):
                    transistor = self.transistors[tid]
                    branch_info = (
                        f"L{transistor['branch']}"
                        if transistor["branch"] is not None
                        else "N"
                    )
                    transistor_info.append(
                        f"T{tid}({transistor['type']},{branch_info})"
                    )
                else:
                    transistor_info.append(f"T{tid}(INVALID)")

            print(f"    Net{i}: {', '.join(transistor_info)} (大小: {len(net)})")

        if len(self.nets) > 5:
            print(f"    ... 还有 {len(self.nets) - 5} 个网络")

    def analyze_structure(self):
        """分析BDD结构"""
        # print("BDD结构分析:")
        # print(f"  层数: {len(self.layers)}")
        # print(f"  变量序列: {self.var_sequence}")
        # print(f"  晶体管总数: {self.get_transistor_count()}")
        # print(f"  网络总数: {len(self.get_nets())}")

        # 按层和类型统计晶体管
        layer_stats = {}
        for t in self.transistors:
            layer = t["layer"]
            if layer not in layer_stats:
                layer_stats[layer] = {"switch": 0, "leaf_switch": 0, "leaf": 0}
            layer_stats[layer][t["type"]] += 1

        # print("  各层晶体管统计:")
        for layer, stats in layer_stats.items():
            total = sum(stats.values())
            #print(
            #    f"    Layer{layer}: {total}个晶体管 "
            #    f"({stats['switch']}个开关, {stats['leaf_switch']}个叶子开关, {stats['leaf']}个叶子)"
            #)

        # 显示每层的具体结构
        #print("\n  各层详细结构:")
        for layer_idx, layer in enumerate(self.layers):
            #print(f"    Layer{layer_idx}: {layer}")
            if layer_idx < len(self.var_sequence):
                pass
                #print(f"      控制变量: var_{self.var_sequence[layer_idx]}")
                #print(f"      每个节点产生2个晶体管")

    def validate_structure(self):
        """验证BDD结构的正确性"""
        print("BDD结构验证:")

        # 检查层数和变量序列的关系
        if len(self.layers) > len(self.var_sequence):
            print(
                f"  注意: 层数({len(self.layers)})大于变量序列长度({len(self.var_sequence)})，最后层可能是叶子节点"
            )

        # 检查每层的晶体管数量
        for layer_idx, layer in enumerate(self.layers):
            expected_count = len(layer) * 2  # 每个节点产生2个晶体管
            actual_count = sum(1 for t in self.transistors if t["layer"] == layer_idx)
            if expected_count != actual_count:
                print(
                    f"  错误: Layer{layer_idx}期望{expected_count}个晶体管，实际{actual_count}个"
                )
            else:
                print(f"  ✓ Layer{layer_idx}: {actual_count}个晶体管")

        # 检查目标节点的有效性
        for t in self.transistors:
            target = t["target"]
            if isinstance(target, tuple):
                target_layer, target_node = target
                # 检查目标层是否存在
                if target_layer < len(self.layers):
                    if target_node >= len(self.layers[target_layer]):
                        print(
                            f"  错误: T{t['id']}的目标({target_node})超出Layer{target_layer}范围"
                        )
                else:
                    print(f"  错误: T{t['id']}的目标层({target_layer})不存在")

        # 检查叶子节点
        leaf_count = sum(
            1 for t in self.transistors if t["type"] in ["leaf", "leaf_switch"]
        )
        if leaf_count > 0:
            print(f"  ✓ 发现{leaf_count}个叶子节点晶体管")

        print("  验证完成")

    def get_leaf_transistors(self):
        """获取所有叶子节点晶体管"""
        return [t for t in self.transistors if t["type"] in ["leaf", "leaf_switch"]]

    def get_connection_matrix(self):
        """获取晶体管连接矩阵（用于布局优化）"""
        n = len(self.transistors)
        connection_matrix = [[0] * n for _ in range(n)]

        for net in self.nets:
            # 网络中的每对晶体管都有连接
            for i in range(len(net)):
                for j in range(i + 1, len(net)):
                    tid1, tid2 = net[i], net[j]
                    if tid1 < n and tid2 < n:
                        connection_matrix[tid1][tid2] = 1
                        connection_matrix[tid2][tid1] = 1

        return connection_matrix
