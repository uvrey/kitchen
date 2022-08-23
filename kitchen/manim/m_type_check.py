""" Generates semantic analysis. """
# kitchen/backend/type_check.py

import anytree
import pandas as pd
import manim as m

from kitchen.helpers import display, sounds, lang_spec
from kitchen.manim import m_general as mg, m_parser as mp

class MSemanticAnalyser(m.Scene):
    def setup_manim(self, cfg, root, inp):
        """Initialises the SemanticAnalyser.

        Args:
            cfg (ContextFreeGrammar): Loaded CFG.
            root (Node): Root of parse tree.
            inp (str): Input to be analysed.
        """        
        self.cfg = cfg
        self.root = root
        self.input = inp
        self.symbol = {'Symbol': [], 'Type': []}

    # shows the input stream and its association with the token stream
    def intro(self):
        # introducing the input
        title = m.Tex(r"Input to be parsed:")
        sounds.narrate("Let's parse this input.", self)
        inp = m.Text(self.inp, weight=m.BOLD, color=m.BLUE)
        m.VGroup(title, inp).arrange(m.DOWN)
        self.play(
            m.FadeIn(title),
            m.Write(inp, shift=m.DOWN),
        )
        self.wait()

        # transforming to lexing
        transform_title = m.Tex(
            "Lexing matched the input to the following tokens:")
        sounds.narrate("The input stream gives these token types.", self)
        transform_title.to_edge(m.UP)
        self.play(
            m.Transform(title, transform_title),
            m.FadeOut(inp)
        )
        self.wait()

        # show tokens then fade everything out
        
        self.play(
            m.LaggedStart(*(m.FadeIn(t, shift=m.UP)
                        for t in mp.map_token_lists(self, self.inp_list, 
                        lang_spec.get_token_format(self.tokens, types=True, 
                        as_list=True)))),
        )
        self.wait()

        # fades the scene out
        self.play(
            *[m.FadeOut(mob)for mob in self.mobjects]
        )
        
    def construct(self):
        # play the intro
        self.intro()

        # draws follow set title
        sem_title = mg.get_title_mobject("semantic analysis") 

        # sets the stage
        self.play(
            sem_title.animate.to_edge(m.UP),
        )

    def _call_error(self, msg = ""):
        """Display an error in the type-checking process.

        Args:
            msg (str, optional): Details. Defaults to "".
        """        
        mg.display_msg(self, ["Type Error: ", msg], script = msg)
        display.fail_secho("Type Error: "+ msg)
        self.print_symbol_table()
        return 

    def init_analysis(self):
        """Analyses a given input based on two basic semantic rules:
           Variable uniqueness and mutability.
        """        
        lhs = True
        lh_type = None
        for node in anytree.PreOrderIter(self.root):
            if node.token != None:
                try:
                    if not lhs:
                        if node.token.value not in self.symbol['Symbol'] \
                            and lh_type == node.token.type:
                            self._call_error(node.token.value + 
                            " has not yet been defined.")
                            return
                        lhs = True
                    else:
                        if node.token.value != "=":
                            if node.token.value in self.symbol['Symbol']:
                                self._call_error(node.token.value + 
                                " has already been defined.")
                                return
                            else:
                                lh_type = node.token.type
                        else:
                            lhs = False
                    
                    self.symbol['Symbol'].append(node.token.value)
                    self.symbol['Type'].append(node.token.type)

                except:
                    self._call_error("Cannot semantically analyse only \
                        a token stream.")
                    return
        self.print_symbol_table()

    def print_symbol_table(self):
        """Displays the symbol table.
        """        
        display.info_secho("Symbol Table:")
        df = pd.DataFrame.from_dict(self.symbol).to_markdown()
        display.structure_secho(df)

    def animate_graph(self):
        pass

    def animate_table(self):
        pass
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
restructure directory :)
documentation progress :)
neaten up imports :)
set up pdoc :)
verify m follow/ m first set :)
line length :)
check cleaning of follow set and first/ follow algorithms :)
first and follow set not using _to_tex properly - DVI issue. :)
weird token issue :)
parsing nodes size setting :)
Fix manim parsing by adding improved algorithm  HIGH :)
make start symbol root :)
Print first and followsets as dataframes :)
cfg_1 parsing has sound not found error :)
colour to opp of bg? MED :)
scaling stack contents :)
scaling replacing etc. :)
scaling cfg line size :)
scaling FS and FW properly :)
Scaling large grammars - fs, fw, pt, ll1 LOW :)
visualising with tokens :)
check epsilons in LL(1) parsing video MED :)
long names look weird in parsing vids - place nicely :)
message formatting going over lines thanks to \
    -> Loading the CFG file failed with "file does not         exist" :)
"""

"""
TODO - DEVELOPMENT

TESTING
get lots of test cases written

Get parsing colours to match LL(1) tokens   LOW
implement semantic analysis HIGH

RuntimeWarning: invalid value encountered in double_scalars
original tokens not showing at end of ll1 parsing manim

token colour coding

tree arranging to the right

LATEX

GRAMMARS
validate grammars and language spec MED

CLI
- some terminals missing regex error - investigate MED
- Notes on regex spec - necessary?  MED

""" 

"""
TODO - INTEGRATION 
start dsl tool from the typer app HIGH
""" 

"""
TODO - DETAILS LOW

remove debugging output
generate tree PNG for export

Neaten up cli_helper parsing code
Code style choices
gray lines for tables

FadeIn mathtex error alpha / 0
""" 

"""
TODO - ADMIN LOW
complete documentation
- type hints
- function return types

how to autogenerate documentation

README 
- better installation guidelines
clean up code   
clean git repo

PAPER
- write and edit draft

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

# Find First(α) and for each terminal in First(α), make entry A –> α 
# in the table.
# If First(α) contains ε (epsilon) as terminal than, find the Follow(A) 
# and for each terminal in Follow(A), make entry A –> α in the table.
# If the First(α) contains ε and Follow(A) contains $ as terminal, then 
# make entry A –> α in the table for the $. 

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
Sound may get corrupted when animation is cancelled before it is finished 
- so it can't clear the cache
Known issues:
- No sound: clear partial movie directory and restart.
"""