try:
    from dslmodule.gcc     import sem
    from dslmodule.gcc.ply import lex
    from dslmodule.gcc.ply import yacc
    
except (Exception):
    from gcc     import sem
    from gcc.ply import lex
    from gcc.ply import yacc
