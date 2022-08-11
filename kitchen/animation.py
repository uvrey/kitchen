""" Creates Kitchen animations """
# kitchen/animation.py

from pathlib import Path
import manim as m
import re
import typer
import os
import anytree

from kitchen import (
    RE_NONTERMINAL,
    RE_PRODUCTION, 
    SUCCESS,
    RE_TERMINAL,
    display_helper,
    TEXT_SCALE,
    COLOURS,
    error,
    stack, 
    sounds as s,
)

VCONFIG = {"radius": 0.25, "color": m.BLUE, "fill_opacity": 1}
VCONFIG_TEMP = {"radius": 0.25, "color": m.GRAY}
LCONFIG = {"vertex_spacing": (0.5, 1)}
ECONFIG = {"color": m.WHITE}
ECONFIG_TEMP = {"color": m.GRAY, "fill_opacity": 0.7}
V_LABELS = {}

# set global configs
m.config.include_sound = True

# TODO clean up this file a bit better
# TODO add sound
# TODO  Unique filename - Date and time?
# TODO neaten up animations

def _to_tex(item):
    tex_item = item.replace("$", "\$").replace("#", "\\epsilon")
    return tex_item

def _play_msg_with_other(self, msg, anim):
    if msg != []:
        msg_group = m.VGroup()

        for ms in msg:
            msg_txt = m.MathTex(ms)
            msg_group.add(msg_txt)
        msg_group.arrange(m.DOWN)
        
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=m.BLACK, fill_opacity=0.9)
        msg_group.move_to(rect.get_center())

        self.play(
            m.FadeIn(rect),
        )

        self.play(
            m.Write(msg_group)
        )

        self.wait()

        self.play(
            m.FadeOut(msg_group),
            m.FadeOut(rect),
        )

        # add the additional animation
        self.play(
            *[a for a in anim]
        ),
    return SUCCESS

def _get_tokens_from_input(inp) -> list:
    """Obtains the token stream of an input string. 

    Args:
        inp (str): Input string

    Returns:
        list: Token stream
    """    
    return list(filter(None, inp.split(" ")))

    # Helper function to put a message on the screen
def notify(self, message, next_to_this):
    # returns a keys group, which is the cfg representation
    msg_text = m.Text(message, color=m.WHITE, weight=m.BOLD).scale(0.5).next_to(
        next_to_this, m.RIGHT)
    self.play(
        m.Write(msg_text),
    )
    self.wait()
    self.play(
        m.FadeOut(msg_text)
    )

def fullscreen_notify(self, message):
    err_msg = message
    err_m_msg = m.Tex(err_msg, color=m.WHITE)
    rect = m.Rectangle(width=20, height=10, color=m.BLACK, fill_opacity=0.85)
    err_m_msg.move_to(rect.get_center())
    self.play(
        m.FadeIn(rect),
    )
    self.play(
        m.FadeIn(err_m_msg),
        run_time=0.5
    )
    self.wait()

# gets the scaling factor for listing tokens
def get_list_scalefactor(list):
    tl = len(list)
    if tl > 3:
        return 1 - (tl - 3)*0.25
    else:
        return 1

# sets up the ten options for colour coding the tokens
def set_up_token_colour(self):
    # set default manim colours
    self.token_has_colour = []
    # set up colour boolean array
    for i in range(10):
        self.token_has_this_colour.append(False)

# checks if a col has been taken
def get_token_colour(self):
    for index, col in enumerate(COLOURS, start=0):
        if not self.token_has_this_colour[index]:
            self.token_has_this_colour[index] = True
            return col
    return m.WHITE

# fades the scene out
def fade_scene(self):
    self.play(
        *[m.FadeOut(mob) for mob in self.mobjects]
    )

def get_manim_cfg_group(self):
    """Sets up an equivalent CFG in terms of correctly-aligned manim objects.

    Returns:
        VGroup: VGroup Mobject containing elements.
    """        
    manim_cfg = self.cfg.manim_cfg

    keys = m.VGroup()

    self.manim_prod_dict = {}
    self.manim_nt_dict = {}     
    self.manim_production_groups = {}

    for key in manim_cfg:
        self.manim_prod_dict[key] = []

        # create a new group
        production_group = m.VGroup()
        new_cfg_production = manim_cfg[key][0]
        self.manim_nt_dict[key] = new_cfg_production
        arrow = m.Arrow(start=m.LEFT, end=m.RIGHT, buff=0).scale(0.6).next_to(
            new_cfg_production, m.RIGHT)

        # add -> to the production group
        production_group.add(new_cfg_production, arrow)
        prev_element = arrow

        # look at every element that the production leads to
        for index, option in enumerate(manim_cfg[key][1], start=0):
            # append smaller groups
            new_sub_prod = []
            for t_or_nt in option:
                text = t_or_nt.next_to(
                    prev_element, m.RIGHT)
                new_sub_prod.append(text)
                production_group.add(text)
                prev_element = text

            # add this new group to the dictionary's list
            self.manim_prod_dict[key].append(new_sub_prod)

            # append the dividor, if any
            if index < len(manim_cfg[key][1]) - 1:
                dividor = m.Text("  |  ")
                production_group.add(dividor)

        production_group.arrange(m.RIGHT)
        keys.add(production_group)
        self.manim_production_groups[key] = production_group
    
    row_no = len(manim_cfg)
    keys.arrange_in_grid(rows=row_no, buff=0.5)
    keys.fade_to(color=m.DARK_GRAY, alpha=1)
    return keys

