#!/usr/bin/env python

import sys
import antlr3
from antlr3.tree import CommonTree
from ValueChangeDumpLexer import ValueChangeDumpLexer, EOF
from ValueChangeDumpParser import ValueChangeDumpParser
from Interpret import Interpret
from VCDSimulation import VCDSimulation

class VCDContext:

    def __init__(self, dict):
        self.defns = dict
        self.now = None
        self.values = {}
        for id_code in self.defns.keys():
            self.values[id_code] = None

    def note_time(self, time):
        self.now = time

    def scalar_change(self, id_code, newvalue):
        varinfo = self.defns[id_code]
        ref = varinfo['ref']
        old_value = self.values[id_code]
        self.values[id_code]=newvalue
        print "%7d Scalar: %s:  %s -> %s\t%s" % (self.now, id_code, old_value, newvalue,ref)

    def vector_change(self, id_code, newvalue):
        varinfo = self.defns[id_code]
        ref = varinfo['ref']
        extended_value = self.__extend_vec(id_code,newvalue)
        old_value = self.values[id_code]
        self.values[id_code]=extended_value
        print "%7d Vector: %s: %s -> %s\t%s" % (self.now, id_code, old_value, extended_value, ref)

        ##print"\t %s --> %s" % (newvalue, extended_value)

    def __extend_vec(self, id_code, value_str):

        "Based on Donald 'Paddy' McCarthy's vcd_reader"
        
        extend_digits = self.defns[id_code]['size'] - len(value_str)
        if extend_digits:
            value_str = ('0' if value_str[0]=='1'
                         else value_str[0])*extend_digits + value_str
        return value_str



def antlr_setup(file):
    char_stream = antlr3.ANTLRInputStream(file)
    lexer = ValueChangeDumpLexer(char_stream)        
    tokens = antlr3.CommonTokenStream(lexer)
    parser = ValueChangeDumpParser(tokens)
    return (parser, tokens)

def process_header(parser, tokenStream):

    r = parser.vcd_header()

    # this is the root of the AST
    root = r.tree

    nodes = antlr3.tree.CommonTreeNodeStream(root)
    nodes.setTokenStream(tokenStream)
    interpret = Interpret(nodes)
    result = interpret.vcd_header()
    return result

def process_body(parser, tokenStream, dict):
    context = VCDContext(dict)
    while True:
        r = parser.simulation_command()
        # this is the root of the AST
        if r.tree is None:
            continue        
        if (r.tree.type == antlr3.INVALID_TOKEN_TYPE):
            print "Invalid token -- done?"
            break
        #print r.tree.text
        #print(repr(r.tree))
        # this is the root of the AST
        root = r.tree

        nodes = antlr3.tree.CommonTreeNodeStream(root)
        nodes.setTokenStream(tokenStream)
        sim = VCDSimulation(nodes)
        result = sim.simulation_command(context)
        #print result

               
       
def main(args):
    parser, tokens = antlr_setup(sys.stdin)
    dict = process_header(parser, tokens)
    print dict
    process_body(parser, tokens, dict)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
