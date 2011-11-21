import os
import re

env = Environment();
env.Append(ENV={'CLASSPATH':'/usr/share/java/stringtemplate.jar:/usr/share/java/antlr-3.1.3.jar'})

def antlr_py_emitter(target, source, env):
    target=[]
    fname, ext = os.path.splitext(str(source[0]))
    target.append(fname+'Lexer.py')
    target.append(fname+'Parser.py')
    target.append(fname+'.tokens')
    return (target, source)
    
antlr_py = Builder(action='java org.antlr.Tool $SOURCE', src_suffix='.g', emitter=antlr_py_emitter)
env.Append(BUILDERS={'AntlrPy' : antlr_py})

antlr_sources=env.AntlrPy('ValueChangeDump')

