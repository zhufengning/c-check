# 更新记录：
# 1. 修复函数调用必须将结果赋给变量的问题
# 2. 修复一行中仅有表达式时不被当作语句的问题
# 3. 添加for循环
# 4. 修复空代码块卡死
# 5. 变量定义不再必须赋初值
# 6. 给FUNDEF, FUNCALL和VAR添加列信息
# 7. 指针、数组语法，取地址、解引用
# 8. 简化部分结构（因为decl算入了instr，不再按照块中先decl后instr的限定顺序，所以有些地方写死的decl+instr简化成了instr）

from .clexer import CLexer
from .AST import *
from . import TreePrinter


class FilePosition(object):
    def __init__(self, line):
        self.line = line


def pos(p):
    return FilePosition(p.lexer.lexer.lineno - 1)


def pos2(p, n):
    line_start = p.lexer.lexer.lexdata.rfind("\n", 0, p.lexpos(n)) + 1
    column = p.lexpos(n) - line_start + 1
    return p.lexer.lexer.lineno, column


class Cparser(object):

    def __init__(self):
        self.scanner = CLexer()
        self.scanner.build()

    tokens = CLexer.tokens

    precedence = (
        ("nonassoc", "IFX"),
        ("nonassoc", "ELSE"),
        ("right", "="),
        ("left", "OR"),
        ("left", "AND"),
        ("left", "|"),
        ("left", "^"),
        ("left", "&"),
        ("nonassoc", "<", ">", "EQ", "NEQ", "LE", "GE"),
        ("left", "SHL", "SHR"),
        ("left", "+", "-"),
        ("left", "*", "/", "%"),
    )

    def handle_error(self, where, p):
        print(
            "Syntax error in %s at line %d, column %d, at token LexToken(%s, '%s')"
            % (where, p.lineno, self.scanner.find_tok_column(p), p.type, p.value)
        )

    def p_error(self, p):
        if not p:
            print("Unexpected end of input")
        else:
            # let the productions handle the error on their own
            pass

    def p_program(self, p):
        """program : ext_declarations"""
        p[0] = Program(p[1])
        # p[0].printTree(0)

    def p_ext_declarations(self, p):
        """ext_declarations : declarations"""
        p[0] = p[1]
    def p_array(self, p):
        """array : '[' INTEGER ']'"""
        p[0] = Array(p[2])

    def p_declarations(self, p):
        """declarations : declarations declaration"""
        if p[2]:
            p[0] = DeclarationList(p[1].decls + [p[2]])
        else:  # error
            p[0] = p[1]

    def p_declarations_single(self, p):
        """declarations : declaration"""
        if p[1]:
            p[0] = DeclarationList([p[1]])
        else:  # error
            p[0] = DeclarationList([])

    def p_declaration_blank(self, p):
        """declarations :"""
        p[0] = DeclarationList([])

    def p_declaration_fundef(self, p):
        """declaration : fundefs"""
        p[0] = p[1]

    def p_declaration(self, p):
        """declaration : TYPE inits ';'"""
        p[0] = Declaration(p[1], p[2], pos2(p, 1))

    def p_declaration_error(self, p):
        """declaration : error ';'"""
        self.handle_error("declaration", p[1])

    def p_inits(self, p):
        """inits : inits ',' init"""
        p[0] = InitList(p[1].inits + [p[3]])

    def p_inits_single(self, p):
        """inits : init"""
        p[0] = InitList([p[1]])

    def p_init(self, p):
        """init : ID '=' expression"""
        p[0] = Init(p[1], p[3], pos2(p, 1))

    def p_init2(self, p):
        """init : ID"""
        # print(p[1])
        p[0] = Init(p[1], Null(), pos2(p, 1))

    def p_init3(self, p):
        """init : ID array"""
        # print(p[1])
        p[0] = Init(p[1], p[2], pos2(p, 1))

    def p_init4(self, p):
        """init : '*' ID"""
        # print(p[1])
        p[0] = Init(Pointer(p[2]), Null(), pos2(p, 2))

    def p_init5(self, p):
        """init : '*' ID '=' expression"""
        p[0] = Init(Pointer(p[2]), p[4], pos2(p, 2))

    def p_instructions(self, p):
        """instructions : instructions instruction"""
        if p[2]:
            p[0] = InstructionList(p[1].instrs + [p[2]])
        else:
            p[0] = p[1]

    def p_instructions_single(self, p):
        """instructions : instruction"""
        if p[1]:
            p[0] = InstructionList([p[1]])
        else:
            p[0] = InstructionList([])

    def p_instruction(self, p):
        """instruction : labeled_instr
        | assignment ';'
        | declaration
        | choice_instr
        | while_instr
        | for_instr
        | return_instr
        | break_instr
        | continue_instr
        | compound_instr
        | statement
        | expression ';'"""
        p[0] = p[1]

    def p_fun_call(self, p):
        "statement : ID '(' expr_list_or_empty ')' ';'"
        p[0] = FunctionCall(p[1], p[3], pos2(p, 1))

    def p_labeled_instr(self, p):
        """labeled_instr : ID ':' instruction"""
        p[0] = LabeledInstruction(p[1], p[3])

    def p_assignment(self, p):
        """assignment : ID '=' expression"""
        if p[3]:
            p[0] = Assignment(p[1], p[3])
        else:  # error
            pass
    def p_assignment_arr(self, p):
        """assignment : ID array '=' expression"""
        if p[3]:
            p[0] = Assignment(Variable(p[1], pos2(p, 1), p[2]), p[4])
        else:  # error
            pass

    def p_assignment_error(self, p):
        """assignment : ID '=' error ';'"""
        self.handle_error("assignment", p[3])

    def p_choice_instr(self, p):
        """choice_instr : IF '(' condition ')' instruction  %prec IFX"""
        p[0] = ChoiceInstruction(p[3], p[5])

    def p_choice_instr_else(self, p):
        """choice_instr : IF '(' condition ')' instruction ELSE instruction"""
        p[0] = ChoiceInstruction(p[3], p[5], p[7])

    def p_choice_instr_error(self, p):
        """choice_instr : IF '(' error ')' instruction  %prec IFX"""
        self.handle_error("if condition", p[3])

    def p_choice_instr_else_error(self, p):
        """choice_instr : IF '(' error ')' instruction ELSE instruction"""
        self.handle_error("if condition", p[3])

    def p_while_instr(self, p):
        """while_instr : WHILE '(' condition ')' instruction"""
        p[0] = WhileInstruction(p[1], p[3], p[5])

    def p_for_instr(self, p):
        """for_instr : FOR '(' instruction expression ';' assignment ')' instruction"""
        p[0] = ForInstruction(p[1], p[3], p[4], p[6], p[8])

    def p_for_error(self, p):
        """for_instr : FOR '(' error ')' instruction"""
        self.handle_error("for instruction", p[3])

    def p_while_error(self, p):
        """while_instr : WHILE '(' error ')' instruction"""
        self.handle_error("while instruction", p[3])

    def p_return_instr(self, p):
        """return_instr : RETURN expression ';'"""
        p[0] = ReturnInstruction(p[2])

    def p_continue_instr(self, p):
        """continue_instr : CONTINUE ';'"""
        p[0] = ContinueInstruction()

    def p_break_instr(self, p):
        """break_instr : BREAK ';'"""
        p[0] = BreakInstruction()

    def p_compound_instr(self, p):
        """compound_instr : '{' instructions '}'"""
        p[0] = CompoundInstructions(p[2])

    def p_compound_instr2(self, p):
        """compound_instr : '{' '}'"""
        p[0] = CompoundInstructions(InstructionList([]))

    def p_condition(self, p):
        """condition : expression"""
        p[0] = p[1]

    def p_const_integer(self, p):
        """const : INTEGER"""
        p[0] = Integer(p[1])

    def p_const_float(self, p):
        """const : FLOAT"""
        p[0] = Float(p[1])

    def p_const_string(self, p):
        """const : STRING"""
        p[0] = String(p[1])

    def p_expression_const(self, p):
        """expression : const"""
        p[0] = p[1]

    def p_expression_id(self, p):
        "expression : ID"
        p[0] = Variable(p[1], pos2(p, 1))

    def p_expression_id_addr(self, p):
        "expression : '&' ID"
        p[0] = Address(Variable(p[2], pos2(p, 2)))

    def p_expression_id_deref(self, p):
        "expression : '*' ID"
        p[0] = Deref(Variable(p[2], pos2(p, 2)))

    def p_expression_arr(self, p):
        "expression : ID array"
        p[0] = Variable(p[1], pos2(p, 1), p[2])

    def p_expression_brackets(self, p):
        "expression : '(' expression ')'"
        p[0] = p[2]

    def p_expression_brackets_error(self, p):
        "expression : '(' error ')'"
        self.handle_error("expression (bracket)", p[2])

    def p_expression_fun_call(self, p):
        "expression : ID '(' expr_list_or_empty ')'"
        p[0] = FunctionCall(p[1], p[3], pos2(p, 1))

    def p_expression_fun_call_error(self, p):
        "expression : ID '(' error ')'"
        self.handle_error("function call", p[3])

    def p_expression_binary_op(self, p):
        """expression : expression '+' expression
        | expression '-' expression
        | expression '*' expression
        | expression '/' expression
        | expression '%' expression
        | expression '|' expression
        | expression '&' expression
        | expression '^' expression
        | expression AND expression
        | expression OR expression
        | expression SHL expression
        | expression SHR expression
        | expression EQ expression
        | expression NEQ expression
        | expression '>' expression
        | expression '<' expression
        | expression LE expression
        | expression GE expression"""

        p[0] = BinExpr(p[1], p[2], p[3])

    def p_expr_list_non_empty(self, p):
        """expr_list_or_empty : expr_list"""
        p[0] = p[1]

    def p_expr_list_empty(self, p):
        """expr_list_or_empty :"""
        p[0] = ExprList([])

    def p_expr_list(self, p):
        """expr_list : expr_list ',' expression"""
        p[0] = ExprList(p[1].exprs + [p[3]])

    def p_expr_list_single(self, p):
        """expr_list : expression"""
        p[0] = ExprList([p[1]])

    # def p_fundefs(self, p):
    #     """fundefs : fundefs fundef
    #                | fundef """
    #     if p[2]:
    #         p[0] = FunctionDefList(p[1].fundefs + [ p[2] ])
    #     else:
    #         p[0] = FunctionDefList([ p[1] ])

    def p_fundefs(self, p):
        """fundefs : fundefs fundef"""
        p[0] = FunctionDefList(p[1].fundefs + [p[2]])

    def p_fundefs_single(self, p):
        """fundefs : fundef"""
        p[0] = FunctionDefList([p[1]])

    def p_fundefs_empty(self, p):
        """fundefs :"""
        p[0] = FunctionDefList([])

    def p_fundef(self, p):
        """fundef : TYPE ID '(' args_list_or_empty ')' compound_instr"""
        p[0] = FunctionDef(p[1], p[2], p[4], p[6], pos2(p, 2))

    def p_args_list_or_empty(self, p):
        """args_list_or_empty : args_list
        |"""
        if len(p) > 1:
            p[0] = p[1]
        else:
            p[0] = ArgsList([])

    # def p_args_list(self, p):
    #     """args_list : args_list ',' arg
    #                  | arg """
    #     if p[3]:
    #         p[0] = ArgsList(p[1].args + [ p[3] ])
    #     else:
    #         p[0] = ArgsList([ p[1] ])

    def p_args_list(self, p):
        """args_list : args_list ',' arg"""
        p[0] = ArgsList(p[1].args + [p[3]])

    def p_args_list_single(self, p):
        """args_list : arg"""
        p[0] = ArgsList([p[1]])

    def p_arg(self, p):
        """arg : TYPE ID"""
        p[0] = Arg(p[1], p[2])
