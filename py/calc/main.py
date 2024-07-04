from calc_lex import lexer

lexer.input("3 + 4")

for tok in lexer:
    print(tok.type, tok.value, tok.lineno, tok.lexpos)
