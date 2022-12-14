""" Generates semantic analysis. """
# kitchen/backend/semantic.py

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

from kitchen.helpers import (
    display, 
    sounds, 
    lang_spec, 
    config
)

from kitchen.manim import (
    m_general as mg, 
)

from kitchen import (
        CFG_SCALE_HEIGHT, 
        RE_NONTERMINAL, 
        CFG_SCALE_WIDTH, 
        RE_TERMINAL,
        ERROR
)

VCONFIG = {"radius": 0.2, "color": m.BLUE_D, "fill_opacity": 1}
LCONFIG = {"vertex_spacing": (2, 1)}
ECONFIG = {"color": config.get_opp_col()}


def set_up_label(g, vertex_id, label, color = m.GRAY):
    """Creates the label for a given vertex.

    Args:
        g (Graph): The Manim Graph Mobject.
        vertex_id (str): Unique vertex identifier.
        label (_type_): _description_
        color (_type_, optional): _description_. Defaults to m.GRAY.
    """    
    # adds label above
    new_vertex = g[vertex_id]

    # fades vertex
    new_vertex.fade_to(color, alpha = 1)

  # sets label color
    if re.match(RE_TERMINAL, label):
        label_col = config.get_theme_col()
    else:
        label_col = m.WHITE

    # adds the new label above
    rendered_label = m.MathTex(
        mg.to_math_tex(label), color = label_col).scale(0.5)

    # add background of label for longer non-terminals
    if len(label) > 1:
        bg = m.Rectangle(width=rendered_label.width, 
        height=rendered_label.height, color = color)
        bg.set_fill(color, opacity=1.0)
        bg.move_to(new_vertex.get_center())
        new_vertex.add(bg)

    rendered_label.move_to(new_vertex.get_center())
    new_vertex.add(rendered_label)
    
def create_vertex(g, vertex_id, parent_id, label, color=m.GRAY,  link=True,
                epsilon = False):
    """Creates a vertex in a given Manim Graph.

    Args:
        g (Graph): Graph Mobject.
        vertex_id (str): Unique vertex identifier.
        parent_id (str): Parent identifier
        label (str): Vertex label.
        color (_type_, optional): Vertex color. Defaults to m.GRAY.
        link (bool, optional): Whether the parent and child are to 
        be linked with an edge. Defaults to True.

    Returns:
        Dot: Manim representation of a Graph vertex.
    """    
    global m
    if epsilon:
        pos = g[parent_id].get_center() + 0.5*m.DOWN
    else:
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

def reset_g(self, g, root):
    """Resets the graph layout.

    Args:
        g (Graph): Graph Mobject.
        root (str): Identifier of the root vertex.
    """    

    self.play(
        g.animate.change_layout(
            "tree",
            root_vertex=root,
            layout_config = LCONFIG,
        ),
    )

