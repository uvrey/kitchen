""" Generates semantic analysis. """
# kitchen/backend/type_check.py

import re
from symtable import Symbol
from tracemalloc import start
import anytree
from anytree.exporter import DictExporter
from collections import OrderedDict
import pandas as pd
import manim as m
import networkx as nx
import typer

from kitchen.helpers import display, sounds, lang_spec, config
from kitchen.manim import m_general as mg, m_parser as mp, m_parse_table as mpt
from kitchen import CFG_SCALE_HEIGHT, RE_NONTERMINAL, CFG_SCALE_WIDTH, RE_TERMINAL

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
        sem_title = mg.get_title_mobject("Semantic Analysis") 

        # show the token stream
        self.m_tok = {}
        self.m_tok_gp = m.VGroup()
        self.m_tok_gp.add(m.Tex("Token stream: ")).scale(0.5)

        for t in self.tokens:
            try:
                tex = m.MathTex("\\text{"+t.type+"}").scale(0.5)
                self.m_tok_gp.add(tex)
                self.m_tok[t.type] = tex
            except:
                tex = m.MathTex("\\text{"+t+"}").scale(0.5)
                self.m_tok_gp.add(tex)
                self.m_tok[t] = tex
        self.m_tok_gp.arrange(m.RIGHT)

        # show the input stream
        self.m_inp = {}
        self.m_inp_gp = m.VGroup()
        self.m_inp_gp.add(m.Tex("Input stream: ")).scale(0.5)

        for t in self.tokens:
            try:
                tex = m.MathTex("\\text{"+t.value+"}").scale(0.5)
                self.m_inp_gp.add(tex)
                self.m_inp[t.type] = tex
            except:
                tex = m.MathTex("\\text{"+t+"}").scale(0.5)
                self.m_inp_gp.add(tex)
                self.m_inp[t] = tex
        self.m_inp_gp.arrange(m.RIGHT)
        self.m_inp_gp.next_to(self.m_tok_gp, m.DOWN)

        # show parsing direction
        arr = m.Arrow(start=3*m.RIGHT, end=3*m.LEFT, color=config.\
            get_opp_col(), buff = 1)
        arr.to_edge(m.DOWN)
        arr_caption = m.Tex("Parsing direction").scale(0.7)
        arr_caption.next_to(arr, m.UP)

        # sets the stage
        self.play(
            sem_title.animate.to_edge(m.UP),
            self.m_tok_gp.animate.to_edge(m.RIGHT).shift(m.UL),
            m.Create(arr),
            m.Write(arr_caption)
        )

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
            col_labels=[m.Tex("Symbol", color = m.BLUE), m.Tex("Type", 
                color = m.BLUE)],
            top_left_entry=m.Star().scale(0.3),
            include_outer_lines=False,
            line_config={"stroke_width": 1, "color": m.BLUE_A})
        table.scale_to_fit_width(CFG_SCALE_WIDTH/2)
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
   
        mg.display_msg(self, ["We traverse the parse tree obtained ", \
        "from parsing the given token stream."], script = "Let us traverse" + 
        " the parse tree.")

        for node in anytree.PreOrderIter(self.root):
            try:
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

                        if re.match(RE_TERMINAL, node.id):
                            sounds.add_sound_to_scene(self, sounds.FLASH)
                            self.play(
                                m.Flash(v, line_length=0.4,
                                num_lines=30, color=m.BLUE,
                                flash_radius=0.3,
                                time_width=0.3),
                            )

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
                    self.fade_in_table()
            except:
                self._call_error("Cannot semantically analyse only "+
                    "a token stream.")
                return
        
        sounds.add_sound_to_scene(self, sounds.SUCCESS)
        mg.display_msg(self, ["Semantic analysis complete!"], script = 
        "Semantic analysis complete! Here is the final symbol table.")

        self.fade_in_table(fade_out = False)
        self.print_symbol_table()

    def replace_entry(self):
        new_contents = []
        for i in range(len(self.symbol["Symbol"])):
            new_contents.append([self.symbol["Symbol"][i], self.symbol["Type"][i]])
        
        new_table = self._update_symbol_table(new_contents)
        old_table = self.table
        self.play(m.Transform(old_table, new_table))
        self.table = new_table
        self.play(
            m.Circumscribe(self.table.get_rows()[len(new_contents)], 
            color = m.BLUE)
            )
        self.play(
            m.FadeOut(old_table)
        )

    def get_str(self, index, new_item):
        old_string = self.symbol[index]
        if old_string == []:
            return new_item
        else:
            new_str = "".join(old_string) + "\n" + new_item
            display.fail_secho(new_str)
            return new_str
    
    def fade_in_table(self, fade_out = True):

        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.get_theme_col(), 
        fill_opacity=0.95)

        st_title = mg.get_title_mobject("Symbol table")
        st_title.to_edge(m.UP)

        self.play(
            m.FadeIn(rect),
        )

        sounds.narrate("Let's add terminal " + 
        self.symbol["Symbol"][-1] + " to the symbol table.", self)

        self.play(
            m.FadeIn(st_title),
            m.FadeIn(self.table)
        )
        
        self.replace_entry()

        if fade_out:
            self.play(
                m.FadeOut(st_title),
                m.FadeOut(rect),
            )

    def print_symbol_table(self):
        """Displays the symbol table.
        """        
        display.info_secho("Symbol Table:")
        df = pd.DataFrame.from_dict(self.symbol).to_markdown(index = False)
        display.structure_secho(df)
