
""" Generates a visualisation of the parse tree calculation. """
# kitchen/manim/m_parser.py

import manim as m
import re
import anytree
import typer

from kitchen import ( 
    CFG_SCALE_WIDTH,
    RE_TERMINAL, 
    RE_NONTERMINAL, 
    RE_PRODUCTION, 
    SUCCESS,
    ERROR
)

from kitchen.backend import stack

from kitchen.helpers import (
    lang_spec, 
    config, 
    sounds, 
    error, 
    display
)

from kitchen.manim import m_general as mg

VCONFIG = {"radius": 0.2, "color": m.BLUE_D, "fill_opacity": 1}
LCONFIG = {"vertex_spacing": (1.5, 1)}
ECONFIG = {"color": config.get_opp_col()}
ECONFIG_TEMP = {"color": m.GRAY, "fill_opacity": 0.7}
V_LABELS = {}

def create_tokens(tokens):
    # Write equations
    token_gp = []
    for t in tokens:
        token_gp.append(m.MathTex("\\text{"+t+"}", color = config.get_opp_col()))
    return token_gp

def set_up_label(g, vertex_id, label, color = m.GRAY):
    # add label above
    new_vertex = g[vertex_id]

    # fade vertex
    new_vertex.fade_to(color, alpha = 1)

    # set label color
    if re.match(RE_TERMINAL, label):
        label_col = config.get_theme_col()
    else:
        label_col = m.WHITE

    # add the new label above
    rendered_label = m.MathTex(
        mg.to_math_tex(label), color = label_col)\
            .scale(0.5)

    # add background of label for longer non-terminals
    if len(label) > 1:
        bg = m.Rectangle(width=rendered_label.width, 
        height=rendered_label.height, color = color)
        bg.set_fill(color, opacity=1.0)
        bg.move_to(new_vertex.get_center())
        new_vertex.add(bg)

    rendered_label.move_to(new_vertex.get_center())
    new_vertex.add(rendered_label)
    
def create_vertex(g, node, label, color=m.GRAY,  link=True, vertex_ids = None):
    global m

    try:
        pos = g[node.parent_id].get_center() + m.DOWN
        v = g._add_vertex(
            node.vertex_id, vertex_config={"color": color}, position=pos)
        v.fill_colour = color
        
        set_up_label(g, node.vertex_id, label, color)

        if link:
            g._add_edge(
                [node.parent_id, node.vertex_id], edge_config={"color": \
                    config.get_opp_col()})
    
        return v
    except:
        pass

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