class MSemanticAnalyser(m.Scene):
    def setup_manim(self, cfg, root, inp, spec):
        """Initialises the SemanticAnalyser Manim Scene.

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
        mg.set_up_token_colour(self)
        self.tok_cols = []
        if self.tokens != ERROR:
                # associate a colour for each token
                for t in self.tokens:
                    self.tok_cols.append(mg.get_token_colour(self))


    def check_for_epsilons(self, g):
        """Checks if any non-terminals lead to epsilon and add this connection,
        only if the node is on the graph. 

        Args:
            g (Graph): Graph MObjects.

        Returns:
            int: Status code.
        """        
        # notify user
        mg.display_msg(self, ["We can now check if any","productions derived ", 
        "\\varepsilon."], script = "Let's check if " +
        "any productions derived epsilon.")

        # look for any epsilons that came before and add.
        for node in self.root.descendants:
            if re.match(RE_NONTERMINAL, node.id):
                if len(node.children) == 0 and "#" in \
                self.cfg.first_set[node.id]:    
                    v_id = node.id + "_#"
                    if v_id in self.vertex_ids:
                        v_id = node.id + "_#_" + str(self.id_count)

                    mg.display_msg(self, [node.id + " derives \\varepsilon."],
                    script = node.id + " derives \\varepsilon.")
                    new_node = anytree.Node("#", parent=node, id= "#", 
                    token = None, parent_id = node.vertex_id, vertex_id =
                    v_id)
                    new_vertex = create_vertex(g, new_node, r'\varepsilon', 
                    color = m.GRAY, epsilon= True)
                    self.play(m.FadeIn(new_vertex))

    def construct(self):
        """Constructs the semantic analysis scene.
        """        
        # play the intro      
        mg.display_msg(self, ["Semantic Analysis checks that a token stream",
        "is placed in the right context.", "Here, identifiers must be immutable",
        "and we can't use them until they", "have been assigned."], central = \
        True)
        mg.display_msg(self, ["Please note: If a non-terminal remains as a",
         "leaf at the end of parsing,", "it derives epsilon."], central = \
        True)
        mg.display_msg(self, ["Let's begin", "Semantic Analysis"], script = "Let's " +
        " begin semantic analysis.", central = True)
        mg.display_msg(self, ["We begin by traversing the tree we got when ",\
        " parsing the token stream."], script = "We begin by traversing the "+
        "tree we got when parsing the token stream.", central = True)

        # draws follow set title
        sem_title = mg.get_title_mobject("Semantic Analysis") 

        # show the token stream
        self.m_tok = []
        self.m_tok_gp = m.VGroup()
        self.m_tok_gp.add(m.Tex("Token stream: ", color = config.\
            get_opp_col()).scale(0.5))

        for t in self.tokens:
            try:
                tex = m.MathTex("\\text{"+t.type+"}", color = config.\
                    get_opp_col()).scale(0.5)
                self.m_tok_gp.add(tex)
                self.m_tok.append(tex)
            except:
                tex = m.MathTex("\\text{"+t+"}").scale(0.5)
                self.m_tok_gp.add(tex)
                self.m_tok.append(tex)
        self.m_tok_gp.arrange(m.RIGHT)
        self.m_tok_gp.scale_to_fit_width(5*CFG_SCALE_WIDTH/12)

        # show the input stream
        self.m_inp = []
        self.m_inp_gp = m.VGroup()
        self.m_inp_gp.add(m.Tex("Input stream: ", color = config.\
            get_opp_col())).scale(0.5)

        for t in self.tokens:
            try:
                tex = m.MathTex("\\text{"+t.value+"}", color = config.\
                    get_opp_col()).scale(0.5)
                self.m_inp_gp.add(tex)
                self.m_inp.append(tex)
            except:
                tex = m.MathTex("\\text{"+t+"}").scale(0.5)
                self.m_inp_gp.add(tex)
                self.m_inp.append(tex)
        self.m_inp_gp.arrange(m.RIGHT)
        self.m_inp_gp.scale_to_fit_width(5*CFG_SCALE_WIDTH/12)
        
        # show parsing direction
        arr = m.Arrow(start=3*m.RIGHT, end=3*m.LEFT, color=config.\
            get_opp_col(), buff = 1)
        arr.to_edge(m.DOWN)
        arr_caption = m.Tex("Parsing direction", color = config.\
            get_opp_col()).scale(0.7)
        arr_caption.next_to(arr, m.UP)

        # sets the stage
        self.play(
            sem_title.animate.to_edge(m.UP),
            self.m_tok_gp.animate.to_edge(m.RIGHT).shift(m.UL+m.UP),
            self.m_inp_gp.animate.to_edge(m.LEFT).shift(m.UR+ m.UP),
            m.Create(arr),
            m.Write(arr_caption)
        )

        # # create the table
        self.table = self._update_symbol_table([[".", "."]])

        # create the manim graph
        start_symbol = self.cfg.start_symbol
        g = m.Graph([start_symbol], [], vertex_config=VCONFIG,
            labels = False, label_fill_color=config.get_opp_col())

        set_up_label(g, start_symbol, start_symbol, m.BLUE_D)
        reset_g(self, g, start_symbol)

        # start semantic analysis
        self.init_analysis(start_symbol, g, True)

    def _update_symbol_table(self, contents):
        """Creates an updated symbol table.

        Args:
            contents (list): New contents of the symbol table. 

        Returns:
            Table: Manim Table
        """        
        table = m.Table(
            contents,
            col_labels=[m.Tex("Symbol", color = m.BLUE_D), m.Tex("Type", 
                color = m.BLUE_D)],
            top_left_entry=m.Star().scale(0.3),
            include_outer_lines=False,
            line_config={"stroke_width": 1, "color": m.BLUE_A})

        table.fade_to(config.get_opp_col(), alpha = 1)
        table.get_col_labels().fade_to(color=m.BLUE_D, alpha=1)

        table.scale_to_fit_width(CFG_SCALE_WIDTH/2)
        if table.height > CFG_SCALE_HEIGHT:
            table.scale_to_fit_width(CFG_SCALE_HEIGHT)
        return table

    def _call_error(self, msg = ""):
        """Displays an error when encountered in the type-checking process.

        Args:
            msg (str, optional): Details. Defaults to "".
        """        
        mg.display_msg(self, ["Type Error: ", msg], script = "We have a "
        + " semantic error. " + msg, error = True)
        display.fail_secho("Type Error: "+ msg)
        self.print_symbol_table()
        return 

    def init_analysis(self, start_symbol, g, start):
        """Analyses a given input based on two basic semantic rules:
           Variable uniqueness and mutability.
        """        
        lhs = True
        lh_type = None
        t_index = 0
        for node in anytree.PreOrderIter(self.root):
            try:
                # draw manim vertex
                if node.id == start_symbol and start:
                    start = False
                else:
                    try: 
                        if re.match(RE_TERMINAL, node.id):
                            tok_col =  self.tok_cols[t_index]
                        else:
                            tok_col = m.GRAY
                        v = create_vertex(g, node.vertex_id, node.parent_id, 
                        node.id, tok_col)
                        sounds.add_sound_to_scene(self, sounds.CLICK)
                        self.play(m.FadeIn(v))

                        reset_g(self, g, start_symbol)

                        if re.match(RE_TERMINAL, node.id):
                            sounds.add_sound_to_scene(self, sounds.TWINKLE)

                            # highlight the terminal, its input and its token
                            self.play(
                                m.Flash(v, line_length=0.3,
                                num_lines=20, color=self.tok_cols[t_index],
                                flash_radius=0.3,
                                time_width=0.3),
                                m.Flash(self.m_inp[t_index], 
                                line_length=0.15,
                                num_lines=20, color=self.tok_cols[t_index],
                                flash_radius=0.1,
                                time_width=0.3),
                                m.Flash(self.m_tok[t_index], 
                                line_length=0.15,
                                num_lines=20, color=self.tok_cols[t_index],
                                flash_radius=0.1,
                                time_width=0.3),
                            )

                            # highlight the input and token stream
                            self.play(
                                m.FadeToColor(self.m_tok[t_index], 
                                color = self.tok_cols[t_index]),
                                m.FadeToColor(self.m_inp[t_index], 
                                color = self.tok_cols[t_index]),
                            )
                            
                            if node.token.type != node.token.value:
                                mg.display_msg(self, ["We matched a terminal"+
                                " that", "may be an operator."], script = 
                                "We matched a terminal that"+
                                " may be an operator.")
                                self.wait()
                            else:
                                mg.display_msg(self, ["We matched a terminal!"],
                                script = "We matched a terminal!")
                            t_index = t_index + 1

                        self.wait()

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
                                    self._call_error("The symbol " + 
                                    node.token.value + " has already been " + 
                                    "defined.")
                                    return
                                else:
                                    lh_type = node.token.type
                            else:
                                lhs = False
                        
                        if node.token.value != node.token.type:
                            self.symbol['Symbol'].append(node.token.value)
                            self.symbol['Type'].append(node.token.type)
                        self.fade_in_table()
            except:
                self._call_error("Cannot semantically analyse only "+
                    "a token stream.")
                return

        
        self.check_for_epsilons(g)
        sounds.add_sound_to_scene(self, sounds.SUCCESS)
        mg.display_msg(self, ["Semantic analysis complete!"], script = 
        "Semantic analysis complete! That was a valid input. Here is " +
        "the final symbol table.")
        self.fade_in_table(fade_out = False, end = True)
        self.print_symbol_table()

    def replace_entry(self, end = False, fade_out = True):
        """Transforms the symbol table as more rows are added to it.

        Args:
            end (bool, optional): Whether this is the last time the
            table is shown in the analysis. Defaults to False.
        """        
        new_contents = []
        for i in range(len(self.symbol["Symbol"])):
            new_contents.append([self.symbol["Symbol"][i], self.symbol["Type"][i]])
        
        new_table = self._update_symbol_table(new_contents)
        old_table = self.table
        self.play(m.Transform(old_table, new_table))
        self.table = new_table

        if not end:
            self.play(
                m.Circumscribe(self.table.get_rows()[len(new_contents)], 
                color = m.BLUE_D)
                )

        if fade_out:
            self.play(
                m.FadeOut(old_table)
            )
    
    def fade_in_table(self, fade_out = True, end = False):
        """Fades in the symbol table for display.

        Args:
            fade_out (bool, optional): Whether the table should
            fade out again once having been shown. Defaults to True.
            end (bool, optional): Whether the symbol table is being
            displayed at the end of the analysis process. Defaults to False.
        """        

        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.get_theme_col(), 
        fill_opacity=0.95)

        st_title = mg.get_title_mobject("Symbol table")
        st_title.to_edge(m.UP)

        self.play(
            m.FadeIn(rect),
        )

        if not end:
            sounds.narrate("Let's add terminal " + self.symbol["Type"][-1] +
            " with value " + self.symbol["Symbol"][-1] + " to the " +
            "symbol table.", self)

            self.wait()

        self.play(
            m.FadeIn(st_title),
            m.FadeIn(self.table)
        )
        
        self.replace_entry(end, fade_out)

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
