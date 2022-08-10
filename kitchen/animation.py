""" Creates Kitchen animations """
# kitchen/animation.py

from re import S
import manim as m
import re

from kitchen import (
    RE_PRODUCTION, 
    RE_TERMINAL,
    display_helper,
    TEXT_SCALE,
    COLOURS,
    error
)



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
    err_m_msg = m.Text(err_msg, color=m.WHITE)
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

    # def align_notify(message, production):
    #     # returns a keys group, which is the cfg representation
    #     msg_text = m.Text(message, color=m.YELLOW, weight=m.BOLD).scale(0.5).next_to(
    #         manim_production_groups[production], m.RIGHT).shift(m.RIGHT*5)
    #     self.play(
    #        m.Write(msg_text),
    #     )
    #     self.wait()
    #     self.play(
    #         m.FadeOut(msg_text)
    #     )

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

        # add A -> to the production group
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

    keys.arrange(m.DOWN)
    keys.fade_to(color=m.DARK_GRAY, alpha=1)
    return keys

# TODO move some values across
# TODO let animation restart again
# Unique filename - Date and time?
# TODO neaten up animation 

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
    pass

class ManimParsingTable(m.Scene):
    def setup(self):
        self.frame_width = m.config["frame_width"]
        self.frame_height = m.config["frame_height"]
    def __init__(self):
        pass

    def swap(self, row, col, new_val):
        """Swaps two elements in a manim parse table.

        Args:
            row (int): Row of element to be swapped.
            col (int): Column of element to be swapped.
            new_val (String): Value to be swapped into the table. 
        """        
        t_old = self.table.get_entries_without_labels((row, col))

        # set up new value with colour
        t_new = m.Tex(new_val)
        t_new.move_to(t_old)
        t_new.fade_to(m.TEAL, alpha=1)

        # fade out old value and into new value
        self.play(
            m.FadeIn(t_new),
            m.FadeOut(t_old),
        )


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

class ManimParseTree(m.Scene):
    pass