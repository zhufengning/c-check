from c_parser import AST


from c_parser.DFSVisitor import DFSVisitor, DFSVisitorWithDepth


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
                    r = f"{node.type} {i.id}"
                    print(i.expr)
                    if isinstance(i.expr, AST.Array):
                        print("Is Array!")
                        r += f"[{i.expr.index}]"
                        print(r)
                    vs.append(
                        {
                            "name": i.id,
                            "pos": i.pos,
                            "used": False,
                            "repr": r,
                        }
                    )
                if depth == 2:
                    print("global:", node)
                    self.globalv += vs
                else:
                    print("local:", self.function, node)
                    for i in vs:
                        i["fun"] = self.function
                    self.localv += vs
            case AST.Variable:
                localv = self.localv
                globalv = self.globalv
                for i in range(len(localv)):
                    if (
                        localv[i]["name"] == node.id
                        and localv[i]["fun"] == self.function
                    ):
                        localv[i]["used"] = True
                for i in range(len(globalv)):
                    if globalv[i]["name"] == node.id and "fun" not in globalv[i]:
                        globalv[i]["used"] = True
            case AST.FunctionDef:
                self.function = node.name


class VarsVisitor2(DFSVisitorWithDepth):
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
                    r = f"{node.type} {i.id}"
                    print(i.expr)
                    if isinstance(i.expr, AST.Array):
                        print("Is Array!")
                        r += f"[{i.expr.index}]"
                        print(r)

                    vs.append({
                        "Variable Name": r,
                        "Position": i.pos,
                        "Belong Function": "",
                        "used": False,
                    })
                if depth == 2:
                    print("global:", node)
                    self.globalv += vs
                else:
                    print("local:", self.function, node)
                    for i in vs:
                        i["Belong Function"] = self.function
                    self.localv += vs
            case AST.Variable:
                localv = self.localv
                globalv = self.globalv
                for i in range(len(localv)):
                    if (
                        localv[i]["Variable Name"] == node.id
                        and localv[i]["Belong Function"] == self.function
                    ):
                        localv[i]["used"] = True
                for i in range(len(globalv)):
                    if globalv[i]["Variable Name"] == node.id and "Belong Function" not in globalv[i]:
                        globalv[i]["used"] = True
            case AST.FunctionDef:
                self.function = node.name

class FindVarVisitor(DFSVisitorWithDepth):
    def __init__(self, fun, var):
        super().__init__()
        self.target_fun = fun
        self.var = var
        self.results = []
        self.function = ""

    def fn(self, node, depth):
        match type(node):
            case AST.Declaration:
                if self.target_fun == "" or self.function == self.target_fun:
                    for i in node.inits.inits:
                        if i.id == self.var:
                            self.results.append(i.pos)
                        elif isinstance(i.id, AST.Pointer):
                            if i.id.id == self.var:
                                self.results.append(i.pos)
            case AST.Variable:
                print(node)
                if isinstance(node.id, AST.Pointer):
                    if node.id.id == self.var and (
                        self.target_fun == "" or self.function == self.target_fun
                    ):
                        self.results.append(node.pos)
                elif (
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
def getVars2(ast):
    mv = VarsVisitor2()
    mv.visit(ast)
    return mv


def findVar(ast, var, fun):
    print(ast.printTree(0))
    fvv = FindVarVisitor(fun, var)
    fvv.visit(ast)
    return fvv.results


from collections import defaultdict


class FunctionVisitor(DFSVisitorWithDepth):
    def __init__(self):
        self.functions = []
        self.calls = ["main"]
        self.callee = {}

    def fn(self, node, depth):
        match type(node):
            case AST.FunctionDef:
                print(node)
                self.functions.append(
                    {"name": node.name, "used": False, "pos": node.pos}
                )
            case AST.FunctionCall:
                self.calls.append(node.id)
                if node.id not in self.callee:
                    self.callee[node.id] = []
                self.callee[node.id].append({"pos": node.pos})


class MallocVisitor(DFSVisitorWithDepth):
    def __init__(self):
        self.malloced = []
        self.freed = set()
        self.function = ""

    def fn(self, node, depth):
        match type(node):
            case AST.Init:
                if isinstance(node.expr, AST.FunctionCall) and node.expr.id == "malloc":
                    self.malloced.append(
                        {
                            "name": node.id.id,
                            "fun": self.function if depth != 2 else "",
                            "pos": node.pos,
                        }
                    )
            case AST.FunctionCall:
                try:
                    if node.id == "free":
                        print("Free!", node, node.params.exprs[0].id)
                        self.freed.add((node.params.exprs[0].id, self.function))
                        print(self.freed)
                except Exception:
                    pass
            case AST.FunctionDef:
                self.function = node.name
