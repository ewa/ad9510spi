#!/usr/bin/env python

import sys
import antlr3
from antlr3.tree import CommonTree
from ValueChangeDumpLexer import ValueChangeDumpLexer, EOF
from ValueChangeDumpParser import ValueChangeDumpParser

def dump_tokens(lexer):
    while True:
        t = lexer.nextToken()
        if t.type == antlr3.EOF:
            break
        else:
            print t
    return

def do_file(file):
    char_stream = antlr3.ANTLRInputStream(file)
    lexer = ValueChangeDumpLexer(char_stream)        
    tokens = antlr3.CommonTokenStream(lexer)
    parser = ValueChangeDumpParser(tokens)
    result = parser.vcd_header()
    return result
    

def main(args):
    r = do_file(sys.stdin)
    print r.tree
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
