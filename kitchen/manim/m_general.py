""" Creates Kitchen animations """
# kitchen/animation.py

from pathlib import Path
import manim as m

from kitchen import (
    SUCCESS,
    COLOURS_DARK,
    COLOURS_LIGHT
)

from kitchen.helpers import (
    sounds,
    config,
    display
)

from kitchen.backend import *

def get_title_mobject(title):
    """Obtains a title Mobject.

    Args:
        title (str): Contents of title.

    Returns:
        Tex: Tex Mobject.
    """    
    return m.Tex(title, tex_template=m.TexFontTemplates.french_cursive, 
    color = config.get_opp_col())

def to_tex(item):
    """Converts a string to its Tex-compatible representation.

    Args:
        item (str): String to be converted.

    Returns:
        str: Tex-compatible string.
    """    
    tex_item = item.replace(r'$', r'\$').replace(r'#', r'\varepsilon').\
    replace(r'\subseteq', r'$\subseteq$').replace(r'->', r'$\to$')
    tex_item = tex_item.replace(r'\varepsilon', 
    r'$\varepsilon$').replace(r'{', r'$\{$').replace(r'}', r'$\}$')
    #display.fail_secho(tex_item)
    return tex_item

def to_math_tex(item):
    """Converts a string to its MathTex-compatible representation.

    Args:
        item (str): String to be converted.

    Returns:
        str: MathTex-compatible string.
    """    
    tex_item = item.replace(r'$', r'\$').replace(r'#', r'\varepsilon')\
    .replace(r'->', r'\to')
    return tex_item

def display_msg(self, msg, script = "", anim=[], error = False, central =\
    False, success = False):
    """Displays a set of messages in full-screen, alongside optional narration. 

    Args:
        msg (str): Messages to be displayed.
        script (str, optional): Narration script. Defaults to "".
        anim (list, optional): Group of simultaneous animations. 
        Defaults to [].

    Returns:
        _type_: _description_
    """    
    if msg != []:
        msg_group = m.VGroup()

        for ms in msg:
            if error:
                col = m.RED
            else:
                if success: col = m.GREEN
                else: col = m.BLUE_C
            msg = to_tex(ms)
            display.fail_secho(msg)
            msg_txt = m.Tex(msg, color=col).scale(0.7)
            msg_group.add(msg_txt)
        msg_group.arrange(m.DOWN)
        if not central:
            msg_group.to_edge(m.RIGHT).shift(m.DOWN)
        
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=config.get_theme_col(), 
        fill_opacity=0.8)

        self.play(
            m.FadeIn(rect),
        )

        # generate voiceover
        if script != "":
            sounds.narrate(script, self)

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
        return list(filter(None, inp.split(" ")))

def set_up_token_colour(self):
    """Sets up the ten options for colour coding the tokens
    """    
    self.token_has_this_colour = []
    # set up colour boolean array
    for i in range(10):
        self.token_has_this_colour.append(False)

def get_token_colour(self):
    """Obtains an unclaimed token colour.

    Returns:
        Color: A unique colour if available, otherwise one which contrasts
        the theme.
    """    
    if config.get_theme_name() == "dark":
        colour_palette = COLOURS_LIGHT
    else:
        colour_palette = COLOURS_DARK

    for index, col in enumerate(colour_palette, start=0):
        if not self.token_has_this_colour[index]:
            self.token_has_this_colour[index] = True
            return col
    return m.DARKER_GRAY()

# fades the scene out
def fade_scene(self):
    self.play(
        *[m.FadeOut(mob) for mob in self.mobjects]
    )

def row(nts, nt):
    """Gets the row index of the parse table contents.

    Args:
        cfg (ContextFreeGrammar): CFG 
        nt (str): Non-terminal 

    Returns:
        int: Row of non-terminal
    """    
    return nts.index(nt) + 1

def col(ts, t):
    """Gets the column index of the parse table contents.

    Args:
        cfg (ContextFreeGrammar): CFG     
        nt (str): Non-terminal 

    Returns:
        int: Column of non-terminal
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
    keys.arrange_in_grid(rows=row_no, buff=1.5, aligned_edge = m.LEFT)
    keys.fade_to(color=m.DARK_GRAY, alpha=1)
    return keys

def get_guide(arr_right = False):
    """Obtains a guide for the colour coding of terminals and non-terminals.

    Args:
        arr_right (bool, optional): Whether the guide should be arranged
        horizontally (i.e. elements are to the right of each other). Defaults 
        to False.

    Returns:
        VGroup: Guide Mobject.
    """    
    guide_group_outer = m.VGroup()
    square_colors = [m.TEAL, m.RED]
    labels = ["Terminal", "Non-terminal"]
    for i in range(2):
        guide_group_inner = m.VGroup()
        guide_group_inner.add(m.Square().set_fill(
            square_colors[i], opacity=1).scale(0.5))
        guide_group_inner.add(m.Tex(labels[i], color = config.get_opp_col()))
        guide_group_inner.arrange_in_grid(rows = 1, buff = 0.8)
        guide_group_outer.add(guide_group_inner)
    
    if not arr_right:
        guide_group_outer.arrange_in_grid(rows = len(labels), buff = 0.8)
        return guide_group_outer.arrange(m.DOWN, aligned_edge=m.LEFT)
    else:
        guide_group_outer.arrange_in_grid(rows = 1, buff = 0.8) 
        return guide_group_outer





