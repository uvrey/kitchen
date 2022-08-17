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
TODO - DEVELOPMENT
match raw input with regex expressions
get regex spec from app/ with simon's help

investigate fstack weirdness :)

get BLA working on current test cases
get PT test cases written
Fix manim parsing by adding improved algorithm  

MANIM
check epsilon bug in LL(1) parsing video

GRAMMARS
warn when they are ambiguous
extension: detect LR recursion etc

SEMANTIC ANALYSIS
based on BLA, with help from the assignment
add intro scene with token stream
customise the terminal definitions
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

""" 
EXTENSIONS
- lecturer-supplied audio
- LALR/ shift reduce/ recursive descent parsing
- proof of accuracy - algorithm analysis
"""

""" 
FEATURES

"""