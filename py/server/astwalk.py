from c_parser import AST

def walk(p: AST.Node):
    print(p)
    match type(p):
        case AST.Program:
            print("program")
