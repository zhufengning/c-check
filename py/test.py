import c_parser
import c_parser.ply.yacc as yacc

cparser = c_parser.Cparser.Cparser()
parser = yacc.yacc(module=cparser)
ast = parser.parse(
    """#include <stdio.h>
#define a 2
int f() {
  f();
  return 1;
}
int main() {
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
