import c_parser
import c_parser.ply.yacc as yacc

cparser = c_parser.cparser.Cparser()
parser = yacc.yacc(module=cparser)
ast = parser.parse(
    """#include <stdio.h>
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
  }
}

""",
    lexer=cparser.scanner,
)

from v_graph import make_graph

print(make_graph(ast))