# general function for mapping elements in some list to another list
def map_token_lists(self, lhs, rhs):
    # create token group
    map_group = m.VGroup()

    # map the tokens
    for index, il in enumerate(lhs, start=0):
        small_group = m.VGroup()
        lh = m.Tex(il, color = config.get_opp_col())
        arrow = m.Arrow(start=m.LEFT, end=m.RIGHT, buff=0)\
            .next_to(lh, m.RIGHT)
        arrow.fade_to(config.get_opp_col(), alpha = 1)
        rh = m.Tex(rhs[index], 
        color=self.tok_cols[index]).next_to(
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
            spec (Specification, optional): Specification Object, 
            which contains the language specification. Defaults to None.
        """     
        self.inp = inp
        self.inp_list = lang_spec.clean_inp_stream(inp.split(" "))
        self.spec = spec
        self.tokens = mg.get_tokens_from_input(inp, spec)
        mg.set_up_token_colour(self)
        self.tok_cols = []

        if self.tokens != ERROR:
            # associate a colour for each token
            for t in self.tokens:
                self.tok_cols.append(mg.get_token_colour(self))

        self.cfg = cfg
        self.nts = sorted(cfg.nonterminals)
        self.ts = sorted(cfg.terminals)

    def construct(self):
        self.vis_parse_ll1()
    
    def tear_down(self):
        self.mtable = None
        self.root = None
        sounds.clear_narrs()

    # shows the input stream and its association with the token stream
    def intro(self):
        # introducing the input
        title = m.Tex(r"Input to be parsed:", color = config.get_opp_col())
        sounds.narrate("Let's parse this input.", self)
        inp = m.Text(self.inp, weight=m.BOLD, color=m.BLUE_D)
        m.VGroup(title, inp).arrange(m.DOWN)
        self.play(
            m.FadeIn(title),
            m.Write(inp, shift=m.DOWN),
        )
        self.wait()

        # transforming to lexing
        transform_title = m.Tex(
            "Lexing matched the input to the following tokens:", color = \
                config.get_opp_col())
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
                        for t in map_token_lists(self, self.inp_list, 
                        lang_spec.get_token_format(self.tokens, types=True, 
                        as_list=True)))),
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
        """Sets up the parse table structure without generating an animation.
        """        
        # draw establishing table animations
        row_labels = self.nts[:]
        col_labels = self.ts[:]

        # gets the row values
        row_vals = self.get_row_contents()

        self.mtable = self.init_m_table(
            row_vals, row_labels, col_labels)
        self.mtable.fade_to(config.get_opp_col(), alpha = 1)

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
                    if item != None:
                        if re.match(RE_TERMINAL, item):
                            row.append(item)
                        else:
                            tmp = mg.to_math_tex(item)
                            row.append(tmp)
                    else:
                        row.append("")
                except KeyError:
                    row.append("")
            row_vals.append(row)
        return row_vals

    def _fade_in_mtable(self, highlight = False, row = -1, col = -1, 
        first_time = False):
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.get_theme_col(), 
        fill_opacity=0.9)

        pt_title = mg.get_title_mobject("Parse table")
        pt_title.to_edge(m.UP)

        self.play(
            m.FadeIn(rect),
        )

        if first_time:
            sounds.narrate("Here is the parse table for this grammar", self)

        if self.mtable.width > CFG_SCALE_WIDTH:
            self.mtable.scale_to_fit_width(CFG_SCALE_WIDTH)

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
                m.Indicate(t, color = m.BLUE_D),
                m.Circumscribe(t, color = m.BLUE_D),
            )

        self.play(
            m.FadeOut(self.mtable),
            m.FadeOut(pt_title),
            m.FadeOut(rect),
        )

    def check_for_epsilons(self, g):
        """Checks if any non-terminals lead to epsilon and add this connection,
        only if the node is on the graph. 

        Args:
            g (Graph): Graph MObjects.

        Returns:
            int: Status code.
        """        
        # notify user
        mg.display_msg(self, ["We can now check if any productions led ", 
        "to $\\varepsilon$, and so disappeared."], script = "Let's check if " +
        "any productions led to epsilon.")

        # look for any epsilons that came before and add.
        for node in self.root.descendants:
            if re.match(RE_NONTERMINAL, node.id):
                if len(node.children) == 0 and "#" in \
                self.cfg.first_set[node.id]:
               
                    v_id = node.id + "_#"
                    if v_id in self.vertex_ids:
                        v_id = node.id + "_#_" + str(self.id_count)

                    new_node = anytree.Node("#", parent=node, id= "#", 
                    token = None, parent_id = node.vertex_id, vertex_id =
                    v_id)
                    new_vertex = create_vertex(g, new_node, r'\varepsilon', 
                    color = m.GRAY)
                    self.play(m.FadeIn(new_vertex))
        return SUCCESS

    def _parsing_successful(self, tokens, semantic: bool, testing = False, 
        verbose = True):
        types = lang_spec.get_token_format(tokens, types=True)
        values = lang_spec.get_token_format(tokens, values=True)
        
        if not semantic:
            if testing:
                display.success_secho("Success.")
                display.structure_secho(anytree.RenderTree(self.root, 
                style= anytree.AsciiStyle()).by_attr("id"))
                return

            if verbose:
                mg.display_msg(self, ["Parsing successful!", values + 
                " is a valid input."], script = "Parsing successful. " +
                "That was a valid input.")
                display.success_secho("\nSuccessfully parsed token stream '" + 
                types + "'\nfrom input stream '" + values + 
                "'.\n\nParse tree:")
                display.print_parsetree(self.root)
        
    # Parse LL(1) in the CLI
    def vis_parse_ll1(self):
        global V_LABELS
        global VCONFIG
        global m
        self.id_count = 0
        
        if self.tokens == ERROR:
            display.fail_secho("Not all tokens from the input stream were " +
                "matched :(\nParsing failed.")
            return

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
        original_tokens = self.tokens[:]

        # set up terminal index
        t_index = 0

        # initialise a way to track the parent nodes
        self.parents = []

        # set up directory of vertex names
        self.vertex_ids = []
        self.intro()

        # draw LL(1) representation title
        ll1_title = mg.get_title_mobject("LL(1) parsing")
        mg.display_msg(self, ["LL(1) Parsing Algorithm"], script = 
        "Let's apply the L L 1 parsing algorithm")
        keys = mg.get_manim_cfg_group(self).to_edge(m.DOWN)

        # create the input group here
        m_tok = []
        m_tok_gp = m.VGroup()
        m_tok_gp.add(m.Tex("Token stream: ", color = config.get_opp_col())\
            .scale(0.5))

        for t in self.tokens:
            try:
                tex = m.MathTex("\\text{"+t.value+"}", color = config.\
                    get_opp_col()).scale(0.5)
                m_tok_gp.add(tex)
            except:
                tex = m.MathTex("\\text{"+t+"}", color = config.\
                    get_opp_col()).scale(0.5)
                m_tok_gp.add(tex)
            m_tok.append(tex)
        m_tok_gp.arrange(m.RIGHT)

        # show the parsing table
        self._fade_in_mtable(first_time=True)

        # show parsing direction
        arr = m.Arrow(start=3*m.RIGHT, end=3*m.LEFT, color=config.\
            get_opp_col(), buff = 1)
        arr.to_edge(m.DOWN)
        arr_caption = m.Tex("Parsing direction", color = config.\
            get_opp_col()).scale(0.7)
        arr_caption.next_to(arr, m.UP)

        # set the stage
        self.play(
            ll1_title.animate.to_edge(m.UP),
            m_tok_gp.animate.to_edge(m.UR).shift(m.DOWN + m.LEFT),
            self.s.mstack.animate.to_edge(m.LEFT).shift(
                m.DOWN+m.RIGHT).align_to(self.mtable.get_center),
            m.Create(arr),
            m.Write(arr_caption)
        )

        # create our first label
        g = m.Graph([start_symbol], [], vertex_config=VCONFIG,
                  labels = False, label_fill_color=config.get_opp_col())

        set_up_label(g, start_symbol, start_symbol, m.GRAY)

        self.add(g)
        self.root.manim.move_to(g[start_symbol].get_center())
         
        # begin parsing
        while self.s.stack != []:
            # check if the stack is empty before the parsing is complete
            if self.tokens == []:
                if re.match(RE_TERMINAL, self.s.stack[-1]):
                    error.ERR_parsing_error(self.root, "Expected " + 
                    self.s.stack[-1]+".")
                    error.ERR_manim_parsing_error(self,  ["Expected `" 
                    + self.s.stack[-1] + "'", "Parsing unsuccessful."], 
                    script = "We expected to see " + self.s.stack[-1]  +
                    " so parsing is unsuccessful.")
                else:
                    # parsing is successful if the remaining non-terminal may 
                    # tend to epsilon
                    if "#" in self.cfg.first_set[self.s.stack[-1]] and \
                    len(self.s.stack) == 1:
                        self.s.pop(msg = self.s.stack[-1] + r'\to \varepsilon')
                        self._parsing_successful(original_tokens, False)
                        return SUCCESS
                    # otherwise calls an error
                    error.ERR_parsing_error(self.root)
                    error.ERR_manim_parsing_error(self, \
                    ["Parsing unsuccessful. "], script = \
                    "Parsing unsuccessful.")
                return 

            top = self.s.stack[-1]
            try:
                next = self.tokens[0].type
            except:
                next = self.tokens[0]

            # draw initial node if top is start symbol
            if re.match(RE_TERMINAL, top) or top == "$":

                if top == next:
                    anims = []
                    prev_token = self.tokens[0]
                    self.tokens = self.tokens[1:]

                    sounds.narrate("The next token " + next + 
                    " matches the top of the stack!", self)
                    self.wait()

                    if self.parents != []:
                        popped = self.parents.pop()

                        # set up the terminal node
                        popped.parent = popped.tmp_parent
                        popped.token = prev_token
                        
                        # create the vertex
                        sounds.add_sound_to_scene(self, sounds.CLICK)
                        new_vertex = create_vertex(g, popped,
                                            mg.to_math_tex(popped.id), 
                                            color = self.tok_cols[t_index], 
                                            vertex_ids=self.vertex_ids)
                        self.play(m.FadeIn(new_vertex))
                        reset_g(self, g, start_symbol)

                    # if we have matched our last token
                    if len(self.tokens) == 1:
                        self.check_for_epsilons(g)

                    self.s.pop(tok_cols = self.tok_cols, ti = t_index, 
                    anim=anims, vertex=new_vertex, token = m_tok[t_index],
                    matching=True, msg=r'\text{Matched }' +
                            mg.to_tex(self.s.stack[-1]) + r'\text{!}')

                    # highlight the token stream line and token that we matched
                    sounds.add_sound_to_scene(sounds.YAY, self)
                    self.play(m.ApplyWave(m_tok_gp))
                    self.play(
                        m.LaggedStart(m.Indicate(m_tok[t_index], 
                        color=self.tok_cols[t_index],
                            scale_factor=3),
                            m.FadeToColor(m_tok[t_index], 
                            color=self.tok_cols[t_index])),
                    )
                    # increase number of terminals
                    t_index = t_index + 1

                else:
                    sounds.add_sound_to_scene(self, sounds.FAIL)
                    error.ERR_parsing_error(self.root, 
                        "Unexpected token [" + top + "]")
                    error.ERR_manim_parsing_error(self, ["Invalid input: '" +
                     top + "'"], script = top + " triggers a parsing error," +
                        " so this input is not valid." )
                    return

            elif re.match(RE_NONTERMINAL, top):
                mg.display_msg(self, ["We must find the entry at \
                        ParseTable["+top+"]["+next+"]"], script = "Let's " +
                            "consider the parse table entry at non-terminal " +
                            top + "'s row and terminal " + next.strip() + "'s"+
                            " column.")

                try:
                    pt_entry = self.cfg.parsetable.pt_dict[top][next]

                    if pt_entry == "Error":
                        self._call_ptable_error(top, next)
                        return

                    prods = pt_entry.split("->")

                    if self.parents != []:
                        replaced_parent = self.parents[-1]
                        sounds.add_sound_to_scene(self, sounds.CLICK)
                        new_vertex = create_vertex(g, replaced_parent, \
                            mg.to_math_tex(self.parents[-1].id), \
                            vertex_ids=self.vertex_ids, color = m.GRAY)
                        self.play(m.FadeIn(new_vertex))
                        reset_g(self, g, start_symbol)

                    sounds.add_sound_to_scene(self, sounds.POP)
                    self.s.pop(r'\text{Replacing }' + top + r'...')

                    # highlight parse table row
                    self._fade_in_mtable(highlight  = True, 
                    row = mg.row(self.nts, top), col = mg.col(self.ts, next))
                    
                    #  copy the cfg_line rather than manipulate it directly
                    cfg_line = self.manim_production_groups[prods[0].strip(
                    )][:]
                    cfg_line.next_to(self.s.mstack, m.DOWN).shift(
                        0.8*m.DOWN).scale(0.8)
                    
                    if cfg_line.width > 3*self.s.mstack.width:
                        cfg_line.scale_to_fit_width(3*self.s.mstack.width)

                    self.play(
                        m.FadeIn(cfg_line)
                    )

                    if top != start_symbol:
                        # append new non-terminal path to the tree
                        to_be_appended = self.parents[-1]
                        if to_be_appended.parent == None:
                            to_be_appended.parent = to_be_appended.tmp_parent

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))
                    
                    nodes_to_append = []
                    stack_to_append = []

                    mg.display_msg(self, [prods[0].strip() + " is a "+
                        "non-terminal,", "so we can replace it with", 
                        "its sub-productions: ",  prods[1]], 
                        script="Let's replace " + prods[0].strip() + 
                        " with its sub productions")

                    # this is the direction we push to the stack
                    for p in ps:
                        # add to the tree
                        if top == start_symbol:
                            v_id = self.root.id + "_" + p
                            if v_id in self.vertex_ids:
                                v_id = v_id + "_" + str(self.id_count)
                                self.id_count = self.id_count + 1
           
                            new_node = anytree.Node(p, parent=self.root, id=p, 
                            tmp_p = self.root.id, tmp_parent = self.root, 
                            vertex_id = v_id,
                            parent_id = self.root.id,
                            token = None)
                            self.vertex_ids.append(v_id)
                        else:
                            # add connecting node if it is a non-terminal
                            v_id = replaced_parent.id + "_" + p

                            if v_id in self.vertex_ids:
                                v_id = v_id + "_" + str(self.id_count)
                                self.id_count = self.id_count + 1
                          
                            new_node = anytree.Node(
                                p, id=p, parent = None, tmp_p=prods[0].strip(),
                                vertex_id = v_id,
                                parent_id = replaced_parent.vertex_id,
                                tmp_parent = replaced_parent, token = None)
                            self.vertex_ids.append(v_id)
                                    
                        # apply non-epsilon nodes to the stack
                        if p != "#":
                            stack_to_append.append(p)
                            nodes_to_append.append(new_node)

                    # pop off current parent
                    if self.parents != []:
                        self.parents.pop()
                    
                    # add children to stack and parent stack
                    for n in reversed(nodes_to_append):
                        self.parents.append(n)
                    
                    for s in reversed(stack_to_append):
                        self.s.push(s)

                    self.play(
                        m.FadeOut(cfg_line)
                    )
                except KeyError:
                    self._call_ptable_error(top, next)
                    return

        # in case parsing finishes but there are still tokens left in the stack
        if len(self.tokens) > 0:
            sounds.add_sound_to_scene(self, sounds.FAIL)
            error.ERR_parsing_error(self.root)
            error.ERR_manim_parsing_error(self, ["The stack is not emptied,", 
            "but parsing has concluded."], script = "Since the stack is not"+
                " emptied, parsing is unsuccessful.")
            return

        # fade out the stack and transform the parse tree
        sounds.narrate("Stack emptied.", self)
        self.s.write_under_stack("\\text{Stack emptied.}")
        reset_g(self, g, start_symbol, anim=[m.FadeOut(self.s.mstack)])

        sounds.add_sound_to_scene(self, sounds.YAY)
        mg.display_msg(self, ["Successfully parsed `" + self.inp + "'!"], 
            script= "Parsing successful! That was a valid input.")

        display.success_secho("Successfully parsed '" + self.inp +
                              "'!\nParse tree:")
        display.print_parsetree(self.root)
        return SUCCESS


    def _call_ptable_error(self, top, next):
        error.ERR_parsing_error(self.root,
                "ParseTable[" + top + ", " + next + "] is empty.")
        sounds.add_sound_to_scene(self, sounds.FAIL)
        mg.display_msg(self, ["No such entry at ParseTable[" + 
        top + ", " + next + "].", "Invalid input: `" + next + "'"],
        script = next + " triggers a parsing error, so this "+
            "input is not valid." )
        error.ERR_parsing_error(self.root, 
            "No such entry at ParseTable[" + top + ", " + next +
            "].")
        return 

