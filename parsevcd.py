import sys
import ply.lex as lex

tokens = (
    ## Keywords
    'DATE',
    'END',
    'TIMESCALE',
    'SCOPE',
    'VAR',
    'WIRE',
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
    
    ## Non-trivial tokens
    'DEC_NUM',
    'TIME_UNIT',
    'IDENTIFIER'
    )

t_END= r'\$end'
t_TIMESCALE= r'\$timescale'
t_SCOPE= r'\$scope'
t_VAR= r'\$var'
t_WIRE= r'\$wire'
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

def t_DATE(t):
    r'\$date'
    t.lexer.text_start = t.lexer.lexpos
    t.lexer.in_type='DATE'
    t.lexer.begin('text')

def t_VERSION(t):
    r'\$version'
    t.lexer.text_start = t.lexer.lexpos
    t.lexer.in_type='VERSION'
    t.lexer.begin('text')

def t_COMMENT(t):
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

f = file("foo.vcd")
lexer.input(f.read())

while True:
    tok = lexer.token()
    if not tok: break      # No more input
    print tok
