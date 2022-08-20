
""" Generates a visualisation of the parse tree calculation. """
# kitchen/manim/m_parse_tree.py

import manim as m
import re
import typer
import anytree

from kitchen import ( 
    RE_TERMINAL, 
    RE_NONTERMINAL, 
    RE_PRODUCTION, 
    SUCCESS
)

from kitchen.backend import stack
from kitchen.helpers import lang_spec, config, sounds, error, display
from kitchen.manim import m_general as mg

VCONFIG = {"radius": 0.25, "color": m.BLUE, "fill_opacity": 1}
VCONFIG_TEMP = {"radius": 0.25, "color": m.GRAY}
LCONFIG = {"vertex_spacing": (0.5, 1)}
ECONFIG = {"color": config.config.get_opp_col()}
ECONFIG_TEMP = {"color": m.GRAY, "fill_opacity": 0.7}
V_LABELS = {}

def create_tokens(tokens):
    # Write equations
    token_gp = []
    for t in tokens:
        token_gp.append(m.MathTex("\\text{"+t+"}"))
    return token_gp

def get_parent_id(parent, start_symbol):
    if parent.parent != None:
        return get_vertex_id(parent.id, parent.parent.id, start_symbol)
    else:
        return parent.id

def create_v_if_exists(scene, g, start_symbol, vertex_id, v_name, parent_id):
    try:
        vertex = g[vertex_id]

    except KeyError:
        # create the new vertex only if it doesn't exist already
        v = create_vertex(
            g, vertex_id, parent_id, v_name)
        reset_g(scene, g, start_symbol)

def get_vertex_id(vertex, parent, start_symbol):
    if vertex == start_symbol:
        return vertex
    else:
        if parent == start_symbol:
            return start_symbol + "_" + vertex
        else:
            return parent + "_" + vertex

def create_vertex(g, vertex_id, parent_id, label, color=m.GRAY,  link=True):
    global m
    V_LABELS[vertex_id] = label
    pos = g[parent_id].get_center()+m.DOWN
    v = g._add_vertex(
        vertex_id, vertex_config={"color": color}, position=pos)
    v.fill_colour = color

    if link:
        g._add_edge(
            [parent_id, vertex_id], edge_config={"color": config.config.get_opp_col()})
    return v

def reset_g(self, g, root, anim=[]):
    for a in anim:
        self.play(a)

    self.play(
        g.animate.change_layout(
            "tree",
            root_vertex=root,
        ),
    )

# general function for mapping elements in some list to another list
def map_token_lists(self, lhs, rhs):
    # create token group
    map_group = m.VGroup()

    # map the tokens
    for index, il in enumerate(lhs, start=0):
        small_group = m.VGroup()
        lh = m.Text(il, slant=m.ITALIC, weight=m.BOLD)
        arrow = m.Arrow(start=m.LEFT, end=m.RIGHT, buff=0).next_to(lh, m.RIGHT)
        rh = m.Text(rhs[index], weight=m.BOLD, color=mg.get_token_colour(self)).next_to(
            arrow, m.RIGHT)
        small_group.add(lh, arrow, rh)
        map_group.add(small_group)
    map_group.arrange(m.DOWN, aligned_edge = m.LEFT)
    return map_group