# helper function to obtain the follow and first set interpretation guide
def get_guide():
    guide_group_outer = m.VGroup()
    square_colors = [m.TEAL, m.RED]
    labels = ["Terminal", "Non-terminal"]
    for i in range(2):
        guide_group_inner = m.VGroup()
        guide_group_inner.add(m.Square().set_fill(
            square_colors[i], opacity=1))
        guide_group_inner.add(m.Tex(labels[i]))
        guide_group_inner.arrange(m.RIGHT)
        guide_group_outer.add(guide_group_inner)
    guide_group_outer.arrange(m.DOWN, aligned_edge=m.LEFT)
    return guide_group_outer
    
def ts_m_epsilon(self):
    ts_m = []
    for t in self.ts:
        if t == "#":
            ts_m.append("\epsilon")
        else:
            ts_m.append(t)
    return ts_m

# initialise the row values for the manim table
def init_row_contents(self):
    row_vals = []
    for n in self.nts:
        row = []
        for t in self.ts:
            row.append(".")
        row_vals.append(row)
    return row_vals

class ManimFirstSet(m.Scene):
    def setup(self):
        self.frame_width = m.config["frame_width"]
        self.frame_height = m.config["frame_height"]

    def setup_manim(self, cfg):        
        self.cfg = cfg

    def construct(self):
        keys = get_manim_cfg_group(self).scale(TEXT_SCALE)
        display_helper.info_secho("Visualising first set calculation:")
        self.vis_first_set(keys, self.cfg.start_symbol, self.cfg.start_symbol, [])

    # animates a visualisation of the first set
    def vis_first_set(self, keys, start, production, pstack):

      #  global vis_has_epsilon
        pstack.append(production)

        # reset all keys to white except the one we are looking at
        keys.fade_to(color=m.DARK_GRAY, alpha=1).to_edge(m.LEFT)

        # highlight manim production
        cfg_line = self.manim_production_groups[production][:]

        # add the first set titles to the canvas
        self.cfg.manim_firstset_lead[production] = m.Text("First(" + production + "):",
                                                    weight=m.BOLD).align_to(cfg_line, m.UP).scale(0.6).shift(m.LEFT)

        self.play(
            m.FadeIn(self.cfg.manim_firstset_lead[production]),
            m.FadeToColor(cfg_line, color=m.WHITE),
        )

        # if production does not have a first set
        try:
            if self.cfg.first_set[production] == []:
                # loop through values which a production leads to
                for i, p in enumerate(self.cfg.cfg_dict[production], start=0):
                    # if a production is/ starts with a non-terminal
                    if p in self.cfg.cfg_dict or p[0].isupper():
                        # find all the productions which are led by a non-terminal
                        p_nt = list(
                            filter(None, re.findall(RE_PRODUCTION, p)))

                        for j, item in enumerate(p_nt, start=0):
                            current_item = item.strip()

                            if j > 1:

                                prev_element = self.manim_prod_dict[production][i][j-1]
                                prev_element.scale(TEXT_SCALE)

                            # if a terminal is encountered after the list
                            # fade in new terminal and corresponding element of the cfg
                            if re.match(RE_TERMINAL, current_item):

                                for ps in pstack:
                                    if current_item not in self.firstset[ps]:
                                        self.firstset[ps].append(current_item)
                                        # add this terminal and play VGroup of each production in the stack
                                        new_element = m.Text(
                                            terminal_to_write, color=m.TEAL, slant=m.ITALIC, weight=BOLD).scale(TEXT_SCALE)
                                        self.manim_firstset_contents[ps].add(
                                            new_element)
                                        self.manim_firstset_contents[ps].arrange(m.RIGHT).next_to(
                                            self.manim_firstset_lead[ps], m.RIGHT)

                                     # fade in new terminal and corresponding element of the cfg
                                    cfg_element = self.manim_prod_dict[production][i][j]
                                    self.play(
                                        m.FadeIn(new_element),
                                        m.Circumscribe(cfg_element, color=m.TEAL),
                                        m.FadeToColor(cfg_element, color=m.TEAL),
                                    )
                                break
                            else:
                                # highlight the non-terminal
                                cfg_element = self.manim_prod_dict[production][i][j]
                                cfg_element.fade_to(color=m.RED, alpha=1)
                                self.play(
                                    m.ScaleInPlace(cfg_element, 1.5),
                                    m.Circumscribe(cfg_element, color=m.RED),
                                )
                                if j > 1:
                                    # fade out the previous non-terminal
                                    prev_element = self.manim_prod_dict[production][i][j-1]
                                    prev_element.fade_to(
                                        color=m.DARK_GRAY, alpha=1)
                                    prev_element.scale(TEXT_SCALE)

                                notify(self, production + " leads to " + current_item + ",\nso First("+production +
                                             ") = First("+current_item+")", 2*m.RIGHT)

                                self.vis_first_set(
                                    keys, production, current_item, pstack)
                                if not self.cfg.vis_has_epsilon:
                                    break

                        self.cfg.vis_has_epsilon = False

                    else:
                        # if a production starts with a terminal
                        first_terminal = list(
                            filter(None, re.findall(RE_TERMINAL, p)))

                        terminal_to_write = ""

                        if first_terminal[0] == "#":
                            # the non-terminal which led to this may disappear in the original production
                            terminal_to_write = "ε"
                            self.cfg.vis_has_epsilon = True
                        else:
                            terminal_to_write = first_terminal[0]

                            # appends this terminal to the first set of previous non-terminals
                        for ps in reversed(pstack):
                            # make sure the production in focus is shaded white
                            self.manim_production_groups[ps].fade_to(
                                color=m.WHITE, alpha=1)

                            # begin adding to its first set
                            if first_terminal[0] not in self.cfg.first_set[ps]:
                                # add to first set
                                self.cfg.first_set[ps].append(first_terminal[0])
                                # add this terminal and play VGroup of each production in the stack
                                new_element = m.Text(
                                    terminal_to_write, color=m.TEAL, slant=m.ITALIC, weight=m.BOLD).scale(TEXT_SCALE)
                                self.cfg.manim_firstset_contents[ps].add(
                                    new_element)
                                self.cfg.manim_firstset_contents[ps].arrange(m.RIGHT).next_to(
                                    self.cfg.manim_firstset_lead[ps], m.RIGHT)

                            # Notify as to what is happening
                            msg = None
                            if len(pstack) > 1 and ps != production:
                                msg = m.Text("Terminal " + terminal_to_write +
                                           " is also\nadded to First(" + ps + "),\nsince " +
                                           ps + " leads to " + production, weight=m.BOLD).scale(0.5).to_edge(m.RIGHT).shift(m.UP)
                            else:
                                msg = m.Text("Terminal " + terminal_to_write +
                                           " is \nadded to First(" + ps + ")", weight=m.BOLD).scale(0.5).to_edge(m.RIGHT).shift(m.UP)

                            # fade in new terminal and corresponding element of the cfg
                            cfg_element = self.manim_prod_dict[production][i][0]

                            # TODO add sound
                            #self.add_sound("click.wav")

                            self.play(
                                m.Write(msg),
                                m.FadeIn(new_element),
                                m.Circumscribe(cfg_element, color=m.TEAL),
                                m.FadeToColor(cfg_element, color=m.TEAL),
                            )
                            self.wait()
                            self.play(
                                m.FadeOut(msg),
                                run_time=0.25
                            )

                            # notify about user epsilon if we are somewhere in the stack
                            if first_terminal[0] == "#" and ps != start:
                                notify(self, 
                                    "ε found at \nproduction " + production + ", so " + production + " may\n disappear :)", self.manim_firstset_contents[ps])

                            # reset other colours to white
                            self.cfg.manim_firstset_contents[ps].fade_to(
                                color=m.WHITE, alpha=1)

                            # reset all cfg lines to white except the one we are looking at
                            keys.fade_to(color=m.DARK_GRAY, alpha=1)

            # by this point, we have recursively found a bunch of first sets
            # so let's find those that are still empty
            if len(pstack) == 1:
                pstack = []
                empty_set_nt = self.cfg.get_next_production(self.cfg.first_set)
                if empty_set_nt != -1:
                    # found a separate first set
                    self.vis_first_set(
                         keys, empty_set_nt, empty_set_nt, [])
            else:
                pstack.pop()

        except KeyError:
            error.ERR_key_not_given_in_CFG(production)

