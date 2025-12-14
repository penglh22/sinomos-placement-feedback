class DecisionTree:
    def __init__(self):
        self.root = None

    class Node:
        def __init__(self, value):
            self.value = value
            self.children = []

    def add_node(self, parent_value, child_value):
        parent_node = self._find_node(self.root, parent_value)
        if parent_node is not None:
            new_node = self.Node(child_value)
            parent_node.children.append(new_node)

    def _find_node(self, current_node, value):
        if current_node is None:
            return None
        if current_node.value == value:
            return current_node
        for child in current_node.children:
            result = self._find_node(child, value)
            if result is not None:
                return result
        return None

    def get_children(self, value):
        node = self._find_node(self.root, value)
        if node is not None:
            return [child.value for child in node.children]
        return []

    def to_layout_format(self):
        # Convert the decision tree structure into a format suitable for layout routing
        layout_data = []
        self._traverse_tree(self.root, layout_data)
        return layout_data

    def _traverse_tree(self, node, layout_data):
        if node is not None:
            layout_data.append(node.value)
            for child in node.children:
                self._traverse_tree(child, layout_data)
