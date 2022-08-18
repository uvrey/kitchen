from logging import root
import manim as m
from kitchen import (RE_TERMINAL, RE_PRODUCTION, RE_NONTERMINAL, cli_helper, sounds, animation, display_helper)
import typer
import anytree

class SemanticAnalyser:
    def __init__(self, cfg, root, inp):
        self.cfg = cfg
        self.root = root
        self.input = inp
        self.symbol = {'Symbol': [], 'Type': [], 'Scope': []}

# 1.	If a variable(identifier) is created/defined on the left hand side of an assignment, it should check if it has already been defined, in which case it should generate an appropriate semantic error. 
# 2.	If a variable(identifier) is used in the right hand side of an assignment it should check if it has been defined already, and if not it should generate an appropriate semantic error.
    def create_symbol_table(self):
        pass

    def traverse_tree(self):
        pass

    # TODO how to get order of this match the output?
    # why are these properties not carrying over :(
    def init_analysis(self):
        typer.echo("analysing...")
        for node in anytree.PreOrderIter(self.root):
            typer.echo(node.id)
            # if node.token != None:
            #     try:
            #         display_helper.show_tokens(node.token)
            #     except:
            #         typer.echo(node.id)

    # TODO how to add to this symbol table? 
    # reset symbol table command?
    # constraints of single line of input parsed?

"""
DONE
investigate fstack weirdness :)
get BLA working on current test cases (ll(1) subsets should work) :)
warn when they are ambiguous :)
customise the regex terminal definitions :)
match raw input with regex expressions :)
get regex spec from app/ with simon's help :)
add intro scene with token stream :)
get regex commands :)
notify about LL(1) grammar ambiguity from parse table stage. :)
"""

"""
TODO - DEVELOPMENT

get PT test cases written

TESTING
pass the funny things

solve CFG_13 parsing table, ll1 bug
solve parsing bug with bla_complex

MANIM
check epsilon bug in LL(1) parsing video
long names look weird in parsing vids - place above node and highlight the colour to opp of bg? 
Fix manim parsing by adding improved algorithm  
Get parsing colours to match LL(1) tokens

GRAMMARS
- first set animation not moving CFG to the left

CLI
- some terminals missing regex error - investigate
- Notes on regex spec - necessary?

SEMANTIC ANALYSIS
based on BLA, with help from the assignment
""" 

"""
TODO - INTEGRATION
start dsl tool from the typer app
""" 

"""
TODO - DETAILS
scaling FS and FW properly
cfg_1 parsing has sound not found error
remove debugging output
generate tree PNG for export
update menu
PT table spacing on large outputs

Neaten up cli_helper parsing code
Code style choices
gray lines for tables

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
FEATURES
- unique filenames and timestamps
- configurable interface
- 4 algorithms visualised
- handles more complex grammars
- handles DSLs
- sound effects and narration
~ matching token colours
~ some semantic analysis 
"""

""" 
LIMITATIONS
Unlike PLY (LALR), Kitchen does not have
support for empty productions, precedence rules, error recovery, 
and ambiguous grammars. 
Single line of input accepted
Max number of token colours 
Difficult grammars not handled
Sound may get corrupted when animation is cancelled before it is finished - so it can't clear the cache
"""