class ManimFollowSet(m.Scene):
    def setup(self):
        self.frame_width = m.config["frame_width"]
        self.frame_height = m.config["frame_height"]
    
    def setup_manim(self, cfg):        
        self.cfg = cfg

    def construct(self):     
        display_helper.info_secho("Visualising follow set calculation:")
        self.vis_follow_set(True)

    def vis_follow_set(self, is_start_symbol):

            # Set up CFG keys
            keys = get_manim_cfg_group(self).to_edge(m.LEFT).scale(TEXT_SCALE)
            keys.fade_to(m.GRAY, 1).to_edge(m.LEFT)

            # draw LL(1) representation title
            fw_title = m.Tex(r"Follow Set calculation")

            # set the stage
            self.play(
                fw_title.animate.to_edge(m.UP),
                m.FadeIn(keys)
            )
            
            # obtain set for each production
            for production in self.cfg.cfg_dict.keys():
                # fade the other keys
                self._prepare_follow_set_line(production, keys)

                # Rule 1
                if is_start_symbol:
                    self.cfg.follow_set[production].append("$")
                    self.add_to_follow_vis(
                        production, "$", keys, [production + "\\text{ is the start symbol,}", "\\text{so we append \$}", "\\text{ to Follow(}" +
                        production + "\\text{)}"])
                    is_start_symbol = False
                    
                # inspect each element in the production
                for i, p in enumerate(self.cfg.cfg_dict[production]):

                    # split up the productions which are contained within this list
                    pps = list(filter(None, re.findall(RE_PRODUCTION, p)))

                    for index, item in enumerate(pps, start=0):
                        # highlight the element we are inspecting
                        cfg_element = self.manim_prod_dict[production][i][index]

                        # highlight items as we inspect them
                        if re.match(RE_TERMINAL, item):
                            if item == "#":
                                ti = "ε"
                            else:
                                ti = item

                            # observe that the follow of a standalone terminal is ε
                            if index == len(pps) - 1:
                                msg = m.Tex("Follow (" + ti + ")\nmay not exist").scale(
                                    TEXT_SCALE).next_to(self.cfg.manim_followset_contents[production], m.RIGHT)

                                self.play(
                                    m.FadeIn(msg),
                                    m.Circumscribe(cfg_element, color=m.TEAL),
                                    m.FadeToColor(cfg_element, color=m.TEAL),
                                )
                                self.wait()
                                self.play(m.FadeOut(msg))
                            else:
                                # normally highlight the terminal
                                self.play(
                                    m.Circumscribe(cfg_element, color=m.TEAL),
                                    m.FadeToColor(cfg_element, color=m.TEAL),
                                )

                        else:
                            self.play(
                                m.Circumscribe(cfg_element, color=m.RED),
                                m.FadeToColor(cfg_element, color=m.RED),
                            )

                        # start processing
                        if index == len(pps) - 1 and item != "#" and item != production:
                            # temporarily append production to let us then iterate over and replace it
                            self.cfg.follow_set[item].append(production)
                            self.add_to_follow_vis(
                                item, production, keys, ["Follow (" + production + ") \\subseteq Follow (" + item + ")"])

                        elif index < len(pps) - 1:
                            next_item = pps[index + 1]
                            # if an item is directly followed by a terminal, it is appended to its follow set
                            if re.match(RE_TERMINAL, next_item):
                                self.cfg.follow_set[item].append(next_item)
                                self.add_to_follow_vis(
                                    item, next_item, keys)
                            else:
                                # we add the first of the non-terminal at this next index
                                tmp_follow = self.cfg.first_set[next_item]
                                next_cfg_element = self.manim_prod_dict[production][i][index + 1]

                                # highlight the next element we are looking at
                                if re.match(RE_TERMINAL, next_item):
                                    self.play(
                                        m.Circumscribe(
                                            next_cfg_element, color=m.TEAL),
                                        m.FadeToColor(next_cfg_element, color=m.TEAL),
                                    )
                                else:
                                    self.play(
                                        m.Circumscribe(
                                            next_cfg_element, color=m.RED),
                                        m.FadeToColor(next_cfg_element, color=m.RED),
                                    )

                                msg = m.Tex("{First ("+next_item+") - \\epsilon} \\ \\in Follow (" + item + ")").scale(
                                    TEXT_SCALE).next_to(self.manim_followset_contents[production], m.RIGHT) 
                                self.play(
                                    m.LaggedStart(
                                        m.FadeIn(msg),
                                        m.Indicate(msg),
                                    )
                                )
                                self.wait()
                                self.play(m.FadeOut(msg))

                                for t in tmp_follow:
                                    if t != "#":
                                        self.cfg.follow_set[item].append(t)
                                        self.add_to_follow_vis(
                                            item, t, keys, [t + " \\in \\text{\{First}("+next_item+"\\) - \\epsilon\}"])
                                    else:
                                        # we found an epsilon, so this non-terminal
                                        self.cfg.follow_set[item].append(next_item)
                                        self.add_to_follow_vis(
                                            item, next_item, keys, ["\\epsilon \\in \\text\{First\}("+next_item+")\\text{,}", "\\text{so }"+next_item+"\\text{ may not}", "\\text{actually appear after }"+item])

            # start cleaning the follow set
            self.is_cleaned = []
            self.is_cleaned = self.cfg.get_reset_cleaned_set()
            self.clean_follow_set(self.cfg.start_symbol, [])

            # transform current follow sets to cleaned versions
            for key in reversed(self.cfg.follow_set.keys()):
                if not re.match(RE_TERMINAL, key):
                    new_fs_group = m.VGroup()
                    has_eos = False
                    for item in self.cfg.follow_set[key]:
                        if item == "$":
                            has_eos = True
                        else:
                            new_fs_group.add(
                                m.Text(item, weight=m.BOLD, slant=m.ITALIC, color=m.TEAL).scale(TEXT_SCALE))
                    # puts $ at end of list for consistency
                    if has_eos:
                        new_fs_group.add(
                            m.Text("$", weight=m.BOLD, slant=m.ITALIC, color=m.TEAL).scale(TEXT_SCALE))
                    new_fs_group.arrange(m.RIGHT).next_to(
                        self.cfg.manim_followset_lead[key], m.RIGHT)

                    self.play(
                        m.Transform(
                            self.cfg.manim_followset_contents[key], new_fs_group),
                    )

