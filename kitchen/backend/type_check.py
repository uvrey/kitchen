
import manim as m
from kitchen.helpers import (display)
import anytree
import pandas as pd

class SemanticAnalyser:
    def __init__(self, cfg, root, inp):
        self.cfg = cfg
        self.root = root
        self.input = inp
        self.symbol = {'Symbol': [], 'Type': []}

    # TODO get +/ = to associate names and vals
    # 1.	If a variable(identifier) is created/defined on the left hand side of an assignment, it should check if it has already been defined, in which case it should generate an appropriate semantic error. 
    # 2.	If a variable(identifier) is used in the right hand side of an assignment it should check if it has been defined already, and if not it should generate an appropriate semantic error.
    # TODO get context of expression; when is it LHS, when is it RHS?

    def _call_error(self, msg = ""):
        display.fail_secho("Type Error: "+ msg)
        self.print_symbol_table()
        return 

    # plan: check if types are the same on either side. if so, we check rhs and lhs accordingly
    def init_analysis(self):
        lhs = True
        lh_type = None
        for node in anytree.PreOrderIter(self.root):
            if node.token != None:
                try:
                    if not lhs:
                        if node.token.value not in self.symbol['Symbol'] and lh_type == node.token.type:
                            self._call_error(node.token.value + " has not yet been defined.")
                            return
                        lhs = True
                    else:
                        if node.token.value != "=":
                            if node.token.value in self.symbol['Symbol']:
                                self._call_error(node.token.value + " has already been defined.")
                                return
                            else:
                                lh_type = node.token.type
                        else:
                            lhs = False
                    
                    self.symbol['Symbol'].append(node.token.value)
                    self.symbol['Type'].append(node.token.type)

                except:
                    self._call_error("Cannot semantically analyse only a token stream.")
                    return
        self.print_symbol_table()

    def print_symbol_table(self):
        display.info_secho("Symbol Table:")
        df = pd.DataFrame.from_dict(self.symbol).to_markdown()
        display.structure_secho(df)

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
solve CFG_13 parsing table, ll1 bug :)
pass the funny things :)
id language :)
semantic analyser backend :)
solve parsing bug with bla_complex - it was not LL(1) compatible :)
first set animation not moving CFG to the left :)
PT table spacing on large outputs :) 
update menu :)
"""

"""
TODO - DEVELOPMENT

TESTING
get lots of test cases written

MANIM
check epsilon bug in LL(1) parsing video
long names look weird in parsing vids - place above node and highlight the colour to opp of bg? 
Fix manim parsing by adding improved algorithm  
Get parsing colours to match LL(1) tokens
implement semantic analysis

GRAMMARS
validate grammars and language spec

CLI
- some terminals missing regex error - investigate
- Notes on regex spec - necessary?
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
another algorithm? (easy?)

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
Checking for conflicts
Sound may get corrupted when animation is cancelled before it is finished - so it can't clear the cache
"""