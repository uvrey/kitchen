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
    CFG_SCALE,
    CFG_SCALE_HEIGHT,
    CFG_SCALE_WIDTH,
    COLOURS,
    ERROR,
    error,
    stack, 
    sounds,
    config
)

VCONFIG = {"radius": 0.25, "color": m.BLUE, "fill_opacity": 1}
VCONFIG_TEMP = {"radius": 0.25, "color": m.GRAY}
LCONFIG = {"vertex_spacing": (0.5, 1)}
ECONFIG = {"color": config.opp_col()}
ECONFIG_TEMP = {"color": m.GRAY, "fill_opacity": 0.7}
V_LABELS = {}

GRID_ITEM_SCALE = 0.4

# set global configs
m.config.include_sound = True

def _get_title_mobject(title):
    return m.Tex(title, tex_template=m.TexFontTemplates.french_cursive)

def _to_tex(item):
    tex_item = item.replace("$", "\$").replace("\epsilon", "$\epsilon$").replace("#", "$\epsilon$").replace("\\subseteq", "$\\subseteq$").replace("->", "$\\to$").replace("(", "$($").replace(")", "$)$")
    return tex_item

def _to_math_tex(item):
    tex_item = item.replace("$", "\$").replace("#", "\epsilon").replace("->", "\\to")
    return tex_item