# cleans the follow set up after everything is found, so that we don't miss elements
    def clean_follow_set(self, start, pstack):
        pstack.append(start)

        # clean up the sets
        items = self.cfg.follow_set[start]

        # loop through the items in a given follow set and replace non-terminals with
        # their associated follow sets
        for index, item in enumerate(items, start=0):
            # typer.echo("looking at " + item)
            # we have an item in the set
            if re.match(RE_NONTERMINAL, item):
                self.clean_follow_set(item, pstack)
                items.remove(item)
            else:
                # we append the descended terminals to the upwards stacks
                for p in pstack:
                    if p != start and item not in self.cfg.follow_set[p]:
                        self.cfg.follow_set[p].append(item)

        self.is_cleaned[start] = True

        if len(pstack) == 1:
            pstack = []
            # gets the next not cleaned set
            for c in self.is_cleaned.keys():
                if self.is_cleaned[c] == False:
                    self.clean_follow_set(c, pstack)
        else:
            pstack.pop()

  
    def add_to_follow_vis(self, production, item, keys, msg=[]):
        new_element = None

        if not re.match(RE_TERMINAL, production) and item != production:
            # display adding to the non-terminal followsets
            self._prepare_follow_set_line(production, keys)

            # check if item to be added is a non-terminal
            if re.match(RE_NONTERMINAL, item):
                # non terminal
                new_element = m.Tex(
                    r'Follow(', item, ')', color=m.BLUE)

            else:
                # append it directly as a terminal
                element = _to_tex(item)
                new_element = m.Tex(
                    element, color=m.TEAL)

            # add to the content group
            self.cfg.manim_followset_contents[production].add(
                new_element)
            self.cfg.manim_followset_contents[production].arrange_in_grid(rows=1, buff=0.5)
            self.cfg.manim_followset_contents[production].next_to(
                self.cfg.manim_followset_lead[production], m.RIGHT)

        # Play the addition of the item to the followset and message, if given
            if msg != []:
                _play_msg_with_other(self, msg, [m.FadeIn(new_element)])
            else:
                self.play(
                    m.FadeIn(new_element)
                )

    def _prepare_follow_set_line(self, production, keys):
        # only prepare a follow set for non-terminals
        if not re.match(RE_TERMINAL, production):
            # create anims buffer
            anims = []

            # highlight manim production
            keys.fade_to(color=m.GRAY, alpha=1)
            cfg_line = self.manim_production_groups[production][:]
            anims.append(m.FadeToColor(cfg_line, m.WHITE))

            # add the follow set titles to the canvas
            if self.cfg.manim_followset_lead[production] == None:
                self.cfg.manim_followset_lead[production] = m.Tex("Follow(" + production + "):",
                                                             ).align_to(cfg_line, m.UP).shift(m.LEFT)
                # prepare content group
                self.cfg.manim_followset_contents[production].next_to(
                    self.cfg.manim_followset_lead[production], m.RIGHT)
                self.cfg.manim_followset_contents[production].arrange(m.RIGHT)

                # show the new follow area
                anims.append(
                    m.FadeIn(self.cfg.manim_followset_lead[production]),
                )

            # animate the cfg line highlight
            self.play(
                *[a for a in anims]
            )


