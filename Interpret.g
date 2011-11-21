tree grammar Interpret;

options {
    language=Python;
    tokenVocab=ValueChangeDump;
    ASTLabelType=CommonTree;
}

@init {
    self.vars={};
    self.empty=[];
}

vcd_header : ^(HEADER decl_command_list[stack=self.empty])
        {print $decl_command_list.value; print self.vars}
    ;

decl_command_list [stack] returns [value]
    :  ^(DECLS decl_command[stack=stack]+)
        {value = "foo";
         print repr($decl_command.value);
         print repr($stack)             
        }
    ;

decl_command [stack] returns [value]
    : ^(TIMESCALE DEC_NUM TIME_UNIT)
        {$value="bob"}
    | ^(NEWVAR type=. size=DEC_NUM id_code=IDENTIFIER ref=IDENTIFIER)
        {$value="sam";
         myvar={'code':$id_code.text,'ref':$ref.text,'scope':$stack};
         self.vars[$id_code.text]=myvar;
        }
    | vcd_scope[stack=stack]
        {$value = $vcd_scope.value}
    ;

vcd_decl_timescale
    :  ^(TIMESCALE DEC_NUM TIME_UNIT)
    ;

vcd_scope [stack] returns [value]
    :  ^(NEWSCOPE vcd_decl_scope decl_command_list[stack=stack+list(($vcd_decl_scope.label,))])
        {$value="ns"}
    ;

vcd_decl_scope returns [label]
    : ^(DECLSCOPE type=. IDENTIFIER)
        {$label=$IDENTIFIER.text}   
    ;

