from c_parser import AST


from c_parser.DFSVisitor import DFSVisitorWithDepth


class VarsVisitor(DFSVisitorWithDepth):
    def __init__(self):
        super().__init__()
        self.function = ""
        self.globalv = []
        self.localv = []

    def fn(self, node, depth):
        match type(node):
            case AST.Declaration:
                vs = []
                for i in node.inits.inits:
                    vs.append({"name": i.id, "pos": i.pos})
                if depth == 2:

                    print("global:", node)
                    self.globalv += vs
                else:
                    print("local:", self.function, node)
                    for i in vs:
                        i["fun"] = self.function
                    self.localv += vs
            case AST.FunctionDef:
                self.function = node.name


class FindVarVisitor(DFSVisitorWithDepth):
    def __init__(self, fun, var):
        super().__init__()
        self.target_fun = fun
        self.var = var
        self.results = []

    def fn(self, node, depth):
        match type(node):
            case AST.Declaration:
                if self.target_fun == "" or self.function == self.target_fun:
                    for i in node.inits.inits:
                        if i.id == self.var:
                            self.results.append(i.pos)
            case AST.Variable:
                print(node)
                if (
                    self.target_fun == "" or self.function == self.target_fun
                ) and self.var == node.id:
                    self.results.append(node.pos)
            case AST.FunctionDef:
                self.function = node.name


def getVars(ast):
    print(ast.printTree(0))
    mv = VarsVisitor()
    mv.visit(ast)
    return {"local": mv.localv, "global": mv.globalv}


def findVar(ast, var, fun):
    print(ast.printTree(0))
    fvv = FindVarVisitor(fun, var)
    fvv.visit(ast)
    return fvv.results
