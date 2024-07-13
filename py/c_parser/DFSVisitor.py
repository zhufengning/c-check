from .AST import Node


class DFSVisitor:
    def __init__(self):
        pass

    def fn(self, node):
        pass

    def visit(self, node):
        if node is None:
            return

        # 执行访问逻辑，这里是将节点加入已访问列表
        self.fn(node)

        # 递归访问子节点
        for attr in vars(node).values():
            if isinstance(attr, list):
                for item in attr:
                    if isinstance(item, Node):
                        self.visit(item)
            elif isinstance(attr, Node):
                self.visit(attr)


class DFSVisitorWithDepth:
    def __init__(self):
        pass

    def fn(self, node, depth):
        pass

    def visit(self, node, depth=0):
        if node is None:
            return

        # 执行访问逻辑，这里是将节点加入已访问列表
        self.fn(node, depth)

        # 递归访问子节点
        for attr in vars(node).values():
            if isinstance(attr, list):
                for item in attr:
                    if isinstance(item, Node):
                        self.visit(item, depth + 1)
            elif isinstance(attr, Node):
                self.visit(attr, depth + 1)
