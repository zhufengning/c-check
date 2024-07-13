import c_parser.ply.yacc as yacc
from c_parser import AST, cparser

cparser = cparser.Cparser()
parser = yacc.yacc(module=cparser)
source1 = (
    """#include <stdio.h>
#define a 2
int ga, gb, gc;

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
  }
}
int fff(){}
int gy;
""",
)

source2 = """#include "dir/dir2/d2.h";
void lib_fun() {
  int x;
  x = x+1;
}
"""

ast = parser.parse(
    source2,
    lexer=cparser.scanner,
)

from c_parser.DFSVisitor import DFSVisitorWithDepth


class MyVisitor(DFSVisitorWithDepth):
    def fn(self, node, depth):
        match type(node):
            case AST.Declaration:
                print(depth, node)


MyVisitor().visit(ast)
