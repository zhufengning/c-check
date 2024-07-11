import sys
import logging
import logging.handlers
import ply.yacc as yacc
from .cparser import Cparser
from .AST import *


if __name__ == "__main__":

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "test.c"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    Cparser = Cparser()
    parser = yacc.yacc(module=Cparser)
    text = file.read()
    # parser.parse(text, lexer=Cparser.scanner, debug=logger)
    # parser.parse(text, lexer=Cparser.scanner)
    ast = parser.parse(text, lexer=Cparser.scanner)
    print(ast.printTree(0))
