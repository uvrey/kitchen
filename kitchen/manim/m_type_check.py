""" Generates semantic analysis. """
# kitchen/backend/type_check.py

import re
from tracemalloc import start
import anytree
from anytree.exporter import DictExporter
from collections import OrderedDict
import pandas as pd
from kitchen import RE_NONTERMINAL
import manim as m
import networkx as nx
import typer

from kitchen.helpers import display, sounds, lang_spec, config
from kitchen.manim import m_general as mg, m_parser as mp, m_parse_table as mpt

VCONFIG = {"radius": 0.2, "color": m.BLUE, "fill_opacity": 1}
LCONFIG = {"vertex_spacing": (2.5, 1)}
ECONFIG = {"color": config.get_opp_col()}


def set_up_label(g, vertex_id, label, color = m.GRAY):
    # add label above
    new_vertex = g[vertex_id]

    # fade vertex
    new_vertex.fade_to(color, alpha = 1)

    # add the new label above
    rendered_label = m.MathTex(
        mg.to_math_tex(label), color = config.get_opp_col())\
            .scale(0.5)
    rendered_label.move_to(new_vertex.get_center())
    new_vertex.add(rendered_label)
    
def create_vertex(g, vertex_id, parent_id, label, color=m.GRAY,  link=True):
    global m
    display.info_secho("creating node between " + vertex_id + " and " + 
        parent_id)
    pos = g[parent_id].get_center() + m.DOWN
    v = g._add_vertex(
        vertex_id, vertex_config={"color": color}, position=pos)
    v.fill_colour = color
    
    set_up_label(g, vertex_id, label, color)

    if link:
        g._add_edge(
            [parent_id, vertex_id], edge_config={"color": \
                config.get_opp_col()})

    return v

def reset_g(self, g, root, anim=[]):
    for a in anim:
        self.play(a)

    self.play(
        g.animate.change_layout(
            "tree",
            root_vertex=root,
            layout_config = LCONFIG,
        ),
    )


class MSemanticAnalyser(m.Scene):
    def setup_manim(self, cfg, root, inp, spec):
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
        self.inp_list = lang_spec.clean_inp_stream(inp.split(" "))
        self.tokens = mg.get_tokens_from_input(inp, spec)

        # mg.set_up_token_colour(self)
        # self.tok_cols = []

        # # associate a colour for each token
        # for t in self.tokens:
        #     self.tok_cols.append(mg.get_token_colour(self))
       


    # shows the input stream and its association with the token stream
    def intro(self):
        # introducing the input
        title = m.Tex(r"Input to be parsed:")
        sounds.narrate("Let's parse this input.", self)
        inp = m.Text(self.input, weight=m.BOLD, color=m.BLUE)
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
        # TODO fix self.intro()

        # draws follow set title
        sem_title = mg.get_title_mobject("semantic analysis") 

        # show the token stream
        self.m_tok = {}
        self.m_tok_gp = m.VGroup()
        self.m_tok_gp.add(m.Tex("Token stream: ")).scale(0.5)

        for t in self.tokens:
            try:
                tex = m.MathTex("\\text{"+t.value+"}").scale(0.5)
                self.m_tok_gp.add(tex)
                self.m_tok[t.type] = tex
            except:
                tex = m.MathTex("\\text{"+t+"}").scale(0.5)
                self.m_tok_gp.add(tex)
                self.m_tok[t] = tex
        self.m_tok_gp.arrange(m.RIGHT)

        # sets the stage
        self.play(
            sem_title.animate.to_edge(m.UP),
            self.m_tok_gp.animate.to_edge(m.RIGHT).shift(m.UL)
        )

        sounds.narrate("Parsing gave this parse tree.", self)

        # create the table
        self.table = self._update_symbol_table([[".", "."]])

        # create the manim graph
        start_symbol = self.cfg.start_symbol
        g = m.Graph([start_symbol], [], vertex_config=VCONFIG,
            labels = False, label_fill_color=config.get_opp_col())

        set_up_label(g, start_symbol, start_symbol, m.BLUE)
        reset_g(self, g, start_symbol)

        # start semantic analysis
        self.init_analysis(start_symbol, g)


    def _update_symbol_table(self, contents):
        table = m.Table(
            contents,
            col_labels=[m.Tex("Symbol", color = m.BLUE), m.Tex("Type", color = m.BLUE)],
            top_left_entry=m.Star().scale(0.3),
            include_outer_lines=False,
            line_config={"stroke_width": 1, "color": m.BLUE_A})
        return table


    def _call_error(self, msg = ""):
        """Display an error in the type-checking process.

        Args:
            msg (str, optional): Details. Defaults to "".
        """        
        mg.display_msg(self, ["Type Error: ", msg], script = msg)
        display.fail_secho("Type Error: "+ msg)
        self.print_symbol_table()
        return 

    def init_analysis(self, start_symbol, g):
        """Analyses a given input based on two basic semantic rules:
           Variable uniqueness and mutability.
        """        
        lhs = True
        lh_type = None
   
        for node in anytree.PreOrderIter(self.root):
           # try: TODO
            # draw manim vertex
            if node.id != start_symbol:
                try: 
                    if re.match(RE_NONTERMINAL, node.id):
                        v_id = node.parent.id + "_" + node.id
                    else:
                        v_id = node.parent.id + "_" + node.token.value
                    if node.parent.id != start_symbol:
                        p_id = node.parent.parent.id + "_" + node.parent.id
                    else:
                        p_id = start_symbol 
                    v = create_vertex(g, v_id, p_id, node.id, m.BLUE)
                    sounds.add_sound_to_scene(self, sounds.CLICK)
                    self.play(m.FadeIn(v))
                    reset_g(self, g, start_symbol)
                except: 
                    pass

            if node.token != None:
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
                self.fade_in_table(node.token.value, node.token.type)
            # except:
            #     self._call_error("Cannot semantically analyse only "+
            #         "a token stream.")
            #     return
        self.print_symbol_table()

    def replace_entry(self):
        new_contents = []
        for i in range(len(self.symbol["Symbol"])):
            new_contents.append([self.symbol["Symbol"][i], self.symbol["Type"][i]])

        typer.echo("new contents:")
        typer.echo(new_contents)
        
        new_table = self._update_symbol_table(new_contents)
        self.play(m.Transform(self.table, new_table), m.FadeOut(self.table))
        self.table = new_table

    def get_str(self, index, new_item):
        old_string = self.symbol[index]
        if old_string == []:
            return new_item
        else:
            new_str = "".join(old_string) + "\n" + new_item
            display.fail_secho(new_str)
            return new_str
    
    def fade_in_table(self, value, type):

        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.get_theme_col(), 
        fill_opacity=0.95)

        st_title = mg.get_title_mobject("Symbol table")
        st_title.next_to(self.table, m.UP)

        self.play(
            m.FadeIn(rect),
        )

        sounds.narrate("Let's add to the symbol table.", self)

        self.play(
            m.FadeIn(st_title),
            m.FadeIn(self.table)
        )
        
        self.replace_entry()

        self.wait()

        self.play(
            m.FadeOut(self.table),
            m.FadeOut(st_title),
            m.FadeOut(rect),
        )

    def print_symbol_table(self):
        """Displays the symbol table.
        """        
        display.info_secho("Symbol Table:")
        df = pd.DataFrame.from_dict(self.symbol).to_markdown(index = False)
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