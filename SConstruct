import os
import re

env = Environment();
env.Append(ENV={'CLASSPATH':os.environ['CLASSPATH']});

def antlr_py_emitter(target, source, env):
    target=[]
    fname, ext = os.path.splitext(str(source[0]))
    target.append(fname+'Lexer.py')
    target.append(fname+'Parser.py')
    target.append(fname+'.tokens')
    print [str(s) for s in source]
    return (target, source)
    
antlr_py = Builder(action='antlr3 $SOURCE', src_suffix='.g', emitter=antlr_py_emitter)
env.Append(BUILDERS={'AntlrPy' : antlr_py})

antlr_sources=env.AntlrPy('ValueChangeDump')