def _play_msg_with_other(self, msg, raw_msg= "", anim=[]):
    if msg != []:
        msg_group = m.VGroup()

        for ms in msg:
            msg_txt = m.Tex(_to_tex(ms), color=config.opp_col())
            msg_group.add(msg_txt)
        msg_group.arrange(m.DOWN)
        
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.theme_col(), fill_opacity=0.9)

        self.play(
            m.FadeIn(rect),
        )

        # generate voiceover
        if raw_msg != "":
            sounds.narrate(raw_msg, self)

        self.play(
            m.Write(msg_group),
        )

        self.wait()

        self.play(
            m.FadeOut(msg_group),
            m.FadeOut(rect),
        )

        # add the additional animation
        if anim != []:
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
    msg_text = m.Text(message, color=config.opp_col(), weight=m.BOLD).scale(0.5).next_to(
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
    err_m_msg = m.Tex(err_msg, color=config.opp_col())
    rect = m.Rectangle(width=20, height=10, color=config.theme_col(), fill_opacity=0.85)
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
    self.token_has_this_colour = []
    # set up colour boolean array
    for i in range(10):
        self.token_has_this_colour.append(False)

# checks if a col has been taken
def get_token_colour(self):
    for index, col in enumerate(COLOURS, start=0):
        if not self.token_has_this_colour[index]:
            self.token_has_this_colour[index] = True
            return col
    return config.opp_col()

# fades the scene out
def fade_scene(self):
    self.play(
        *[m.FadeOut(mob) for mob in self.mobjects]
    )

def row(cfg, nt):
    """Quickly get the row and column index of the parse table contents_summary_

    Args:
        cfg (ContextFreeGrammar): CFG 
        nt (str): Non-terminal 

    Returns:
        int: Row of non-terminal
    """    
    return sorted(cfg.nonterminals).index(nt) + 1

def col(cfg, t):
    """Quickly get the row and column index of the parse table contents_summary_

    Args:
        cfg (ContextFreeGrammar): CFG     
        nt (str): Non-terminal 

    Returns:
        int: Row of non-terminal
    """    
    return sorted(cfg.terminals).index(t) + 1

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
def get_guide(arr_right = False):
    guide_group_outer = m.VGroup()
    square_colors = [m.TEAL, m.RED]
    labels = ["Terminal", "Non-terminal"]
    for i in range(2):
        guide_group_inner = m.VGroup()
        guide_group_inner.add(m.Square().set_fill(
            square_colors[i], opacity=1).scale(0.5))
        guide_group_inner.add(m.Tex(labels[i], color = config.opp_col()))
        guide_group_inner.arrange_in_grid(rows = 1, buff = 0.8)
        guide_group_outer.add(guide_group_inner)
    
    if not arr_right:
        guide_group_outer.arrange_in_grid(rows = len(labels), buff = 0.8)
    else:
        guide_group_outer.arrange_in_grid(rows = 1, buff = 0.8) 
    return guide_group_outer.arrange(m.DOWN, aligned_edge=m.LEFT)
    
def ts_m_epsilon(self):
    ts_m = []
    for t in self.ts:
        if t == "#":
            ts_m.append("#")
        else:
            ts_m.append(t)
    return ts_m

def clear_narrs():
    # clear and reinitialise the narration diary
    if sounds.get_config() == sounds.NARR:
        sounds.clear_narr_dir()
        sounds.init_narr_dir()

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
        sounds.narrate("Let's find the first set!", self)
        display_helper.info_secho("Visualising the First Set:")


        # set title and scaling here since the function is recursive
        fs_title = _get_title_mobject("first set calculation") 
        self.play(fs_title.animate.to_edge(m.UP))

        keys = get_manim_cfg_group(self)
        keys.scale_to_fit_height(CFG_SCALE_HEIGHT/3)

        # show key for colour coding
        guide = get_guide().scale_to_fit_height(CFG_SCALE_HEIGHT/4)

        self.vis_first_set(keys, guide, self.cfg.start_symbol, self.cfg.start_symbol, [])

        # success message and sound
        sounds.add_sound_to_scene(self, sounds.YAY)
        _play_msg_with_other(self, ["Successfully found the first set :)"], raw_msg= "Woohoo! We got the first set!")

    def tear_down(self):
        # clear first set structures for if the animation is regenerated
        self.cfg.vis_has_epsilon = False
        self.cfg.manim_firstset_lead = {}
        for key in self.cfg.first_set.keys():
            self.cfg.first_set[key] = []
            self.cfg.manim_firstset_contents[key] = m.VGroup()
        clear_narrs()

    # animates a visualisation of the first set
    def vis_first_set(self, keys, guide, start, production, pstack):

        #  global vis_has_epsilon
        pstack.append(production)

        # reset all keys to white except the one we are looking at
        keys.fade_to(color=m.DARK_GRAY, alpha=1)

        # highlight manim production
        cfg_line = self.manim_production_groups[production][:]

    # add the first set titles to the canvas
        self.cfg.manim_firstset_lead[production] = m.Tex("First(" + production + "):", color = config.opp_col()
                                                    ).align_to(cfg_line, m.UP).shift(m.LEFT)

        self.play(
            m.FadeIn(self.cfg.manim_firstset_lead[production]),
            m.FadeToColor(cfg_line, color=config.opp_col()),
            guide.animate.to_edge(m.RIGHT),
        )

        # if production does not have a first set
        try:

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

                        # if a terminal is encountered after the list
                        # fade in new terminal and corresponding element of the cfg
                        if re.match(RE_TERMINAL, current_item):

                            for ps in pstack:
                                if current_item not in self.firstset[ps]:
                                    self.firstset[ps].append(current_item)
                                    # add this terminal and play VGroup of each production in the stack
                                    new_element = m.Tex(
                                        _to_tex(terminal_to_write), color=m.TEAL).scale(TEXT_SCALE)
                                    self.manim_firstset_contents[ps].add(
                                        new_element)
                                    self.manim_firstset_contents[ps].arrange_in_grid(row=1, buff = 0.5).next_to(
                                        self.manim_firstset_lead[ps], m.RIGHT)

                                    # fade in new terminal and corresponding element of the cfg
                                cfg_element = self.manim_prod_dict[production][i][j]
                                sounds.add_sound_to_scene(self, sounds.CLICK)
                                self.play(
                                    m.FadeIn(new_element),
                                    m.Circumscribe(cfg_element, color=m.TEAL, shape = m.Circle),
                                    m.FadeToColor(cfg_element, color=m.TEAL, shape = m.Circle),
                                )
                            break
                        else:
                            # highlight the non-terminal
                            cfg_element = self.manim_prod_dict[production][i][j]
                            cfg_element.fade_to(color=m.RED, alpha=1)
                            sounds.add_sound_to_scene( self, sounds.CLICK)
                            self.play(
                                m.LaggedStart(
                                m.Circumscribe(cfg_element, color=m.RED, shape = m.Circle),
                                m.FadeToColor(cfg_element, color = m.RED),
                                )
                            )
                            if j > 1:
                                # fade out the previous non-terminal
                                prev_element = self.manim_prod_dict[production][i][j-1]
                                prev_element.fade_to(
                                    color=m.DARK_GRAY, alpha=1)
                                prev_element.scale(TEXT_SCALE)

                            # display the message alongside narration
                            _play_msg_with_other(self, [production + " leads to " + current_item + ",", "so First("+production +
                                            ") \\subseteq First("+current_item+")"], raw_msg=production + ", leads to another non terminal" + current_item + ", so their first sets will overlap.")

                            # ensure we don't add # when unnecessary
                            had_eps = "#" in self.cfg.first_set[current_item]
                            self.vis_first_set(
                                keys, guide, production, current_item, pstack)
                            has_eps = "#" in self.cfg.first_set[current_item]

                            if not had_eps and has_eps and len(pstack) == 1 and j != len(p_nt) - 1:
                                self.cfg.first_set[production].remove("#")

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
                        self.cfg.vis_has_epsilon = True

                    terminal_to_write = _to_tex(first_terminal[0])

                        # appends this terminal to the first set of previous non-terminals
                    for ps in reversed(pstack):
                        # make sure the production in focus is shaded white
                        self.manim_production_groups[ps].fade_to(
                            color=config.opp_col(), alpha=1)

                        # don't add # if we are down the stack
                        # begin adding to its first set
                        if first_terminal[0] not in self.cfg.first_set[ps]:
                            # add to first set
                            self.cfg.first_set[ps].append(first_terminal[0])
                            # add this terminal and play VGroup of each production in the stack
                            display_helper.info_secho("texing: " + terminal_to_write)
                            new_element = m.Tex(
                                    terminal_to_write, color=m.TEAL).scale(TEXT_SCALE)
                            self.cfg.manim_firstset_contents[ps].add(
                                new_element)
                            self.cfg.manim_firstset_contents[ps].arrange_in_grid(row=1, buff = 0.5).next_to(
                                self.cfg.manim_firstset_lead[ps], m.RIGHT)

                        # Notify as to what is happening
                        msg = []
                        if len(pstack) > 1 and ps != production:
                            msg = ["Terminal " + terminal_to_write +
                                        " is also", "added to First(" + ps + "),", "since " +
                                        ps + " leads to " + production]
                            raw_msg = ps + " leads to " + production + ", so we add " + first_terminal[0] + " to both. "
                        else:
                            msg = ["Terminal " + terminal_to_write +
                                        " is ", "added to First(" + ps + ")"]
                            raw_msg = "Let's add terminal " + first_terminal[0] + "!"
                        _play_msg_with_other(self, msg, raw_msg)

                        # fade in new terminal and corresponding element of the cfg
                        cfg_element = self.manim_prod_dict[production][i][0]

                        # adds sound as the new element is added
                        sounds.add_sound_to_scene(self, sounds.CLICK)
                        self.add(new_element)

                        self.play(
                            m.Circumscribe(cfg_element, color=m.TEAL, shape = m.Circle),
                            m.FadeToColor(cfg_element, color=m.TEAL),
                        )

                        # notify about user epsilon if we are somewhere in the stack
                        if first_terminal[0] == "#" and ps != start:
                            _play_msg_with_other(self, ["\\epsilon found at production " + production + ",", "so " + production + " may disappear :)"], raw_msg = "The production may disappear since it can lead to epsilon.")

                        # reset other colours to white
                        self.cfg.manim_firstset_contents[ps].fade_to(
                            color=config.opp_col(), alpha=1)

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
                         keys, guide, empty_set_nt, empty_set_nt, [])
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
        sounds.narrate("Let's find the follow set.", self)
        display_helper.info_secho("Visualising follow set calculation:")
        self.vis_follow_set(True)
    
    def tear_down(self):
        for key in self.cfg.follow_set.keys():
            self.cfg.follow_set[key] = []
        clear_narrs()

    def vis_follow_set(self, is_start_symbol):

            # Set up CFG keys
            keys = get_manim_cfg_group(self).to_edge(m.LEFT).scale_to_fit_height(CFG_SCALE_HEIGHT)
            keys.fade_to(m.GRAY, 1).to_edge(m.LEFT)

            # draw follow set title
            fw_title = _get_title_mobject("follow set calculation") 
            guide = get_guide().scale(CFG_SCALE)


            # set the stage
            self.play(
                fw_title.animate.to_edge(m.UP),
                guide.animate.to_edge(m.RIGHT),
                m.FadeIn(keys)
            )
            
            # obtain set for each production
            for production in self.cfg.cfg_dict.keys():
                # fade the other keys
                self._prepare_follow_set_line(production, keys)

                # Rule 1
                if is_start_symbol:
                    self.cfg.follow_set[production].append("$")
                    self._add_to_follow_vis(
                        production, "$", keys, [production + " is the start symbol,", "so we append $", "to Follow(" +
                        production + ")"], raw_msg = production + ", is the start symbol, so we append $ to its follow set.")
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
                                ti = "#"
                            else:
                                ti = item

                            # observe that the follow of a standalone terminal may be ε
                            if index == len(pps) - 1:
                                # prepare simultaneous animations
                                anims = []
                                tmp_anim = [m.Circumscribe(cfg_element, color=m.TEAL, shape = m.Circle),
                                    m.FadeToColor(cfg_element, color=m.TEAL)]
                                for t in tmp_anim:
                                    anims.append(t)
                                
                                _play_msg_with_other(self, ["Follow(" + _to_tex(ti) + ") may not exist"], raw_msg = "A standalone non epsilon terminal won't have a follow set.")


                            else:
                                # just highlight the terminal
                                self.wait()
                                sounds.narrate(item + " , is a terminal.")
                                self.play(
                                    m.Circumscribe(cfg_element, color=m.TEAL, shape = m.Circle),
                                    m.FadeToColor(cfg_element, color=m.TEAL),
                                )

                        else:
                            self.wait()
                            sounds.narrate("Let's now look at " +item +", which is a non terminal.", self)
                            self.play(
                                m.Circumscribe(cfg_element, color=m.RED, shape = m.Circle),
                                m.FadeToColor(cfg_element, color=m.RED),
                            )
                            self.wait()

                        # start processing
                        if index == len(pps) - 1 and item != "#" and item != production:
                            # temporarily append production to let us then iterate over and replace it
                            if production not in self.cfg.follow_set[item]:
                                self.cfg.follow_set[item].append(production)
                                self.wait()
                                self._add_to_follow_vis(
                                    item, production, keys, ["Follow(" + production + ") \\subseteq Follow(" + item + ")"], raw_msg = "The follow set of " + production + " is a subset of that of " + item + " ")
                            else:
                                _play_msg_with_other(self, [next_item +", is already in Follow(" + item + ")"], raw_msg=item + "is already in the follow set.")                                   
                        
                        elif index < len(pps) - 1:
                            next_item = pps[index + 1]
                            # if an item is directly followed by a terminal, it is appended to its follow set
                            if re.match(RE_TERMINAL, next_item):
                                if next_item not in self.cfg.follow_set[item]:
                                    self.cfg.follow_set[item].append(next_item)
                                    self._add_to_follow_vis(
                                        item, next_item, keys)
                                else:
                                    _play_msg_with_other(self, [next_item +", is already in Follow(" + item + ")"], raw_msg=item + "is already in the follow set.")   
                            else:
                                # we add the first of the non-terminal at this next index
                                tmp_follow = self.cfg.first_set[next_item]
                                next_cfg_element = self.manim_prod_dict[production][i][index + 1]

                                # highlight the next element we are looking at
                                if re.match(RE_TERMINAL, next_item):
                                    self.play(
                                        m.Circumscribe(
                                            next_cfg_element, color=m.TEAL, shape = m.Circle),
                                        m.FadeToColor(next_cfg_element, color=m.TEAL),
                                    )
                                else:
                                    self.play(
                                        m.Circumscribe(
                                            next_cfg_element, color=m.RED, shape = m.Circle),
                                        m.FadeToColor(next_cfg_element, color=m.RED),
                                    )
                                
                                _play_msg_with_other(self, ["{First ("+next_item+") - #}", "\\subseteq Follow (" + item + ")"], raw_msg = "The first set of " + next_item + " without epsilon is a subset of " + item + "'s follow set.")

                                for t in tmp_follow:
                                    if t != "#":
                                        if t not in self.cfg.follow_set[item]:
                                            self.cfg.follow_set[item].append(t)
                                            self._add_to_follow_vis(
                                                item, t, keys, [t + " \\in \{First("+next_item+"\\) - \\epsilon\}"])
                                    else:

                                        if index + 1 == len(pps) - 1:
                                            # if B -> # and A -> aB, then follow(a) = Follow(A) 
                                            if production not in self.follow_set[item]: 
                                                self.follow_set[item].append(production)
                                                self._add_to_follow_vis(
                                                item, production, keys, ["\\epsilon \\subseteq First("+next_item+"),", "so "+next_item+ "may not", "actually appear after "+item, " From this, Follow(" + item + ") \\subseteq Follow(" + production +")"], raw_msg = "Epsilon is in the first set of " + item + " so the non terminal "+next_item + " might not actually appear after " + item)
                                        else:
                                            self.follow_set[item].append(next_item)
                                            self._add_to_follow_vis(
                                                item, next_item, keys, ["\\epsilon \\subseteq First("+next_item+"),", "so "+next_item+ "may not", "actually appear after "+item], raw_msg = "Epsilon is in the first set of " + item + " so the non-terminal "+next_item + " might not actually appear after " + item)

            # start cleaning the follow set
            self.is_cleaned = []
            self.is_cleaned = self.cfg.get_reset_cleaned_set()
            self.clean_follow_set(self.cfg.start_symbol, [])
            sounds.narrate("Time to simplify the sets.", self)
            self.wait()


            # transform current follow sets to cleaned versions
            for key in reversed(self.cfg.follow_set.keys()):
                if not re.match(RE_TERMINAL, key):
                    new_fs_group = m.VGroup()
                    has_eos = False

                    # rewrite the elements of the set
                    for item in self.cfg.follow_set[key]:
                        if item == "$":
                            has_eos = True
                        else:
                            new_fs_group.add(
                                m.Tex(_to_tex(item), color = m.BLUE).scale(TEXT_SCALE))

                    # puts $ at end of list for consistency
                    if has_eos:
                        new_fs_group.add(
                            m.Tex(_to_tex("$"), color = m.BLUE).scale(TEXT_SCALE))
                    new_fs_group.arrange_in_grid(rows=1, buff=0.5).next_to(
                        self.cfg.manim_followset_lead[key], m.RIGHT)

                    # transform to new contents
                    self.play(
                        m.Transform(
                            self.cfg.manim_followset_contents[key], new_fs_group),
                    )

            # show success
            sounds.add_sound_to_scene(self, sounds.YAY)
            sounds.narrate("Awesome. We found the follow set!", self)
            self.play(
                m.FadeOut(keys)
            )
                                
