import sys
import ply.lex as lex
import ply.yacc as yacc

def makelexer() :

    tokens = (
        ## Keywords
        'DATE',
        'ENDDEFNS',
        'END',
        'TIMESCALE',
        'SCOPE',
        'VAR',
        'UPSCOPE',
        'OCTOTHORPE',
        'COMMENT',
        'DUMPALL',
        'DUMPON',
        'DUMPOFF',
        'DUMPVARS',
        'VERSION',
        'BEGIN',
        'FORK',
        'FUNCTION',
        'MODULE',
        'TASK',
        'EVENT',
        'INTEGER',
        'PARAMETER',
        'REAL',
        'REG',
        'SUPPLY0',
        'SUPPLY1',
        'TIME',
        'TRI',
        'TRIAND',
        'TRIOR',
        'TRIREG',
        'TRI0',
        'TRI1',
        'WAND',
        'WIRE',
        'WOR',

        ## Non-trivial tokens
        'DEC_NUM',
        'TIME_UNIT',
        'IDENTIFIER'
        )

    t_ENDDEFNS= r'\$enddefinitions'
    t_END= r'\$end'
    t_TIMESCALE= r'\$timescale'
    t_SCOPE= r'\$scope'
    t_VAR= r'\$var'
    t_UPSCOPE= r'\$upscope'
    t_OCTOTHORPE= r'\#'
    t_DUMPALL= r'\$dumpall'
    t_DUMPON= r'\$dumpon'
    t_DUMPOFF= r'\$dumpoff'
    t_DUMPVARS= r'\$dumpvars'
    t_BEGIN= r'begin'
    t_FORK= r'fork'
    t_FUNCTION= r'function'
    t_MODULE= r'module'
    t_TASK= r'task'
    t_EVENT= r'event'
    t_INTEGER= r'integer'
    t_PARAMETER= r'parameter'
    t_REAL= r'real'
    t_REG= r'reg'
    t_SUPPLY0= r'supply0'
    t_SUPPLY1= r'supply1'
    t_TIME= r'time'
    t_TRI= r'tri'
    t_TRIAND= r'triand'
    t_TRIOR= r'trior'
    t_TRIREG= r'trireg'
    t_TRI0= r'tri0'
    t_TRI1= r'tri1'
    t_WAND= r'wand'
    t_WIRE= r'wire'
    t_WOR= r'wor'
    


    t_TIME_UNIT= r's | ms | us | ns | ps | fs'

    t_IDENTIFIER=r'\S+'

    def t_DEC_NUM(t):
        r'\d+'
        t.value=int(t.value)
        return t

# Error handling rule
    def t_error(t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)
        sys.exit(-1)

## Whitespace
    t_ignore_WS = r'\s'

## Just eat free-form text
    states=(
        ('text','exclusive'),
        )

    def t_DATE(t):                      # Eats END
        r'\$date'
        t.lexer.text_start = t.lexer.lexpos
        t.lexer.in_type='DATE'
        t.lexer.begin('text')

    def t_VERSION(t):                   # Eats END
        r'\$version'
        t.lexer.text_start = t.lexer.lexpos
        t.lexer.in_type='VERSION'
        t.lexer.begin('text')

    def t_COMMENT(t):                   # Eats END
        r'\$comment'
        t.lexer.text_start = t.lexer.lexpos
        t.lexer.in_type='COMMENT'
        t.lexer.begin('text')

    def t_text_error(t):
        t.lexer.skip(1)

    def t_text_END(t):
        r'\$end'
        t.value = t.lexer.lexdata[t.lexer.text_start:t.lexer.lexpos+1]
        t.type = t.lexer.in_type
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')           
        return t


    lexer = lex.lex()
    return (lexer, tokens)

def make_decl_parser(tokens):

    def p_header(p):
        '''header : decl_command_list end_defns'''
        p[0] = ('header',p[1])        
        print(p[0])
        return

    def p_decl_command_list(p):

        '''decl_command_list : decl_command
                             | decl_command_list decl_command'''
        if len(p)==2:
            p[0] = ('decl_command_list',p[1])
        else:
            p[0] = ('decl_command_list',p[1],p[2])       
        #print(p[0])
        return

    def p_decl_command(p):
        '''decl_command : vcd_decl_date
                        | vcd_decl_version
                        | vcd_decl_timescale
                        | vcd_scope
                        | vcd_decl_vars
        '''
        p[0] = ('decl_command',p[1])
        print(p[0])
        return

    def p_end_defns(p):
        '''end_defns : ENDDEFNS END
        '''
        p[0] = ('end_decls')
        return

    def p_vcd_decl_date(p):
        '''vcd_decl_date : DATE '''
        p[0] = ('decl_date',p[1])
        return


    def p_vcd_decl_version(p):
        '''vcd_decl_version : VERSION '''
        p[0] = ('decl_version',p[1])
        return
        
    def p_vcd_decl_timescale(p):
        '''vcd_decl_timescale : TIMESCALE DEC_NUM TIME_UNIT END'''
        p[0] = ('decl_timescale', p[2], p[3])
        return

    def p_vcd_scope(p):
        ''' vcd_scope : vcd_decl_scope decl_command_list vcd_decl_upscope '''
        p[0] = ('scope', p[1], p[2], p[3])
        return

    def p_vcd_decl_scope(p):
        '''vcd_decl_scope : SCOPE scope_type IDENTIFIER END
        '''
        p[0] = ('decl_scope', p[2], p[3])
        return


    def p_vcd_decl_upscope(p):
        '''vcd_decl_upscope : UPSCOPE END
        '''
        p[0] = ('decl_upscope')
        return


    def p_scope_type(p):
        '''scope_type : BEGIN
                      | FORK
                      | FUNCTION
                      | MODULE
                      | TASK
        '''
        p[0] = ('scope_type',p[1])
        return

    def p_vcd_decl_vars(p):
        ''' vcd_decl_vars : VAR var_type DEC_NUM IDENTIFIER IDENTIFIER END
        '''
        p[0] = ('decl_vars', p[2], p[3], p[4], p[5])
        return

    def p_var_type(p):
        ''' var_type : EVENT
                     | INTEGER
                     | PARAMETER
                     | REAL
                     | REG
                     | SUPPLY0
                     | SUPPLY1
                     | TIME
                     | TRI
                     | TRIAND
                     | TRIOR
                     | TRIREG
                     | TRI0
                     | TRI1
                     | WAND
                     | WIRE
                     | WOR
        '''
        p[0] = ('var_type',p[1])
        return
        


    def p_error(p):
        print "Syntax error at token", p.type
        # Just discard the token and tell the parser it's okay.
        yacc.errok()

        
    parser = yacc.yacc(debug=True, start='header')
    return parser

lexer, tokens = makelexer()
dparser = make_decl_parser(tokens)

f = file("foo.vcd")
dparser.parse(f.read(), lexer=lexer)
#lexer.input(f.read())
# while True:
#     tok = lexer.token()
#     if not tok: break      # No more input
#     print tok
