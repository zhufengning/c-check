
import os,sys,tempfile,io
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import c_parser.ply.yacc as yacc
from c_parser import AST, cparser
from c_parser.AST import *

class ComplexityAnalyzer:
    def __init__(self, ast,filename:str):
        self.filename=filename
        self.ast = ast
        self.complexity = 0
        self.function_lengths = []
        self.nested_levels = []
        self.current_function_length = 0
        self.current_nested_level = 0
        self.max_current_nested_level = 0

    def analyze(self):
        self.visit(self.ast)
        average_function_length = (
            sum(self.function_lengths) / len(self.function_lengths)
            if self.function_lengths
            else 0
        )
        max_nested_level = max(self.nested_levels) if self.nested_levels else 0

        return {
            "文件名":self.filename,
            "圈复杂度": self.complexity,
            "平均函数长度": average_function_length,
            "最大嵌套": max_nested_level,
        }

    def visit(self, node):
        method_name = "visit_" + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if hasattr(node, "__dict__"):
            for value in node.__dict__.values():
                if isinstance(value, Node):
                    self.visit(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, Node):
                            self.visit(item)

    def visit_FunctionDef(self, node):
        self.current_function_length = 0
        self.current_nested_level = 0
        self.max_current_nested_level = 0
        self.complexity += 1  # Start with one for the function itself

        self.visit(node.body)

        self.function_lengths.append(self.current_function_length)
        self.nested_levels.append(self.max_current_nested_level)

    def visit_ChoiceInstruction(self, node):
        self.complexity += 1
        self.current_nested_level += 1
        self.max_current_nested_level = max(self.max_current_nested_level, self.current_nested_level)
        self.visit(node.cond)
        self.visit(node.ithen)
        if node.ielse:
            self.visit(node.ielse)
        self.current_nested_level -= 1

    def visit_ForInstruction(self, node):
        self.complexity += 1
        self.current_nested_level += 1
        self.max_current_nested_level = max(self.max_current_nested_level, self.current_nested_level)
        self.visit(node.expr1)
        self.visit(node.expr2)
        self.visit(node.expr3)
        self.visit(node.instr)
        self.current_nested_level -= 1

    def visit_WhileInstruction(self, node):
        self.complexity += 1
        self.current_nested_level += 1
        self.max_current_nested_level = max(self.max_current_nested_level, self.current_nested_level)
        self.visit(node.cond)
        self.visit(node.instr)
        self.current_nested_level -= 1

    def visit_InstructionList(self, node):
        for instr in node.instrs:
            self.current_function_length += 1
            self.visit(instr)

    def visit_CompoundInstructions(self, node):
        if isinstance(node.instrs, InstructionList):
            self.visit_InstructionList(node.instrs)
        else:
            for instr in node.instrs:
                self.current_function_length += 1
                self.visit(instr)

    def visit_ReturnInstruction(self, node):
        self.current_function_length += 1
        self.visit(node.expr)

    def visit_BinExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Variable(self, node):
        if node.arr:
            self.visit(node.arr)

    def visit_Const(self, node):
        pass

    def visit_FunctionCall(self, node):
        self.current_function_length += 1
        if isinstance(node.params, ExprList):
            for param in node.params.exprs:
                self.visit(param)
        else:
            for param in node.params:
                self.visit(param)
if __name__ == '__main__':

    cparser = cparser.Cparser()
    parser = yacc.yacc(module=cparser)
    source2 = """#include <stdio.h>
    #define a 2
    int f() {
    f();
    return 1;
    }
    int main() {
    int x = 0;
    int *y = &x;
    int arr[50];
    arr[0] = 1;
    arr[1] = arr[0];
    int a = 0;
    int b;
    b=(a+1)*3;
    printf("%d", a);
    f(a + 2);
    float fuck;
    printf("%lf", fuck);
    while (1) {
    int a=0;
    while(1)
    {
    if(a==0){
    }
    }
    }
    }

    """

    ast = parser.parse(
        source2,
        lexer=cparser.scanner,
    )

    analyzer = ComplexityAnalyzer(ast,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!this.c")
    metrics = analyzer.analyze()
    print(metrics)








