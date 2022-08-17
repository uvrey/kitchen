from logging import root
from manim import m
from kitchen import (RE_TERMINAL, RE_PRODUCTION, RE_NONTERMINAL, cli_helper, sounds, animation)
import typer

class SymbolTable:
    def __init__(self, cfg, root, g):
        self.cfg = cfg
        self.root = root
        self.g = g

# 1.	If a variable(identifier) is created/defined on the left hand side of an assignment, it should check if it has already been defined, in which case it should generate an appropriate semantic error. 
# 2.	If a variable(identifier) is used in the right hand side of an assignment it should check if it has been defined already, and if not it should generate an appropriate semantic error.
    def create_symbol_table(self):
        pass

    def traverse_tree(self):
        pass

"""
DONE
investigate fstack weirdness :)
get BLA working on current test cases (ll(1) subsets should work) :)
warn when they are ambiguous :)
customise the regex terminal definitions :)
match raw input with regex expressions :)
get regex spec from app/ with simon's help :)
"""

"""
TODO - DEVELOPMENT

get PT test cases written

MANIM
check epsilon bug in LL(1) parsing video
long names look weird in parsing vids
Fix manim parsing by adding improved algorithm  

GRAMMARS

SEMANTIC ANALYSIS
based on BLA, with help from the assignment
add intro scene with token stream 

""" 

"""
TODO - INTEGRATION
start dsl tool from the typer app
get regex commands
""" 

"""
TODO - DETAILS
scaling FS and FW properly
cfg_1 parsing has sound not found error
remove debugging output
generate tree PNG for export
update menu
PT table spacing on large outputs
notify about LL(1) grammar ambiguity from parse table stage.
Neaten up cli_helper parsing code
""" 

"""
TODO - ADMIN
complete documentation
README
clean up code   
clean git repo

PAPER
- write and edit

USER TESTING
- ethics approval
- conduct tests
""" 

""" *********************************************************
EXTENSIONS
- lecturer-supplied audio
- LALR/ shift reduce/ recursive descent parsing
- proof of accuracy - algorithm analysis
- Reload CFGs within the app
- extension: detect LR recursion etc
"""

""" 
NOTES
Valid LL(1) Grammars

For any production S -> A | B, it must be the case that:

    For no terminal t could A and B derive strings beginning with t
    At most one of A and B can derive the empty string
    if B can derive the empty string, then A does not derive any 
    string beginning with a terminal in Follow(A)
"""

""" 
LIMITATIONS
Unlike PLY (LALR), Kitchen does not have
support for empty productions, precedence rules, error recovery, 
and ambiguous grammars. 

"""