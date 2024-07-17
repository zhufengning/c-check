import c_parser
from c_parser.AST import Node, Variable, Assignment, Address, Deref, BinExpr, Integer, Float, String, Init, InitList, \
    DeclarationList, FunctionDef, InstructionList, Pointer, Array
import networkx as nx
import matplotlib.pyplot as plt
from c_parser.ply import yacc


class my_Visitor:
    def __init__(self):
        self.graphs = {}
        self.current_function = None
        self.node_dict = {}
        self.global_vars = {}

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node)

    def generic_visit(self, node):
        if not hasattr(node, '__dict__'):
            return
        for field, value in vars(node).items():
            if isinstance(value, Node):
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        self.visit(item)

    def visit_Program(self, node):
        self.visit(node.ext_decls)

    def visit_DeclarationList(self, node):
        for decl in node.decls:
            self.visit(decl)

    def visit_FunctionDefList(self, node):
        for fundef in node.fundefs:
            self.visit(fundef)

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        if self.current_function not in self.graphs:
            self.graphs[self.current_function] = nx.DiGraph()
        self.visit(node.body)
        self.current_function = None

    def visit_CompoundInstructions(self, node):
        self.visit(node.instrs)

    def visit_InstructionList(self, node):
        for instr in node.instrs:
            self.visit(instr)

    def visit_Assignment(self, node):
        lhs = self.get_qualified_name(node.id)
        rhs = self.get_qualified_name(node.expr)
        self.add_edge(rhs, lhs)
        self.visit(node.expr)

    def visit_Declaration(self, node):
        if isinstance(node.inits, InitList):
            for init in node.inits.inits:
                if isinstance(init, Init):
                    lhs = self.get_qualified_name(init.id)
                    rhs = self.get_qualified_name(init.expr)
                    self.add_edge(rhs, lhs)
                    self.visit(init.expr)
        else:
            lhs = self.get_qualified_name(node.id)
            rhs = self.get_qualified_name(node.expr)
            self.add_edge(rhs, lhs)
            self.visit(node.expr)

    def get_qualified_name(self, node):
        if isinstance(node, Variable):
            if self.current_function is None:
                return f"global.{node.id}"
            elif node.arr:
                base_name = f"{self.current_function}.{node.id}[{self.get_qualified_name(node.arr.index)}]"
            else:
                base_name = f"{self.current_function}.{node.id}"
            return base_name
        elif isinstance(node, Integer):
            return str(node.value)
        elif isinstance(node, Float):
            return str(node.value)
        elif isinstance(node, String):
            return str(node.value)
        elif isinstance(node, Address):
            return f"&{self.get_qualified_name(node.var)}"
        elif isinstance(node, Deref):
            return f"*{self.get_qualified_name(node.var)}"
        elif isinstance(node, BinExpr):
            return f"({self.get_qualified_name(node.left)} {node.op} {self.get_qualified_name(node.right)})"
        elif isinstance(node, Pointer):
            return f"*{self.get_qualified_name(node.id)}"
        else:
            return str(node)

    def add_edge(self, src, dst):
        if self.current_function is not None:
            graph = self.graphs[self.current_function]
            if src not in self.node_dict:
                self.node_dict[src] = src
                graph.add_node(src)
            if dst not in self.node_dict:
                self.node_dict[dst] = dst
                graph.add_node(dst)
            graph.add_edge(src, dst, label='=')

    def get_graphs(self):
        return self.graphs


def gen_graph(ast):
    visitor = my_Visitor()
    visitor.visit(ast)
    graphs = visitor.get_graphs()

    for func_name, G in graphs.items():
        plt.figure(figsize=(20, 15))
        pos = nx.spring_layout(G)
        edge_labels = nx.get_edge_attributes(G, 'label')
        filtered_edges = [(u, v) for (u, v, d) in G.edges(data=True) if 'label' in d]
        filtered_edge_labels = {k: edge_labels[k] for k in filtered_edges}

        nx.draw_networkx_edges(G, pos, edgelist=filtered_edges, arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=filtered_edge_labels, font_color='red')
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=16, font_color='black',
                font_weight='bold', arrows=True)
        plt.title(f"Data Flow Graph for function {func_name}")
        plt.savefig("graph.png")