# cleans the follow set up after everything is found, so that we don't miss elements
# TODO fix later from other work
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

    def _add_to_follow_vis(self, production, item, keys, msg=[], raw_msg = ""):
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
                _play_msg_with_other(self, msg, raw_msg = raw_msg)
                sounds.add_sound_to_scene(self, sounds.CLANG)
                self.play(
                    m.FadeIn(new_element)
                )

            else:
                # adds sound as the new element is added
                sounds.add_sound_to_scene(self, sounds.CLANG)
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
            anims.append(m.FadeToColor(cfg_line, config.opp_col()))

            # add the follow set titles to the canvas
            if self.cfg.manim_followset_lead[production] == None:
                self.cfg.manim_followset_lead[production] = m.Tex("Follow(" + production + "):", color = config.opp_col()).align_to(cfg_line, m.UP).shift(m.LEFT)
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
    
    def tear_down(self):
        clear_narrs()

    def vis_populate_table(self):
        """Visualises the algorithm which constructs the parsing table

        Args:
            scene (_type_): _description_
        """
        # make sure parse table is fully reset
        self.pt_dict = {}
        self.init_pt_dict()

        all_elements = m.VGroup()

        # set up the title
        ll1_title = _get_title_mobject("LL(1) parsing: parse table")
        sounds.narrate("Let's find the parse table for this grammar.", self)
        keys = get_manim_cfg_group(self)
        keys.scale_to_fit_height(CFG_SCALE_HEIGHT/3)
        all_elements.add(keys)

        # show key for colour coding
        cfg_heading = m.Tex("Context-Free Grammar", tex_template = m.TexFontTemplates.french_cursive).next_to(keys, m.UP).align_to(keys.get_center)
        cfg_heading.scale(0.6)

        # draw establishing table animations
        row_labels = self.nts
        col_labels = ts_m_epsilon(self)

        # build up the row values
        row_vals = init_row_contents(self)

        # add the table
        self.mtable = self.init_m_table(
            row_vals, row_labels, col_labels)
        self.mtable.get_row_labels().fade_to(color=m.RED, alpha=1)
        self.mtable.get_col_labels().fade_to(color=m.TEAL, alpha=1)
        self.mtable.scale_to_fit_height(CFG_SCALE_HEIGHT)
        all_elements.add(self.mtable)

        # add the guide 
        guide = get_guide(arr_right= True)
        guide.scale_to_fit_height(CFG_SCALE_HEIGHT/4)
        
        # arrange all items
        all_elements.arrange_in_grid(rows = 1, buff = 1)
        all_elements.center()

        # scale everything nicely
        all_elements.scale_to_fit_width(CFG_SCALE_WIDTH)
        cfg_heading.next_to(keys, m.UP)

        sounds.add_sound_to_scene(self, sounds.MOVE)
        self.play(
            ll1_title.animate.to_edge(m.UP),
            guide.animate.to_edge(m.DOWN),
            m.FadeIn(cfg_heading),
            m.LaggedStart(*(m.FadeIn(k, shift=m.UP)
                        for k in keys)),
        )

        # add typing sound as the labels are drawn
        sounds.add_sound_to_scene(self, sounds.TYPE)
        self.play(
           m.Write((self.mtable).get_labels()),
            run_time=1
        )

        self.play(
            m.Create((self.mtable).get_horizontal_lines()[2]),
            m.Create((self.mtable).get_vertical_lines()[2]),
            run_time=2
        )

        # populate the whole table with the first and follow set, if appropriate
        for i, key in enumerate(self.cfg.first_set.keys(), start=0):
            # reset all lines to gray
            keys.fade_to(m.GRAY, 1)

            # highlight the CFG line
            cfg_line = self.manim_production_groups[key][:]
            self.play(
                    m.FadeToColor(cfg_line, color=config.opp_col())
            )

            for j, item in enumerate(self.cfg.first_set[key], start=0):
                # if the first set contains epsilon, may disappear
                if item == "#":
                    for f in self.cfg.follow_set[key]:
                        if f == "$":
                            mprod = key + " \\to $"
                            prod = key + " -> $"
                        else:
                            mprod = key + " \\to \epsilon"
                            prod = key + " -> #"
                        _play_msg_with_other(self, ["Following " + prod + "adds #", " to First(" + _to_tex(key) + ")"], raw_msg = "If we follow "+key+"'s production, we find an epsilon. So, we add this production to the parse table.")
                        self.wait()

                        code = self.vis_add_to_parsetable( key, f, prod, mprod)
                        if code == ERROR:
                            sounds.add_sound_to_scene(self, sounds.FAIL)
                            return
                else:

                    # add item to the parse table
                    prod = self.cfg.firstset_index[key][j]
                    mprod = prod
                    tmp_prod = prod.replace(
                        "->", "\\to").strip().replace("#", "\epsilon")
                    _play_msg_with_other(self, ["Following " + prod + " adds " +
                                 self.cfg.first_set[key][j], " to First(" + key + ")"], raw_msg = "If we follow " + key + "'s production, we encounter terminal " + self.cfg.first_set[key][j] + ". So, let's add this production to the parse table at row " + key + " and column " + self.cfg.first_set[key][j])
 
                    code = self.vis_add_to_parsetable(
                         key, item, prod, tmp_prod)
                    if code == ERROR:
                        sounds.add_sound_to_scene(self, sounds.FAIL)
                        return
        
        self.wait()
        sounds.add_sound_to_scene(self, sounds.YAY)
        sounds.narrate("The parse table is complete. Yay!", self)
        return SUCCESS

    def vis_add_to_parsetable(self, nt, t, prod, mprod):
        try:
            if self.pt_dict[nt][t] != None:
                _play_msg_with_other(self, ["Cannot add entry: There is already a production", "at ParseTable[" + nt +", " + t +"].", "NOTE: This grammar cannot be parsed with LL(1)." ], raw_msg = "There's already an entry, so this grammar is unsuitable for LL(1) parsing.")
                error.ERR_too_many_productions_ll1(nt, t)
                return ERROR
            else:
                self.pt_dict[nt][t] = prod
                self.swap(row(self.cfg, nt), col(self.cfg, t), mprod)

        except KeyError:
            self.pt_dict[nt][t] = prod
            self.swap(row(self.cfg, nt), col(self.cfg, t), mprod)
        return SUCCESS

    # swap a current entry
    def swap(self, row, col, new_val) -> m.MathTable:
        """Swaps two elements in a manim parse table.

        Args:
            row (int): Row of element to be swapped.
            col (int): Column of element to be swapped.
            new_val (String): Value to be swapped into the table. 
        """        
        global GRID_ITEM_SCALE
        GRID_ITEM_SCALE = self.mtable.width / len(self.cfg.terminals)

        t_old = self.mtable.get_entries_without_labels((row, col))

        self.play(
            m.Indicate(t_old, color = config.opp_col())
        )

        # set up new value with colour
        t_new = m.MathTex(_to_math_tex(new_val))
        t_new.scale_to_fit_width(GRID_ITEM_SCALE).scale(0.7)
        t_new.move_to(t_old)
        t_new.fade_to(config.opp_col(), alpha=0.2)

        # fade out old value and into new value
        sounds.add_sound_to_scene(self, sounds.CLACK)
        self.play(
            m.FadeIn(t_new),
            m.FadeOut(t_old),
        )

        self.play(
            m.ApplyWave(t_new),
        )

        # pause
        self.wait()

    def init_m_table(self, row_vals, row_labels, col_labels):
        row_labels = row_labels
        col_labels = col_labels

        table = m.MathTable(
            row_vals,
            row_labels=[m.MathTex(_to_math_tex(rl)) for rl in row_labels],
            col_labels=[m.MathTex(_to_math_tex(cl)) for cl in col_labels],
            include_outer_lines=True)

        # Table
        lab = table.get_labels()
        lab.set_color(m.LIGHT_GRAY)
        table.get_horizontal_lines()[2].set_stroke(width=3, color=m.LIGHT_GRAY)
        table.get_vertical_lines()[2].set_stroke(width=3, color=m.LIGHT_GRAY)
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
            row_labels=[m.MathTex(_to_math_tex(rl)) for rl in self.row_labels],
            col_labels=[m.MathTex(_to_math_tex(cl)) for cl in self.col_labels],
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
    pos = g[parent_id].get_center()+m.DOWN
    v = g._add_vertex(
        vertex_id, vertex_config={"color": color}, position=pos)
    v.fill_colour = color

    if link:
        g._add_edge(
            [parent_id, vertex_id], edge_config={"color": config.opp_col()})
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
        set_up_token_colour(self)
        self.tok_cols = []

        for t in self.tokens:
            self.tok_cols.append(get_token_colour(self))

        self.cfg = cfg
        self.nts = sorted(cfg.nonterminals)
        self.ts = sorted(cfg.terminals)

    def construct(self):
        self.vis_parse_ll1(self.inp, self.tokens)
    
    def tear_down(self):
        self.mtable = None
        self.root = None
        clear_narrs()
        
    def init_m_table(self, row_vals, row_labels, col_labels):
        row_labels = row_labels
        col_labels = col_labels

        table = m.MathTable(
            row_vals,
            row_labels=[m.MathTex(_to_math_tex(rl)) for rl in row_labels],
            col_labels=[m.MathTex(_to_math_tex(cl)) for cl in col_labels],
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

    def _fade_in_mtable(self, highlight = False, row = -1, col = -1, first_time = False):
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.theme_col(), fill_opacity=0.9)

        pt_title = _get_title_mobject("Parse table")
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
            typer.echo("row and col: " + str(row) +", " + str(col))
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

        # draw LL(1) representation title
        ll1_title = _get_title_mobject("LL(1) parsing")
        _play_msg_with_other(self, ["Parsing `" +  " ".join(original_tokens) + "' :)"], raw_msg = "Let's apply the L L 1 parsing algorithm")
        keys = get_manim_cfg_group(self).to_edge(m.DOWN)

        # create the input group here
        m_tok = {}
        m_tok_gp = m.VGroup()
        m_tok_gp.add(m.Tex("Token stream: ")).scale(0.7)
        for t in tokens:
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
                    _play_msg_with_other(self, ["Expected `" + self.s.stack[-1] + "'", "Parsing unsuccessful."], raw_msg = "We expected to see " + self.s.stack[-1]  + " so parsing is unsuccessful.")
                    error.ERR_parsing_error("Expected " + self.s.stack[-1])
                else:
                    _play_msg_with_other(self, ["Parsing unsuccessful. "], raw_msg = "Parsing unsuccessful.")
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

                    sounds.narrate("The next token " + next + " matches the top of the stack!", self)
                    self.wait()

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
                                            popped.id, parent=p, id=popped.id, manim=m.Tex(popped.id, color = m.BLACK))

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
                                                        g, vertex_id, parent_id, "\epsilon", color = self.tok_cols[original_tokens.index(next)])
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
                            rendered_label = m.Tex(
                                top, color = m.BLACK)
                            new_vertex.fade_to(m.BLUE, 1)
                            rendered_label.move_to(new_vertex.get_center())
                            new_vertex.add(rendered_label)
                            
                            sounds.add_sound_to_scene(self, sounds.CLICK)
                            self.play(
                                m.Circumscribe(new_vertex, color=m.BLUE, shape = m.Circle),
                            )
                            try:
                                edge = g.edges[(parent_vertex_id, vertex_id)]
                                anims.append(
                                    m.FadeToColor(edge, color=config.opp_col()))
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
                               _to_tex(self.s.stack[-1]) + "\\text{!}")


                    # highlight the token stream line and token that we matched
                    sounds.add_sound_to_scene(sounds.YAY, self)
                    self.play(m.ApplyWave(m_tok_gp))
                    self.play(
                        m.LaggedStart(m.Indicate(m_tok[next], color=m.BLUE, scale_factor=1.5),
                                    m.FadeToColor(
                            m_tok[next],m.BLUE)),
                    )

                else:
                    sounds.add_sound_to_scene(self, sounds.FAIL)
                    _play_msg_with_other(self, ["Invalid input: '" + top + "'"], raw_msg = top + " leads to a parsing error, so this input is not valid." )
                    error.ERR_parsing_error(
                        "Unexpected token [" + top + "]")
                    error.ERR_manim_parsing_error(self)
                    return

            elif re.match(RE_NONTERMINAL, top):
                try:
                    pt_entry = self.cfg.parsetable.pt_dict[top][next]
                    prods = pt_entry.split("->")
                    _play_msg_with_other(self, ["We must find the entry at ParseTable["+top+"]["+next+"]"], raw_msg = "Let's consider the parse table entry at non-terminal " + top + "'s row and terminal " + next + "'s column.")

                    # highlight parse table row
                    self._fade_in_mtable(highlight  = True, row = row(self.cfg, top), col = col(self.cfg, next))
                    
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
                                   _to_tex(popped_off), color = m.BLACK)

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
                               msg="\\text{Replacing }" + _to_tex(popped_off) + "\\text{...}")

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))

                    _play_msg_with_other(self, [_to_tex(popped_off) + " is a non-terminal,", "so we can replace it with", "its sub-productions: ",  prods[1]], raw_msg="Let's replace " + popped_off + " with its sub productions")

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
                            self.s.push(p, _to_tex(new_prod))
                            self.parents.append(new_node)

                    self.play(
                        m.FadeOut(cfg_line)
                    )

                except KeyError:
                    sounds.add_sound_to_scene(self, sounds.FAIL)
                    _play_msg_with_other(self, ["No such entry at ParseTable[" + top + ", " + next + "].", "Invalid input: `" + next + "'"], raw_msg = next + " leads to a parsing error, so this input is not valid." )
                    error.ERR_parsing_error(self.root, 
                        "No such entry at ParseTable[" + top + ", " + next + "].")
                    return

            # transform the tree
            reset_g(self, g, start_symbol)

        # in case parsing finishes but there are still tokens left in the stack
        if len(tokens) > 0:
            sounds.add_sound_to_scene(self, sounds.FAIL)
            _play_msg_with_other(self, ["The stack is not emptied,", "but parsing has concluded."], raw_msg = "Since the stack is not emptied, parsing is unsuccessful.")
            error.ERR_parsing_error()
            error.ERR_manim_parsing_error(self)
            return

        # fade out the stack and transform the parse tree
        sounds.narrate("Stack emptied.", self)
        self.s.write_under_stack("\\text{Stack emptied.}")
        reset_g(self, g, start_symbol, anim=[m.FadeOut(self.s.mstack), m.FadeOut(self.mtable)])

        sounds.add_sound_to_scene(self, sounds.YAY)
        _play_msg_with_other(self, ["Successfully parsed `" + " ".join(original_tokens) +
                                "'!"], raw_msg= "Parsing successful! That was a valid input.")

        display_helper.success_secho("Successfully parsed '" + " ".join(original_tokens) +
                              "'!\nParse tree:")
        display_helper.print_parsetree(self.root)
        return SUCCESS