class MParseTree(m.Scene):

    def setup_manim(self, inp, cfg, spec = None):
        """Sets up the structures which the animation will make use of.

        Args:
            inp (str): Input to be parsed.
            cfg (ContextFreeGrammar): Loaded CFG.
            spec (Specification, optional): Specification Object, which contains the language specification. Defaults to None.
        """     
        self.inp = inp
        self.inp_list = lang_spec.clean_inp_stream(inp.split(" "))
        self.spec = spec
        self.tokens = mg.get_tokens_from_input(inp, spec)
        mg.set_up_token_colour(self)
        self.tok_cols = []

        # associate a colour for each token
        for t in self.tokens:
            self.tok_cols.append(mg.get_token_colour(self))

        self.cfg = cfg
        self.nts = sorted(cfg.nonterminals)
        self.ts = sorted(cfg.terminals)

    def construct(self):
        self.vis_parse_ll1(self.inp, self.tokens)
    
    def tear_down(self):
        self.mtable = None
        self.root = None
        mg.clear_narrs()

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
                        for t in map_token_lists(self, self.inp_list, lang_spec.get_token_format(self.tokens, types=True, as_list=True)))),
        )
        self.wait()

        # fades the scene out
        self.play(
            *[m.FadeOut(mob)for mob in self.mobjects]
        )
        
    def init_m_table(self, row_vals, row_labels, col_labels):
        row_labels = row_labels
        col_labels = col_labels

        table = m.MathTable(
            row_vals,
            row_labels=[m.MathTex(mg.to_math_tex(rl)) for rl in row_labels],
            col_labels=[m.MathTex(mg.to_math_tex(cl)) for cl in col_labels],
            include_outer_lines=True)

        # Table
        lab = table.get_labels()
        lab.set_color(m.LIGHT_GRAY)
        table.get_horizontal_lines()[2].set_stroke(width=8, color=m.LIGHT_GRAY)
        table.get_vertical_lines()[2].set_stroke(width=8, color=m.LIGHT_GRAY)
        return table

    def init_m_ll1_parsetable(self):
        """Sets up the parse table structure without generating an animation_summary_
        """        
        # draw establishing table animations
        row_labels = self.nts
        col_labels = mg.ts_m_epsilon(self)

        # gets the row values
        row_vals = self.get_row_contents()

        self.mtable = self.init_m_table(
            row_vals, row_labels, col_labels)

        self.mtable.get_row_labels().fade_to(color=m.RED, alpha=1)
        self.mtable.get_col_labels().fade_to(color=m.TEAL, alpha=1)

    # get the rows as a list of lists
    def get_row_contents(self):
        row_vals = []
        for n in self.nts:
            row = []
            for t in self.ts:
                try:
                    item = self.cfg.parsetable.pt_dict[n][t]
                    typer.echo(item)
                    if item != None:
                        if re.match(RE_TERMINAL, item):
                            row.append(item)
                        else:
                            tmp = mg.to_tex(item)
                            row.append(tmp)
                    else:
                        row.append("")
                except KeyError:
                    row.append("")
            row_vals.append(row)
        return row_vals

    def _fade_in_mtable(self, highlight = False, row = -1, col = -1, first_time = False):
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.get_theme_col(), fill_opacity=0.9)

        pt_title = mg.get_title_mobject("Parse table")
        pt_title.next_to(self.mtable, m.UP)

        self.play(
            m.FadeIn(rect),
        )

        if first_time:
            sounds.narrate("Here is the parse table for this grammar", self)

        self.play(
            m.FadeIn(pt_title),
            m.FadeIn(self.mtable)
        )
        self.wait()
        self.wait()

        if highlight:
            tmp_tab = self.mtable
            t =  self.mtable.get_entries_without_labels([row, col])
            self.play(
                m.Indicate(t, color = m.BLUE),
                m.Circumscribe(t, color = m.BLUE),
            )

        self.play(
            m.FadeOut(self.mtable),
            m.FadeOut(pt_title),
            m.FadeOut(rect),
        )

