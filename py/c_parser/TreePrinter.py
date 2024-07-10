from . import AST


def addToClass(cls):

    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


def tprint(l, s):
    return "| " * l + s + "\n"


class TreePrinter:

    @addToClass(AST.Node)
    def printTree(self, l):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.ErrorNode)
    def printTree(self, l):
        return tprint(l, "ERROR")

    @addToClass(AST.Program)
    def printTree(self, l):
        return (
            self.ext_decls.printTree(l)
            + self.fundefs.printTree(l)
            + self.instrs.printTree(l)
        )

    @addToClass(AST.BinExpr)
    def printTree(self, l):
        return (
            tprint(l, self.op)
            + self.left.printTree(l + 1)
            + self.right.printTree(l + 1)
        )

    @addToClass(AST.Const)
    def printTree(self, l):
        return tprint(l, self.value)

    @addToClass(AST.ExprList)
    def printTree(self, l):
        r = ""
        for expr in self.exprs:
            r += expr.printTree(l)
        return r

    @addToClass(AST.FunctionCall)
    def printTree(self, l):
        # print 'Function call', self.params
        return (
            tprint(l, "FUNCALL ")
            + tprint(l + 1, self.id)
            + self.params.printTree(l + 1)
        )

    @addToClass(AST.InstructionList)
    def printTree(self, l):
        r = ""
        for instr in self.instrs:
            r += instr.printTree(l)
        return r

    @addToClass(AST.ReturnInstruction)
    def printTree(self, l):
        return tprint(l, "RETURN") + self.expr.printTree(l + 1)

    @addToClass(AST.Variable)
    def printTree(self, l):
        return tprint(l, self.id)

    @addToClass(AST.DeclarationList)
    def printTree(self, l):
        # tprint(l, "DECL_LIST")
        r = ""
        for decl in self.decls:
            r += decl.printTree(l)
        return r

    @addToClass(AST.Declaration)
    def printTree(self, l):
        return (
            tprint(l, "DECL") + tprint(l + 1, self.type) + self.inits.printTree(l + 1)
        )

    @addToClass(AST.FunctionDefList)
    def printTree(self, l):
        r = ""
        for fundef in self.fundefs:
            r += fundef.printTree(l)
        return r

    @addToClass(AST.InitList)
    def printTree(self, l):
        r = ""
        for init in self.inits:
            r += init.printTree(l + 1)
        return r

    @addToClass(AST.Init)
    def printTree(self, l):
        return tprint(l, "=") + tprint(l + 1, self.id) + self.expr.printTree(l + 1)

    @addToClass(AST.ChoiceInstruction)
    def printTree(self, l):
        r = (
            tprint(l, "IF")
            + self.cond.printTree(l + 1)
            + tprint(l + 1, "THEN")
            + self.ithen.printTree(l + 2)
        )

        if self.ielse:
            r += tprint(l + 1, "ELSE")
            r += self.ielse.printTree(l + 2)
        return r

    @addToClass(AST.WhileInstruction)
    def printTree(self, l):
        return (
            tprint(l, self.keyword.upper())
            + self.cond.printTree(l + 1)
            + self.instr.printTree(l + 1)
        )

    @addToClass(AST.ForInstruction)
    def printTree(self, l):
        return (
            tprint(l, self.keyword.upper())
            + self.expr1.printTree(l + 1)
            + self.expr2.printTree(l + 1)
            + self.expr3.printTree(l + 1)
            + self.instr.printTree(l + 1)
        )

    @addToClass(AST.BreakInstruction)
    def printTree(self, l):
        return tprint(l, "BREAK")

    @addToClass(AST.ContinueInstruction)
    def printTree(self, l):
        return tprint(l, "CONTINUE")

    @addToClass(AST.CompoundInstructions)
    def printTree(self, l):
        return (
            tprint(l, "BLOCK")
            + self.decls.printTree(l + 1)
            + self.instrs.printTree(l + 1)
        )

    @addToClass(AST.Assignment)
    def printTree(self, l):
        return tprint(l, "=") + tprint(l + 1, self.id) + self.expr.printTree(l + 1)

    @addToClass(AST.LabeledInstruction)
    def printTree(self, l):
        return (
            tprint(l, ":") + tprint(l + 1, self.keyword) + self.instr.printTree(l + 1)
        )

    @addToClass(AST.ArgsList)
    def printTree(self, l):
        r = ""
        for args in self.args:
            r += args.printTree(l)
        return r

    @addToClass(AST.Arg)
    def printTree(self, l):
        return tprint(l, "ARG") + tprint(l + 1, self.type) + tprint(l + 1, self.id)

    @addToClass(AST.Null)
    def printTree(self, l):
        return tprint(l, "NULL")

    @addToClass(AST.FunctionDef)
    def printTree(self, l):
        return (
            tprint(l, "FUNDEF")
            + tprint(l + 1, self.name)
            + tprint(l + 1, "RET")
            + tprint(l + 2, self.rettype)
            + self.fmlparams.printTree(l + 1)
            + self.body.printTree(l + 1)
        )
