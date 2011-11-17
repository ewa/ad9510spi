grammar ValueChangeDump;

tokens {
    ENDDEFNS = '$enddefinitions';
    END= '$end';
    TIMESCALE= '$timescale';
    SCOPE= '$scope';
    VAR= '$var';
    UPSCOPE= '$upscope';
    OCTOTHORPE= '#';
    DUMPALL= '$dumpall';
    DUMPON= '$dumpon';
    DUMPOFF= '$dumpoff';
    DUMPVARS= '$dumpvars';
    BEGIN= 'begin';
    FORK= 'fork';
    FUNCTION= 'function';
    MODULE= 'module'   ;
    TASK= 'task';
    EVENT= 'event'; 
    INTEGER= 'integer';
    PARAMETER= 'parameter';
    REAL= 'real';
    REG= 'reg';
    SUPPLY0= 'supp  ly0';
    SUPPLY1= 'supply1';
    TIME= 'time';
    TRI= 'tri';
    TRIAND= 'triand';
    TRIOR= 'trio';
    TRIREG= 'trireg';
    TRI0= 'tri0';
    TRI1= 'tri1';
    WAND= 'wand';
    WIRE= 'wire';
    WOR= 'wor';
}

@rulecatch{
	catch (RecognitionException e) {
        reportError(e);
                throw e;
    }
}

/* Parser rules */

vcd_header
    : decl_command_list end_defns
    ;

decl_command_list 
    : decl_command+
    ;

decl_command 
    : vcd_decl_date
    | vcd_decl_version
    | vcd_decl_timescale
    | vcd_scope
    | vcd_decl_vars
    ;


end_defns 
    : ENDDEFNS END
    ;

vcd_decl_date 
    : DATE
    ;

vcd_decl_version 
    : VERSION
    ;

vcd_decl_timescale
    : TIMESCALE DEC_NUM TIME_UNIT END
    ;

vcd_scope
    : vcd_decl_scope decl_command_list vcd_decl_upscope
    ;

vcd_decl_scope 
    : SCOPE scope_type IDENTIFIER END
    ;

vcd_decl_upscope 
    : UPSCOPE END
    ;

scope_type 
    : BEGIN
    | FORK
    | FUNCTION
    | MODULE
    | TASK
    ;

vcd_decl_vars
    : VAR var_type DEC_NUM IDENTIFIER IDENTIFIER END
    ;

var_type
    : EVENT
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
    ;

/* Lexer rules */


DEC_NUM :	'0'..'9'+
    ;
TIME_UNIT
	:  's' | 'ms' | 'us' | 'ns' | 'ps' | 'fs'
	;


ML_COMMENT
    :   '$comment' (options {greedy=false;} : .)* '$end' {$channel=HIDDEN;}
    ;
 
DATE
    :   '$date' (options {greedy=false;} : .)* '$end'
    ;

VERSION
    :   '$version' (options {greedy=false;} : .)* '$end'
    ;

WS  :   ( ' '
        | '\t'
        | '\r'
        | '\n'
        ) {$channel=HIDDEN;}
    ;


/*
IDENTIFIER :	('a'..'z'|'A'..'Z'|'_'|'!'..'/') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'!'..'/')*
    ;
 */
 
// Almost every non-space printable character.   The '..' operation here depends on the ASCII ordering
// Note that I am departing from the IEEE standard by not allowing a digit as the first character.  That's a 
// hack to prevent strings like "10ns" from being lexed as an identifier.  So far, every VCD file I've looked at 
// complies with this, but it's still technically wrong.
 IDENTIFIER
 	: ('a'..'z'|'A'..'Z'|'_'|'!'..'/'|':'..'@')('!'..'~')+	
 	;