class ManimParseTable(m.Scene):
    def setup(self):
        self.frame_width = m.config["frame_width"]
        self.frame_height = m.config["frame_height"]

    def construct(self):
        self.vis_populate_table()

    def init_pt_dict(self):
        # set up parsing table structure
        for n in self.nts:
            for t in self.ts:
                self.pt_dict[n] = {}
                self.pt_dict[n][t] = None

    def setup_manim(self, cfg):
        self.ts = sorted(cfg.terminals)
        self.nts = sorted(cfg.nonterminals)
        self.cfg = cfg
        self.add_sound(os.getcwd() + "\\assets\sounds\\add_to_set.wav")

    # quickly get the row and column index of the parse table contents
    def row(self, nt):
        return self.nts.index(nt) + 1

    def col(self, t):
        return self.ts.index(t) + 1

    def vis_populate_table(self):
        """Visualises the algorithm which constructs the parsing table

        Args:
            scene (_type_): _description_
        """
        typer.echo("vis pop table")
        # make sure parse table is fully reset
        self.pt_dict = {}
        self.init_pt_dict()

        # set up the title
        ll1_title = m.Tex(r"LL(1) Parsing: Setting up the Parse Table")
        keys = get_manim_cfg_group(self)
        keys.to_edge(m.LEFT)

        # show key for colour coding
        guide = get_guide().scale(0.3)

        self.play(
            ll1_title.animate.to_edge(m.UP),
            guide.animate.to_corner(m.DOWN + m.RIGHT),
            m.FadeIn(m.Text("CFG", weight=m.BOLD).move_to(
                keys.get_top()+m.UP*0.3).align_to(keys.get_center()).scale(0.5)),
            m.LaggedStart(*(m.FadeIn(k.scale(0.6), shift=m.UP)
                        for k in keys)),
        )

        # draw establishing table animations
        row_labels = self.nts
        col_labels = ts_m_epsilon(self)

        # build up the row values
        row_vals = init_row_contents(self)

        self.mtable = self.init_m_table(
            row_vals, row_labels, col_labels)

        self.mtable.get_row_labels().fade_to(color=m.RED, alpha=1)
        self.mtable.get_col_labels().fade_to(color=m.TEAL, alpha=1)

        self.play(
           m.Write((self.mtable).get_labels()),
            run_time=1
        )
        # TODO play the sound effect
        # typer.echo("SOUND EFFECT")
        # self.add_sound(s.add_to_set_sound())

        self.play(
            m.Create((self.mtable).get_horizontal_lines()[2]),
            m.Create((self.mtable).get_vertical_lines()[2]),
            run_time=2
        )
        # # TODO play the sound effect
        # typer.echo("SOUND EFFECT")
        # self.add_sound(s.add_to_set_sound())

        # populate the whole table with the first and follow set, if appropriate
        for i, key in enumerate(self.cfg.first_set.keys(), start=0):
            for j, item in enumerate(self.cfg.first_set[key], start=0):
                # if the first set contains epsilon, may disappear
                if item == "#":
                    for f in self.cfg.follow_set[key]:
                        if f == "$":
                            mprod = key + " \\to DOLLAR"
                            prod = key + " -> $"
                        else:
                            mprod = key + " \\to \epsilon"
                            prod = key + " -> #"
                        notify(
                            "Following " + prod + "\nadded ε to First(" + key + ")", self.mtable)
                        self.vis_add_to_parsetable( key, f, prod, mprod)
                else:

                    # add item to the parse table
                    prod = self.cfg.firstset_index[key][j]
                    mprod = prod
                    tmp_prod = prod.replace(
                        "->", "\\to").strip().replace("#", "\epsilon")
                    notify(self, "Following " + prod + "\nadded " +
                                 self.cfg.first_set[key][j] + " to First(" + key + ")", self.mtable)
                    self.vis_add_to_parsetable(
                         key, item, prod, tmp_prod)

    def vis_add_to_parsetable(self, nt, t, prod, mprod):
        try:
            if self.pt_dict[nt][t] != None:
                error.ERR_too_many_productions_ll1(nt, t)
            else:
                self.pt_dict[nt][t] = prod
                self.swap(self.row(nt), self.col(t), mprod)

        except KeyError:
            self.pt_dict[nt][t] = prod
            self.swap(self.row(nt), self.col(t), mprod)

    # swap a current entry
    def swap(self, row, col, new_val) -> m.MathTable:
        """Swaps two elements in a manim parse table.

        Args:
            row (int): Row of element to be swapped.
            col (int): Column of element to be swapped.
            new_val (String): Value to be swapped into the table. 
        """        
        t_old = self.mtable.get_entries_without_labels((row, col))

        self.play(
            m.Indicate(t_old)
        )

        # set up new value with colour
        t_new = m.MathTex(new_val).scale(0.7)
        t_new.move_to(t_old)
        t_new.fade_to(m.WHITE, alpha=0.2)

        # fade out old value and into new value
        self.play(
            m.FadeIn(t_new),
            m.FadeOut(t_old),
        )
        # pause
        self.wait()

    def init_m_table(self, row_vals, row_labels, col_labels):
        row_labels = row_labels
        col_labels = col_labels

        table = m.MathTable(
            row_vals,
            row_labels=[m.MathTex(rl) for rl in row_labels],
            col_labels=[m.MathTex(cl) for cl in col_labels],
            include_outer_lines=True)

        # Table
        lab = table.get_labels()
        lab.set_color(m.LIGHT_GRAY)
        table.get_horizontal_lines()[2].set_stroke(width=8, color=m.LIGHT_GRAY)
        table.get_vertical_lines()[2].set_stroke(width=8, color=m.LIGHT_GRAY)
        return table

    def init_table(self, x_vals, y_vals, row_labels, col_labels):
        """Set up Table MObject prior to being drawn.

        Args:
            x_vals (List): List of x values.
            y_vals (List): List of y values.
            row_labels (List): X labels.
            col_labels (List): Y Labels. 
        """        

        self.xs = x_vals
        self.ys = y_vals
        self.row_labels = row_labels
        self.col_labels = col_labels

        self.table = m.MathTable(
            [self.xs, self.ys],
            row_labels=[m.MathTex(rl) for rl in self.row_labels],
            col_labels=[m.MathTex(cl) for cl in self.col_labels],
            include_outer_lines=True)

        # Table
        lab = self.table.get_labels()
        lab.set_color(m.LIGHT_GRAY)
        self.table.get_horizontal_lines()[2].set_stroke(
            width=8, color=m.LIGHT_GRAY)
        self.table.get_vertical_lines()[2].set_stroke(
            width=8, color=m.LIGHT_GRAY)


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
    # BUG Should be + DOWN
    pos = g[parent_id].get_center()+m.DOWN
    v = g._add_vertex(
        vertex_id, vertex_config={"color": color}, position=pos)
    v.fill_colour = color

    if link:
        g._add_edge(
            [parent_id, vertex_id], edge_config={"color": m.WHITE})
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



