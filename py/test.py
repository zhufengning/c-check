from c_parser import CParser

ast = CParser().parse(
    """int main(){
int x = 1;
int y = x;
int a = 0;
int b = a + x;
int c = y+b;
int d = y;
}
"""
)

from v_graph import make_graph

print(make_graph(ast))
