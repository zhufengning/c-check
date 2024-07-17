
from py.c_parser.AST import Node, Variable

class ExtendedVariable(Variable):
    def __init__(self, id, pos, arr=None):
        super().__init__(id, pos, arr)
        self.arr = arr

    def __repr__(self):
        return self.id + (f"[{self.arr.index}]" if self.arr else "") + " " + str(self.pos)

    def get_qualified_name(self, current_function):
        base_name = f"{current_function}.{self.id}"
        if self.arr:
            index_name = self.arr.index if isinstance(self.arr.index, int) else self.arr.index.get_qualified_name(current_function)
            return f"{base_name}[{index_name}]"
        return base_name

class Array(Node):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return f"Array[{self.index}]"

    def get_qualified_name(self, current_function):
        return str(self.index)
