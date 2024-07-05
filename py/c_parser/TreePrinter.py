import AST


def addToClass(cls):

    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


def tprint(l, s):
    print("| " * l + s)


class TreePrinter:

    @addToClass(AST.Node)
    def printTree(self, l):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.ErrorNode)
    def printTree(self, l):
        tprint(l, "ERROR")

    @addToClass(AST.Program)
    def printTree(self, l):
        self.ext_decls.printTree(l)
        self.fundefs.printTree(l)
        self.instrs.printTree(l)

    @addToClass(AST.BinExpr)
    def printTree(self, l):
        tprint(l, self.op)
        self.left.printTree(l + 1)
        self.right.printTree(l + 1)

    @addToClass(AST.Const)
    def printTree(self, l):
        tprint(l, self.value)

    @addToClass(AST.ExprList)
    def printTree(self, l):
        for expr in self.exprs:
            expr.printTree(l)

    @addToClass(AST.FunctionCall)
    def printTree(self, l):
        # print 'Function call', self.params
        tprint(l, "FUNCALL ")
        tprint(l + 1, self.id)
        self.params.printTree(l + 1)

    @addToClass(AST.InstructionList)
    def printTree(self, l):
        for instr in self.instrs:
            instr.printTree(l)

    @addToClass(AST.ReturnInstruction)
    def printTree(self, l):
        tprint(l, "RETURN")
        self.expr.printTree(l + 1)

    @addToClass(AST.Variable)
    def printTree(self, l):
        tprint(l, self.id + " " + str(self.pos.line))

    @addToClass(AST.DeclarationList)
    def printTree(self, l):
        # tprint(l, "DECL_LIST")
        for decl in self.decls:
            decl.printTree(l)

    @addToClass(AST.Declaration)
    def printTree(self, l):
        tprint(l, "DECL")
        tprint(l + 1, self.type)
        self.inits.printTree(l + 1)

    @addToClass(AST.FunctionDefList)
    def printTree(self, l):
        for fundef in self.fundefs:
            fundef.printTree(l)

    @addToClass(AST.InitList)
    def printTree(self, l):
        for init in self.inits:
            init.printTree(l + 1)

    @addToClass(AST.Init)
    def printTree(self, l):
        tprint(l, "=")
        tprint(l + 1, self.id)
        self.expr.printTree(l + 1)

    @addToClass(AST.ChoiceInstruction)
    def printTree(self, l):
        tprint(l, "IF")
        self.cond.printTree(l + 1)

        tprint(l + 1, "THEN")
        self.ithen.printTree(l + 2)

        if self.ielse:
            tprint(l + 1, "ELSE")
            self.ielse.printTree(l + 2)

    @addToClass(AST.WhileInstruction)
    def printTree(self, l):
        tprint(l, self.keyword.upper())
        self.cond.printTree(l + 1)
        self.instr.printTree(l + 1)

    @addToClass(AST.ForInstruction)
    def printTree(self, l):
        tprint(l, self.keyword.upper())
        self.expr1.printTree(l + 1)
        self.expr2.printTree(l + 1)
        self.expr3.printTree(l + 1)
        self.instr.printTree(l + 1)

    @addToClass(AST.BreakInstruction)
    def printTree(self, l):
        tprint(l, "BREAK")

    @addToClass(AST.ContinueInstruction)
    def printTree(self, l):
        tprint(l, "CONTINUE")

    @addToClass(AST.CompoundInstructions)
    def printTree(self, l):
        tprint(l, "BLOCK")
        self.decls.printTree(l + 1)
        self.instrs.printTree(l + 1)

    @addToClass(AST.Assignment)
    def printTree(self, l):
        tprint(l, "=")
        tprint(l + 1, self.id)
        self.expr.printTree(l + 1)

    @addToClass(AST.LabeledInstruction)
    def printTree(self, l):
        tprint(l, ":")
        tprint(l + 1, self.keyword)
        self.instr.printTree(l + 1)

    @addToClass(AST.ArgsList)
    def printTree(self, l):
        for args in self.args:
            args.printTree(l)

    @addToClass(AST.Arg)
    def printTree(self, l):
        tprint(l, "ARG")
        tprint(l + 1, self.type)
        tprint(l + 1, self.id)

    @addToClass(AST.Null)
    def printTree(self, l):
        tprint(l, "NULL")

    @addToClass(AST.FunctionDef)
    def printTree(self, l):
        tprint(l, "FUNDEF")
        tprint(l + 1, self.name)
        tprint(l + 1, "RET")
        tprint(l + 2, self.rettype)
        self.fmlparams.printTree(l + 1)
        self.body.printTree(l + 1)
