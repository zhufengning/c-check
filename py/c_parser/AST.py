class Node(object):

    def __init__(self, node_info):
        self.lineno = node_info["lno"]
        print(node_info)



class ErrorNode(Node):
    pass


class Program(Node):
    def __init__(self, ext_decls, fundefs, instrs):
        self.ext_decls = ext_decls
        self.fundefs = fundefs
        self.instrs = instrs


class Const(Node):
    def __init__(self, value):
        self.value = value


class Integer(Const):
    pass


class Float(Const):
    pass


class String(Const):
    pass


class Variable(Node):
    def __init__(self, id, pos, arr=None):
        self.id = id
        self.pos = pos
        self.arr =arr

    def __str__(self):
        #print(self.id,self.arr.index)
        return self.id + (f"[{self.arr.index}]" if self.arr else "") + " " + str(self.pos)


class BinExpr(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        # sprint(left, op, right)


class ExprList(Node):
    def __init__(self, exprs):
        self.exprs = exprs


class FunctionCall(Node):
    def __init__(self, id, params, pos):
        self.id = id
        self.params = params
        self.pos = pos


class FunctionDefList(Node):
    def __init__(self, fundefs):
        self.fundefs = fundefs


class FunctionDef(Node):
    def __init__(self, rettype, name, fmlparams, body, pos):
        self.rettype = rettype
        self.name = name
        self.fmlparams = fmlparams
        self.body = body
        self.pos = pos


class InstructionList(Node):
    def __init__(self, instrs):
        self.instrs = instrs


class PrintInstruction(Node):
    def __init__(self, expr):
        self.expr = expr


class ReturnInstruction(Node):
    def __init__(self, expr):
        self.expr = expr


class DeclarationList(Node):
    def __init__(self, decls):
        self.decls = decls


class Declaration(Node):
    def __init__(self, type, inits, pos):
        self.type = type
        self.inits = inits
        self.pos = pos


class InitList(Node):
    def __init__(self, inits):
        self.inits = inits


class Init(Node):
    def __init__(self, id, expr, pos):
        self.id = id
        self.expr = expr
        self.pos = pos


class ChoiceInstruction(Node):
    def __init__(self, cond, ithen, ielse=None):
        self.cond = cond
        self.ithen = ithen
        self.ielse = ielse


class WhileInstruction(Node):
    def __init__(self, kw, cond, instr):
        self.keyword = kw
        self.cond = cond
        self.instr = instr


class ForInstruction(Node):
    def __init__(self, kw, expr1, expr2, expr3, instr):
        self.keyword = kw
        self.expr1 = expr1
        self.expr2 = expr2
        self.expr3 = expr3
        self.instr = instr


class ContinueInstruction(Node):
    def __init__(self):
        pass


class BreakInstruction(Node):
    def __init__(self):
        pass


class CompoundInstructions(Node):
    def __init__(self, decls, instrs):
        self.decls = decls
        self.instrs = instrs


class Assignment(Node):
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr


class LabeledInstruction(Node):
    def __init__(self, kw, instr):
        self.keyword = kw
        self.instr = instr


class ArgsList(Node):
    def __init__(self, args):
        self.args = args


class Arg(Node):
    def __init__(self, type, id):
        self.type = type
        self.id = id


class Null(Node):
    def __init__(self):
        pass


class Array(Node):
    def __init__(self, index):
        self.index = index


class Pointer(Node):
    def __init__(self, id):
        self.id = id
    def __str__(self) -> str:
        return "*"+self.id

class Address(Node):
    def __init__(self, var):
        self.var = var

class Deref(Node):
    def __init__(self, var):
        self.var = var
