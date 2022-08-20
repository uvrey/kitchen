""" Creates Kitchen animations """
# kitchen/animation.py

from pathlib import Path
import manim as m

from kitchen import (
    SUCCESS,
    COLOURS,
)

from kitchen.helpers import (
    sounds,
    config,
    display,
)

from kitchen.backend import *

# set global configs
m.config.include_sound = True

def get_title_mobject(title):
    return m.Tex(title, tex_template=m.TexFontTemplates.french_cursive)

def to_tex(item):
    tex_item = item.replace("$", "\$").replace("\epsilon", "$\epsilon$").replace("#", "$\epsilon$").replace("\\subseteq", "$\\subseteq$").replace("->", "$\\to$").replace("(", "$($").replace(")", "$)$")
    return tex_item

def to_math_tex(item):
    tex_item = item.replace("$", "\$").replace("#", "\epsilon").replace("->", "\\to")
    return tex_item

def display_msg(self, msg, raw_msg= "", anim=[]):
    if msg != []:
        msg_group = m.VGroup()

        for ms in msg:
            msg_txt = m.Tex(to_tex(ms), color=config.opp_col())
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

def get_tokens_from_input(inp, spec = None) -> list:
    """Obtains the token stream of an input string. 
    Args:
        inp (str): Input string
    Returns:
        list: Token stream
    """    
    if spec != None:
        tokens = spec.get_tokens_from_input(inp)
        return tokens
    else:
        display.info_secho("Note:\tNo language specification has been provided, so the given \n\tinput will be interpreted as tokens directly.")
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

def row(nts, nt):
    """Quickly get the row and column index of the parse table contents_summary_

    Args:
        cfg (ContextFreeGrammar): CFG 
        nt (str): Non-terminal 

    Returns:
        int: Row of non-terminal
    """    
    return nts.index(nt) + 1

def col(ts, t):
    """Quickly get the row and column index of the parse table contents_summary_

    Args:
        cfg (ContextFreeGrammar): CFG     
        nt (str): Non-terminal 

    Returns:
        int: Row of non-terminal
    """    
    return ts.index(t) + 1

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
        return guide_group_outer.arrange(m.DOWN, aligned_edge=m.LEFT)
    else:
        guide_group_outer.arrange_in_grid(rows = 1, buff = 0.8) 
        return guide_group_outer
    
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



