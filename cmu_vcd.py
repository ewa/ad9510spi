#!/usr/bin/env python

import sys
import antlr3
from antlr3.tree import CommonTree
from ValueChangeDumpLexer import ValueChangeDumpLexer, EOF
from ValueChangeDumpParser import ValueChangeDumpParser
from Interpret import Interpret
from VCDSimulation import VCDSimulation

class VCDContext:

    def __init__(self, dict, verbose_changes=False):
        self.defns = dict
        self.now = None
        self.verbose_changes = verbose_changes
        self.values = {}
        self.ref_to_idcode = {}
        self.watchers = {}
        for id_code in self.defns.keys():
            self.values[id_code] = None
            self.watchers[id_code] = []
            ref = self.defns[id_code]['ref']
            self.ref_to_idcode[ref] = id_code
        

    def note_time(self, time):
        self.now = time

    def __common_change(self, id_code, new_value):
        varinfo = self.defns[id_code]
        ref = varinfo['ref']
        old_value = self.values[id_code]
        if ((old_value is None) or (new_value != old_value)):
            self.values[id_code]=new_value
            for obs in self.watchers[id_code]:
                obs(self.now,id_code,ref,old_value, new_value, (old_value is None))
        return old_value

    def scalar_change(self, id_code, newvalue):        
        old_value = self.__common_change(id_code,newvalue)
        if self.verbose_changes:
            ref = self.defns[id_code]['ref']
            print "%7d Scalar: %s:  %s -> %s\t%s" % (self.now, id_code, old_value, newvalue,ref)
        
    def vector_change(self, id_code, newvalue):        
        extended_value = self.__extend_vec(id_code,newvalue)
        old_value = self.__common_change(id_code,extended_value)
        if self.verbose_changes:
            ref = self.defns[id_code]['ref']
            print "%7d Vector: %s: %s -> %s\t%s" % (self.now, id_code, old_value, extended_value, ref)

        ##print"\t %s --> %s" % (newvalue, extended_value)

    def __extend_vec(self, id_code, value_str):

        "Based on Donald 'Paddy' McCarthy's vcd_reader"
        
        extend_digits = self.defns[id_code]['size'] - len(value_str)
        if extend_digits:
            value_str = ('0' if value_str[0]=='1'
                         else value_str[0])*extend_digits + value_str
        return value_str

    def reg_by_name(self, ref, observer):
        id_code = self.ref_to_idcode[ref]
        self.watchers[id_code].append(observer)

        
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

def process_body(parser, tokenStream, context):
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

class AntlrVCD:

    "A very thin wrapper for the parsing functions in this file"
    
    def __init__(self, file):
        self.parser, self.tokens = antlr_setup(file)
        self.dict = process_header(self.parser, self.tokens)
        self.context = VCDContext(self.dict)

    def reg_by_name(self, name, observer):
        self.context.reg_by_name(name, observer)

    def go(self):
        process_body(self.parser, self.tokens, self.context)

    def getContext(self):
        return self.context
       
def main(args):

    foo = AntlrVCD(sys.stdin)
    foo.go()
    # parser, tokens = antlr_setup(sys.stdin)
    # dict = process_header(parser, tokens)
    # print dict
    # process_body(parser, tokens, dict)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
