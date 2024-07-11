class Node(object):
    def __init__(self, node_info):
        self.lineno = node_info["lno"]
        print(node_info)

    def __repr__(self):
        return f"Node at line {self.lineno}"

class ErrorNode(Node):
    def __repr__(self):
        return "ErrorNode"

class Program(Node):
    def __init__(self, ext_decls, fundefs, instrs):
        self.ext_decls = ext_decls
        self.fundefs = fundefs
        self.instrs = instrs

    def __repr__(self):
        return "Program"

class Const(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

class Integer(Const):
    def __repr__(self):
        return f"Integer: {self.value}"

class Float(Const):
    def __repr__(self):
        return f"Float: {self.value}"

class String(Const):
    def __repr__(self):
        return f"String: {self.value}"

class Variable(Node):
    def __init__(self, id, pos, arr=None):
        self.id = id
        self.pos = pos
        self.arr = arr

    def __repr__(self):
        return self.id + (f"[{self.arr.index}]" if self.arr else "") + " " + str(self.pos)

class BinExpr(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinExpr({self.left}, {self.op}, {self.right})"

class ExprList(Node):
    def __init__(self, exprs):
        self.exprs = exprs

    def __repr__(self):
        return f"ExprList({self.exprs})"

class FunctionCall(Node):
    def __init__(self, id, params, pos):
        self.id = id
        self.params = params
        self.pos = pos

    def __repr__(self):
        return f"FunctionCall({self.id}, {self.params}, {self.pos})"

class FunctionDefList(Node):
    def __init__(self, fundefs):
        self.fundefs = fundefs

    def __repr__(self):
        return f"FunctionDefList({self.fundefs})"

class FunctionDef(Node):
    def __init__(self, rettype, name, fmlparams, body, pos):
        self.rettype = rettype
        self.name = name
        self.fmlparams = fmlparams
        self.body = body
        self.pos = pos

    def __repr__(self):
        return f"FunctionDef({self.rettype}, {self.name}, {self.fmlparams}, {self.body}, {self.pos})"

class InstructionList(Node):
    def __init__(self, instrs):
        self.instrs = instrs

    def __repr__(self):
        return f"InstructionList({self.instrs})"

class ReturnInstruction(Node):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ReturnInstruction({self.expr})"

class DeclarationList(Node):
    def __init__(self, decls):
        self.decls = decls

    def __repr__(self):
        return f"DeclarationList({self.decls})"

class Declaration(Node):
    def __init__(self, type, inits, pos):
        self.type = type
        self.inits = inits
        self.pos = pos

    def __repr__(self):
        return f"Declaration({self.type}, {self.inits}, {self.pos})"

class InitList(Node):
    def __init__(self, inits):
        self.inits = inits

    def __repr__(self):
        return f"InitList({self.inits})"

class Init(Node):
    def __init__(self, id, expr, pos):
        self.id = id
        self.expr = expr
        self.pos = pos

    def __repr__(self):
        return f"Init({self.id}, {self.expr}, {self.pos})"

class ChoiceInstruction(Node):
    def __init__(self, cond, ithen, ielse=None):
        self.cond = cond
        self.ithen = ithen
        self.ielse = ielse

    def __repr__(self):
        return f"ChoiceInstruction({self.cond}, {self.ithen}, {self.ielse})"

class WhileInstruction(Node):
    def __init__(self, kw, cond, instr):
        self.keyword = kw
        self.cond = cond
        self.instr = instr

    def __repr__(self):
        return f"WhileInstruction({self.keyword}, {self.cond}, {self.instr})"

class ForInstruction(Node):
    def __init__(self, kw, expr1, expr2, expr3, instr):
        self.keyword = kw
        self.expr1 = expr1
        self.expr2 = expr2
        self.expr3 = expr3
        self.instr = instr

    def __repr__(self):
        return f"ForInstruction({self.keyword}, {self.expr1}, {self.expr2}, {self.expr3}, {self.instr})"

class ContinueInstruction(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "ContinueInstruction"

class BreakInstruction(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "BreakInstruction"

class CompoundInstructions(Node):
    def __init__(self, decls, instrs):
        self.decls = decls
        self.instrs = instrs

    def __repr__(self):
        return f"CompoundInstructions({self.decls}, {self.instrs})"

class Assignment(Node):
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr

    def __repr__(self):
        return f"Assignment({self.id}, {self.expr})"

class LabeledInstruction(Node):
    def __init__(self, kw, instr):
        self.keyword = kw
        self.instr = instr

    def __repr__(self):
        return f"LabeledInstruction({self.keyword}, {self.instr})"

class ArgsList(Node):
    def __init__(self, args):
        self.args = args

    def __repr__(self):
        return f"ArgsList({self.args})"

class Arg(Node):
    def __init__(self, type, id):
        self.type = type
        self.id = id

    def __repr__(self):
        return f"Arg({self.type}, {self.id})"

class Null(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return "Null"

class Array(Node):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return f"Array[{self.index}]"

class Pointer(Node):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"*{self.id}"

class Address(Node):
    def __init__(self, var):
        self.var = var

    def __repr__(self):
        return f"&{self.var}"

class Deref(Node):
    def __init__(self, var):
        self.var = var

    def __repr__(self):
        return f"*{self.var}"