# Parse LL(1) in the CLI
    def vis_parse_ll1(self, input, tokens):
        global V_LABELS
        global VCONFIG
        global m

        # set up the stack and the parsing table
        self.s = stack.Stack(self, m.DR, 5)
        self.init_m_ll1_parsetable()
        self.mtable.scale_to_fit_height(m.config["frame_height"]/2)
        V_LABELS = {}

        # add start symbol to the stack
        start_symbol = self.cfg.start_symbol
        self.s.stack.append(start_symbol)
        self.root = anytree.Node(start_symbol, id=start_symbol,
                         manim=m.MathTex(start_symbol))

        # copy the tokens
        original_tokens = tokens[:]

        # initialise a way to track the parent nodes
        self.parents = []
        self.intro()

        # draw LL(1) representation title
        ll1_title = mg.get_title_mobject("LL(1) parsing")
        mg.display_msg(self, ["LL(1) Parsing Algorithm"], raw_msg = "Let's apply the L L 1 parsing algorithm")
        keys = mg.get_manim_cfg_group(self).to_edge(m.DOWN)

        # create the input group here
        # BUG inputs could have the same names as each other
        m_tok = {}
        m_tok_gp = m.VGroup()
        m_tok_gp.add(m.Tex("Token stream: ")).scale(0.7)
        for t in tokens:
            try:
                tex = m.MathTex("\\text{"+t.value+"}")
                m_tok_gp.add(tex)
                m_tok[t.type] = tex
            except:
                tex = m.MathTex("\\text{"+t+"}")
                m_tok_gp.add(tex)
                m_tok[t] = tex
        m_tok_gp.arrange(m.RIGHT)

        # show the parsing table
        self._fade_in_mtable(first_time=True)

        # set the stage
        self.play(
            ll1_title.animate.to_edge(m.UP),
            m_tok_gp.animate.to_edge(m.UR).shift(m.DOWN+m.LEFT),
            self.s.mstack.animate.to_edge(m.LEFT).shift(
                m.DOWN+m.RIGHT).align_to(self.mtable.get_center),
        )

        # create our first label
        V_LABELS[start_symbol] = start_symbol
        g = m.Graph([start_symbol], [], vertex_config=VCONFIG,
                  labels=V_LABELS, label_fill_color=m.BLACK)

        g.to_edge(m.UP).shift(m.DOWN)
        self.add(g)
        self.root.manim.move_to(g[start_symbol].get_center())
         
        # begin parsing
        while self.s.stack != []:
            # in case we run out of input before the stack is empty
            if tokens == []:
                sounds.add_sound_to_scene(self, sounds.FAIL)
                if re.match(RE_TERMINAL, self.s.stack[-1]):
                    error.ERR_parsing_error(self.root, "Expected " + self.s.stack[-1]+".")
                    error.ERR_manim_parsing_error(self,  ["Expected `" + self.s.stack[-1] + "'", "Parsing unsuccessful."], raw_msg = "We expected to see " + self.s.stack[-1]  + " so parsing is unsuccessful.")
                else:
                    error.ERR_parsing_error(self.root)
                    error.ERR_manim_parsing_error(self, ["Parsing unsuccessful. "], raw_msg = "Parsing unsuccessful.")
                return

            top = self.s.stack[-1]
            try:
                next = tokens[0].type
            except:
                next = tokens[0]

            # draw initial node if top is start symbol
            if re.match(RE_TERMINAL, top) or top == "$":

                if top == next:
                    anims = []
                    tokens = tokens[1:]

                    sounds.narrate("The next token " + next + " matches the top of the stack!", self)
                    self.wait()

                    # highlight parents
                    if self.parents == []:
                        parent = None

                    # pops appropriately
                    if self.parents != []:
                        popped = self.parents.pop()
                        parent = None

                        # always pop again if an epsilon was encountered
                        if self.parents != []:
                            parent = self.parents[-1]
                            done = False

                            i = 1
                            while not done:
                                p = self.parents[-i]
                                if re.match(RE_NONTERMINAL, p.id):

                                    # if we have encountered the first set which the production can fall under
                                    if popped.id in self.cfg.first_set[p.id]:
                                        parent = p
                                        # remove children if they were previously added
                                        if p.height != 0:
                                            p.children = []
                                        anytree.Node(
                                            popped.id, parent=p, id=popped.id, manim=m.Tex(popped.id, color = m.BLACK))

                                        # check for epsilons
                                        rhs = self.parents[-i + 1:]
                                        for r in rhs:
                                            if re.match(RE_NONTERMINAL, r.id) and r.id != p.id and r.height == 0:
                                                if "#" in self.cfg.first_set[r.id]:
                                                    new_node = anytree.Node(
                                                        "#", parent=r, id="eps", manim=m.MathTex(r'\varepsilon'))
                                                    vertex_id = r.id + "_" + new_node.id
                                                    parent_id = r.id
                                                    if r.id != start_symbol:
                                                        parent_id = r.parent.id + "_" + r.id
                                                    v = create_vertex(
                                                        g, vertex_id, parent_id, r'\varepsilon', color = m.BLUE)
                                                    reset_g(
                                                        self, g, start_symbol)

                                        # pop as many productions off as necessary
                                        for j in range(i - 1):
                                            self.parents.pop()
                                        done = True
                                    else:
                                        i = i + 1
                                else:
                                    parent = self.root
                                    break

                    # Add new connection if it exists :)
                    typer.echo(parent)

                    if parent != None:
                        vertex_id = parent.id + "_" + top

                        if parent.id == start_symbol:
                            parent_vertex_id = parent.id
                        else:
                            parent_vertex_id = parent.parent.id + "_"+ parent.id

                        # check if we already have a vertex
                        try:
                            # get existing vertex
                            new_vertex = g[vertex_id]
                            # confirm the path by adding the colour
                            rendered_label = m.MathTex(
                                mg.to_math_tex()(top), color = m.BLACK)
                            new_vertex.fade_to(self.tok_cols[lang_spec.get_index_by_token_type(original_tokens, top)], 1)
                            rendered_label.move_to(new_vertex.get_center())
                            new_vertex.add(rendered_label)
                            
                            sounds.add_sound_to_scene(self, sounds.CLICK)
                            self.play(
                                m.Circumscribe(new_vertex, color=self.tok_cols[lang_spec.get_index_by_token_type(original_tokens, top)], shape = m.Circle),
                            )
                            try:
                                edge = g.edges[(parent_vertex_id, vertex_id)]
                                anims.append(
                                    m.FadeToColor(edge, color=config.config.get_opp_col()))
                            except:
                                pass
                        except KeyError:
                            # create and add new vertex
                            
                            new_vertex = create_vertex(
                                g, vertex_id, parent_vertex_id, vertex_id.split("_")[
                                    1].strip(), color=self.tok_cols[lang_spec.get_index_by_token_type(original_tokens, next)])
                            reset_g(self, g, start_symbol)

                        # pop off the stack and 'flash'
                        self.s.pop(anim=anims, vertex=new_vertex, matching=True, msg="\\text{Matched }" +
                                mg.to_tex(self.s.stack[-1]) + "\\text{!}")


                    # highlight the token stream line and token that we matched
                    sounds.add_sound_to_scene(sounds.YAY, self)
                    self.play(m.ApplyWave(m_tok_gp))
                    self.play(
                        m.LaggedStart(m.Indicate(m_tok[next], color=self.tok_cols[lang_spec.get_index_by_token_type(original_tokens, next)], scale_factor=1.5),
                                   m.FadeToColor(m_tok[next], color=self.tok_cols[lang_spec.get_index_by_token_type(original_tokens, next)])),
                    )

                else:
                    sounds.add_sound_to_scene(self, sounds.FAIL)
                    error.ERR_parsing_error(self.root, 
                        "Unexpected token [" + top + "]")
                    error.ERR_manim_parsing_error(self, ["Invalid input: '" + top + "'"], raw_msg = top + " leads to a parsing error, so this input is not valid." )
                    return

            elif re.match(RE_NONTERMINAL, top):
                try:
                    pt_entry = self.cfg.parsetable.pt_dict[top][next]
                    prods = pt_entry.split("->")
                    mg.display_msg(self, ["We must find the entry at ParseTable["+top+"]["+next+"]"], raw_msg = "Let's consider the parse table entry at non-terminal " + top + "'s row and terminal " + next + "'s column.")

                    # highlight parse table row
                    self._fade_in_mtable(highlight  = True, row = mg.row(self.nts, top), col = mg.col(self.ts, next))
                    
                    #  copy the cfg_line rather than manipulate it directly
                    cfg_line = self.manim_production_groups[prods[0].strip(
                    )][:]
                    cfg_line.next_to(self.s.mstack, m.DOWN).shift(
                        0.8*m.DOWN).scale(0.7)

                    self.play(
                        m.FadeIn(cfg_line)
                    )

                    # set up animations
                    popped_off = self.s.stack[-1]
                    anims = []

                    # highlight the edge and vertex if applicable to our path
                    if self.parents != []:
                        parent_id = self.parents[-1].parent.id

                        # create p_c and P_p links
                        if popped_off != start_symbol:
                            v_id = parent_id + "_" + popped_off

                            if parent_id != start_symbol:
                                parent_id = self.parents[-1].parent.parent.id + \
                                    "_" + self.parents[-1].parent.id

                            # highlight edge and vertex
                            anims = []
                            try:
                                vertex = g[v_id]
                                rendered_label = m.Tex(
                                   mg.to_tex(popped_off), color = m.BLACK)

                                # confirm the path by adding the colour
                                vertex.fade_to(m.BLUE, 1)
                                rendered_label.move_to(vertex.get_center())
                                vertex.add(rendered_label)

                                sounds.add_sound_to_scene(self, sounds.CLICK)
                                self.play(
                                    m.Circumscribe(vertex, color=m.BLUE, shape = m.Circle),
                                )
                            except:
                                pass
                                
              
                    sounds.add_sound_to_scene(self, sounds.POP)
                    self.s.pop(anim=anims,
                               msg="\\text{Replacing }" + mg.to_tex(popped_off) + "\\text{...}")

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))
                    nodes_to_append = []

                    mg.display_msg(self, [mg.to_tex(popped_off) + " is a non-terminal,", "so we can replace it with", "its sub-productions: ",  prods[1]], raw_msg="Let's replace " + popped_off + " with its sub productions")

                    for p in reversed(ps):
                        # add to the tree
                        if top == start_symbol:
                            # create the node
                            new_node = anytree.Node(
                                p, parent=self.root, id=p)
                            try:
                                vertex_id = top + "_" + p.strip()
                                vertex = g[vertex_id]

                            except KeyError:
                                # create the new vertex only if it doesn't exist already
                                vertex_id = top + "_" + new_node.id
                                v = create_vertex(
                                    g, vertex_id, start_symbol, new_node.id)
                                reset_g(self, g, start_symbol)
                        else:
                            # add connecting node if it is a non-terminal
                            if re.match(RE_NONTERMINAL, p):
                                new_node = anytree.Node(
                                    p, id=p, parent=self.parents[-1])

                                parent = self.parents[-1]
                                parent_id = get_parent_id(parent, start_symbol)
                                typer.echo(parent_id)
                                create_v_if_exists(
                                    self, g, start_symbol, parent.id + "_" + p.strip(), p.strip(), parent_id)

                            else:
                                if p != "#":
                                    new_node = anytree.Node(
                                        p, id=p, manim=m.Tex(p))

                        # we don't need to match epsilon, and we also only want non-terminals as parent nodes
                        if p != "#" and p != "$":
                            new_prod = prods[0].strip() + " -> " + p
                            self.s.push(p, mg.to_tex(new_prod))
                            nodes_to_append.append(new_node)

                        # TODO NEW! only append parents once whole list has been processed
                        for t in nodes_to_append:
                            self.parents.append(t)

                    self.play(
                        m.FadeOut(cfg_line)
                    )

                except KeyError:
                    sounds.add_sound_to_scene(self, sounds.FAIL)
                    mg.display_msg(self, ["No such entry at ParseTable[" + top + ", " + next + "].", "Invalid input: `" + next + "'"], raw_msg = next + " leads to a parsing error, so this input is not valid." )
                    error.ERR_parsing_error(self.root, 
                        "No such entry at ParseTable[" + top + ", " + next + "].")
                    return

            # transform the tree
            reset_g(self, g, start_symbol)

        # in case parsing finishes but there are still tokens left in the stack
        if len(tokens) > 0:
            sounds.add_sound_to_scene(self, sounds.FAIL)
            error.ERR_parsing_error(self.root)
            error.ERR_manim_parsing_error(self, ["The stack is not emptied,", "but parsing has concluded."], raw_msg = "Since the stack is not emptied, parsing is unsuccessful.")
            return

        # fade out the stack and transform the parse tree
        sounds.narrate("Stack emptied.", self)
        self.s.write_under_stack("\\text{Stack emptied.}")
        reset_g(self, g, start_symbol, anim=[m.FadeOut(self.s.mstack)])

        sounds.add_sound_to_scene(self, sounds.YAY)
        mg.display_msg(self, ["Successfully parsed `" + lang_spec.get_token_format(original_tokens) +
                                "'!"], raw_msg= "Parsing successful! That was a valid input.")

        display.success_secho("Successfully parsed '" + lang_spec.get_token_format(original_tokens) +
                              "'!\nParse tree:")
        display.print_parsetree(self.root)
        return SUCCESS