class ManimParseTree(m.Scene):
    # Parse LL(1) in the CLI
    def setup(self):
        self.frame_width = m.config["frame_width"]
        self.frame_height = m.config["frame_height"]

    def setup_manim(self, inp, cfg):
        self.inp = inp
        self.tokens = _get_tokens_from_input(inp)
        self.cfg = cfg
        self.nts = sorted(cfg.nonterminals)
        self.ts = sorted(cfg.terminals)

    def construct(self):
        self.vis_parse_ll1(self.inp, self.tokens)
        
    def init_m_table(self, row_vals, row_labels, col_labels):
        row_labels = row_labels
        col_labels = col_labels

        table = m.MathTable(
            row_vals,
            row_labels=[m.MathTex(rl) for rl in row_labels],
            col_labels=[m.MathTex(cl) for cl in col_labels],
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
        col_labels = ts_m_epsilon(self)

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
                            tmp = item.replace(
                                "->", "\\to").strip().replace("#", "\epsilon")
                            row.append(tmp)
                    else:
                        row.append("")
                except KeyError:
                    row.append("")
            row_vals.append(row)
        return row_vals

# Parse LL(1) in the CLI

    def vis_parse_ll1(self, input, tokens):
        global V_LABELS
        global VCONFIG
        global m

        # set up the stack and the parsing table
        self.s = stack.Stack(self, m.DR, 5)
        self.init_m_ll1_parsetable()
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

        # draw LL(1) representation title
        ll1_title = m.Tex(r"LL(1) Parsing")
        keys = get_manim_cfg_group(self).to_edge(m.RIGHT)

        # create the input group here
        m_tok = {}
        m_tok_gp = m.VGroup()
        m_tok_gp.add(m.Tex("Token stream: ")).scale(0.7)
        for t in tokens:
            tex = m.MathTex("\\text{"+t+"}")
            m_tok_gp.add(tex)
            m_tok[t] = tex
        m_tok_gp.arrange(m.RIGHT)

        # set the stage
        self.play(
            ll1_title.animate.to_edge(m.UP),
            m_tok_gp.animate.to_edge(m.UR).shift(m.DOWN+m.LEFT),
            self.s.mstack.animate.to_edge(m.LEFT).shift(
                m.DOWN+m.RIGHT).align_to(self.mtable.get_center),
        )

        # TODO custom colour for terminals!
        # TODO educational messages
        # TODO show input and frame to move through
        # TODO sound on popping

        # create our first label
        V_LABELS[start_symbol] = start_symbol
        g = m.Graph([start_symbol], [], vertex_config=VCONFIG,
                  labels=V_LABELS, label_fill_color=m.WHITE)

        g.to_edge(m.UP).shift(m.DOWN)
        self.add(g)
        self.root.manim.move_to(g[start_symbol].get_center())
         
        # begin parsing
        while self.s.stack != []:
            # in case we run out of input before the stack is empty
            if tokens == []:
                if re.match(RE_TERMINAL, self.s.stack[-1]):
                    error.ERR_parsing_error("Expected " + self.s.stack[-1])
                else:
                    error.ERR_parsing_error()
                error.ERR_manim_parsing_error(self)
                return

            top = self.s.stack[-1]
            next = tokens[0]

            # draw initial node if top is start symbol
            if re.match(RE_TERMINAL, top) or top == "$":

                if top == next:
                    anims = []
                    tokens.remove(next)

                    # highlight parents
                    if self.parents == []:
                        parent = None

                    # pops appropriately
                    if self.parents != []:
                        popped = self.parents.pop()
                        parent = self.parents[-1]

                        # always pop again if an epsilon was encountered
                        if self.parents != []:
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
                                            popped.id, parent=p, id=popped.id, manim=m.Text(popped.id, weight=m.BOLD))

                                        # check for epsilons
                                        rhs = self.parents[-i + 1:]
                                        for r in rhs:
                                            if re.match(RE_NONTERMINAL, r.id) and r.id != p.id and r.height == 0:
                                                if "#" in self.cfg.first_set[r.id]:
                                                    new_node = anytree.Node(
                                                        "#", parent=r, id="eps", manim=m.MathTex("\epsilon"))
                                                    vertex_id = r.id + "_" + new_node.id
                                                    parent_id = r.id
                                                    if r.id != start_symbol:
                                                        parent_id = r.parent.id + "_" + r.id
                                                    v = create_vertex(
                                                        g, vertex_id, parent_id, "\epsilon")
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
                        typer.echo("parent is " + parent.id)

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
                                "\\text{"+top+"}", color=m.BLACK)
                            new_vertex.fade_to(m.BLUE, 1)
                            rendered_label.move_to(new_vertex.get_center())
                            new_vertex.add(rendered_label)

                            self.play(
                                m.Circumscribe(new_vertex, color=m.BLUE),
                                run_time=2
                            )
                            try:
                                edge = g.edges[(parent_vertex_id, vertex_id)]
                                anims.append(
                                    m.FadeToColor(edge, color=m.WHITE))
                            except:
                                pass
                        except KeyError:
                            # create and add new vertex
                            new_vertex = create_vertex(
                                g, vertex_id, parent_vertex_id, vertex_id.split("_")[
                                    1].strip(), color=m.BLUE)
                            reset_g(self, g, start_symbol)

                    # pop off the stack and 'flash'
                    self.s.pop(anim=anims, vertex=new_vertex, matching=True, msg="\\text{Matched }" +
                               self.s.stack[-1] + "\\text{!}")

                    # highlight the token stream line and token that we matched
                    self.play(m.ApplyWave(m_tok_gp))
                    self.play(
                        m.LaggedStart(m.Indicate(m_tok[next], color=m.BLUE, scale_factor=1.5),
                                    m.FadeToColor(
                            m_tok[next],m.BLUE)),
                    )

                else:
                    error.ERR_parsing_error(
                        "Unexpected token [" + top + "]")
                    error.ERR_manim_parsing_error(self)
                    return

            elif re.match(RE_NONTERMINAL, top):
                try:
                    pt_entry = self.cfg.parsetable.pt_dict[top][next]
                    prods = pt_entry.split("->")

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
                                rendered_label = m.MathTex(
                                    "\\text{"+popped_off+"}", color=m.BLACK)

                                # confirm the path by adding the colour
                                vertex.fade_to(m.BLUE, 1)
                                rendered_label.move_to(vertex.get_center())
                                vertex.add(rendered_label)

                                self.play(
                                    m.Circumscribe(vertex, color=m.BLUE),
                                    run_time=2
                                )
                            except:
                                pass

                    self.s.pop(anim=anims,
                               msg="\\text{Replacing }" + popped_off + "\\text{...}")

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))

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
                            new_prod = prods[0].strip() + " \\to " + p
                            self.s.push(p, new_prod)
                            self.parents.append(new_node)

                    self.play(
                        m.FadeOut(cfg_line)
                    )

                except KeyError:
                    error.ERR_parsing_error(
                        "ParseTable[" + top + ", " + top + "] is empty.")
                    return

            # transform the tree
            reset_g(self, g, start_symbol)

        # in case parsing finishes but there are still tokens left in the stack
        if len(tokens) > 0:
            error.ERR_parsing_error()
            error.ERR_manim_parsing_error(self)
            return

        # fade out the stack and transform the parse tree
        reset_g(self, g, start_symbol, anim=[m.FadeOut(self.s.mstack)])

        self.s.write_under_stack("Stack emptied.")
        fullscreen_notify(self, "Successfully parsed '" + " ".join(original_tokens) +
                                "'!")

        display_helper.success_secho("Successfully parsed '" + " ".join(original_tokens) +
                              "'!\nParse tree:")
        display_helper.print_parsetree(self.root)
        return SUCCESS

