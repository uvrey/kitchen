""" Generates a visualisation of the first set calculation. """
# kitchen/manim/m_first.py

import manim as m
import re

from kitchen import (
    CFG_SCALE_HEIGHT, 
    CFG_SCALE_WIDTH, 
    RE_PRODUCTION, 
    RE_TERMINAL, 
)

from kitchen.helpers import sounds, config, display, error
from kitchen.manim import m_general as mg

class MFirstSet(m.Scene):
    def setup_manim(self, cfg): 
        """Sets up the structures which the animation will make use of.

        Args:
            cfg (ContextFreeGrammar): Loaded CFG.
        """                    
        self.cfg = cfg
        mg.display_msg(self, ["The First Set of X contains all the TERMINALS",\
            "which can BEGIN a string that is", "derived from X."], central = \
                True)
        
    def construct(self):
        """Constructs the scene.
        """        
        sounds.narrate("Let's find the First Set!", self)
        display.info_secho("Visualising the First Set:")

        # set title and scaling here since the function is recursive
        fs_title = mg.get_title_mobject("first set calculation") 
        self.play(fs_title.animate.to_edge(m.UP))

        keys = mg.get_manim_cfg_group(self)
        keys.scale(0.8)
        if keys.width > CFG_SCALE_WIDTH/ 3:
            keys.scale_to_fit_width(CFG_SCALE_WIDTH/ 3)
        
        if keys.height > CFG_SCALE_HEIGHT/2:
            keys.scale_to_fit_height(CFG_SCALE_HEIGHT/ 2)

        # show key for colour coding
        guide = mg.get_guide(arr_right = True).scale_to_fit_width\
            (CFG_SCALE_WIDTH/2)

        self.vis_first_set(keys, guide, self.cfg.start_symbol, 
        self.cfg.start_symbol, [])

        # success message and sound
        self.play(
            m.Flash(keys, line_length=0.3,
            num_lines=30, color=m.BLUE_D,
            flash_radius=0.3,
            time_width=0.3),
        )
        sounds.add_sound_to_scene(self, sounds.YAY)
        mg.display_msg(self, ["Successfully found the First Set :)"], 
        script= "We successfully found the First Set.")

    def tear_down(self):
        """Clears first set structures at the end of the animation.
        """        
        self.cfg.vis_has_epsilon = False
        self.cfg.manim_firstset_lead = {}
        for key in self.cfg.first_set.keys():
            self.cfg.first_set[key] = []
            self.cfg.manim_firstset_contents[key] = m.VGroup()
        sounds.clear_narrs()

    def vis_first_set(self, keys, guide, start, production, pstack):
        """Generates a visualisation of the first set.

        Args:
            keys (VGroup): CFG keys as a group of Mobjects.
            guide (VGroup): Colour code guide.
            start (str): Start symbol string representation.
            production (str): Production being handled (may be a terminal or
                              a non-terminal).
            pstack (list): Stack of encountered productions.
        """        

        # prevents deep recursion
        if production in pstack and len(pstack) > 1:
            return

        #  global vis_has_epsilon
        pstack.append(production)

        # reset all keys to white except the one we are looking at
        keys.fade_to(color=m.DARK_GRAY, alpha=1)

        # highlight manim production
        cfg_line = self.manim_production_groups[production][:]

    # add the first set titles to the canvas

        self.play(
            m.FadeToColor(cfg_line, color=config.get_opp_col()),
            guide.animate.to_edge(m.DOWN),
            keys.animate.to_edge(m.LEFT)
        )

        sounds.narrate("Let's get the first set of non-terminal " + production\
            , self)
        self.cfg.manim_firstset_lead[production] = m.Tex("First(" + 
        production + "):", color = config.get_opp_col()).align_to(cfg_line, m.UP)

        if self.cfg.manim_firstset_lead[production].height > \
                1.5*cfg_line.height:
                self.cfg.manim_firstset_lead[production].scale_to_fit_height\
                    (1.5*cfg_line.height)

        self.cfg.manim_firstset_contents[production].next_to\
            (self.cfg.manim_firstset_lead[production], m.RIGHT)

        self.play(m.FadeIn(self.cfg.manim_firstset_lead[production]))

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
                            prev_element = self.manim_prod_dict[production]\
                                [i][j-1]

                        # if a terminal is encountered after the list
                        # fade in new terminal and corresponding element of 
                        # the cfg
                        if re.match(RE_TERMINAL, current_item):

                            for ps in pstack:
                                if current_item not in self.firstset[ps]:
                                    self.firstset[ps].append(current_item)
                                    # add this terminal and play VGroup of 
                                    # each production in the stack
                                    new_element = m.Tex(mg.to_tex(current_item), 
                                        color=m.TEAL)

                                    if new_element.height > cfg_line.height:
                                        new_element.scale_to_fit_height\
                                            (1.5*cfg_line.height)

                                    self.manim_firstset_contents[ps].add(
                                        new_element)
                                    self.manim_firstset_contents[ps]\
                                        .arrange_in_grid\
                                        (rows = 1, buff = 0.5).next_to\
                                    (self.cfg.manim_firstset_lead[ps], m.RIGHT)

                                    # fade in new terminal and corresponding 
                                    # element of the cfg
                                    cfg_element = self.manim_prod_dict\
                                        [production][i][j]
                                    sounds.add_sound_to_scene(self, 
                                                    sounds.CLICK)
                                    self.play(
                                        m.FadeIn(new_element),
                                        m.Circumscribe(cfg_element, 
                                                    color=m.TEAL, 
                                                    shape = m.Circle),
                                        m.FadeToColor(cfg_element, 
                                                    color=m.TEAL, 
                                                    shape = m.Circle),
                                    )
                                else:
                                    mg.display_msg(self, 
                                    ["Note: Since First(" + ps + ") may lead \
                                    to ", "the same production via more than \
                                    one", "production, the CFG is ambiguous."],
                                     script = "This CFG is ambiguous, since "+
                                        "more than one production derives the "+
                                        "same terminal.")
                            break
                        else:
                            # highlight the non-terminal
                            cfg_element = self.manim_prod_dict[production]\
                                [i][j]
                          
                            if j > 1:
                                # fade out the previous non-terminal
                                prev_element = self.manim_prod_dict\
                                    [production][i][j-1]
                                prev_element.fade_to(
                                    color=m.DARK_GRAY, alpha=1)
                                prev_element.scale_to_fit_height(1.5*cfg_line.height)

                            # display the message alongside narration
                            mg.display_msg(self, [production + " derives " + 
                                current_item + ",", "so First("+production +
                                ") \\subseteq First("+current_item+")"], 
                                script=production + ", derives another non \
                                    terminal" + current_item + ", so their \
                                    first sets will overlap.")

                            sounds.add_sound_to_scene( self, sounds.CLACK)
                            self.play(
                                m.LaggedStart(
                                m.Circumscribe(cfg_element, color=m.RED, 
                                shape = m.Circle),
                                m.FadeToColor(cfg_element, color = m.RED),
                                )
                            )

                            # ensure we don't add # when unnecessary
                            had_eps = "#" in self.cfg.first_set[current_item]
                            self.vis_first_set(
                                keys, guide, production, current_item, pstack)
                            has_eps = "#" in self.cfg.first_set[current_item]

                            got_eps = had_eps and has_eps
                            len_okay = len(pstack) == 1 and j != len(p_nt) - 1
                            if not got_eps and len_okay:
                                if "#" in self.cfg.first_set[production]:
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
                        # the non-terminal which led to this may disappear in 
                        # the original production
                        self.cfg.vis_has_epsilon = True

                    terminal_to_write = mg.to_tex(first_terminal[0])

                        # appends this terminal to the first set of previous 
                        # non-terminals
                    for ps in pstack:
                        # make sure the production in focus is shaded white
                        self.manim_production_groups[ps].fade_to(
                            color=config.get_opp_col(), alpha=1)

                        # don't add # if we are down the stack
                        # begin adding to its first set
                        if first_terminal[0] not in self.cfg.first_set[ps]:

                            # add to first set
                            self.cfg.first_set[ps].append(first_terminal[0])

                            # add this terminal and play VGroup of each 
                            # production in the stack
                            new_element = m.Tex(
                                    terminal_to_write, color=m.TEAL)
                            if new_element.height > 1.5*cfg_line.height:
                                        new_element.scale_to_fit_height\
                                            (1.5*cfg_line.height)
                            self.cfg.manim_firstset_contents[ps].add(
                                new_element)
                            self.cfg.manim_firstset_contents[ps]\
                                .arrange_in_grid(rows=1, buff = 0.5).next_to\
                                    (self.cfg.manim_firstset_lead[ps], m.RIGHT)
                        else:
                            mg.display_msg(self, ["Note: Since First("+ps+") "+
                                "may lead to ", "the same production via more "+
                                "than one", "production, the CFG is "+
                                "ambiguous."], script = "This CFG is \
                                ambiguous, since more than one production \
                                derives the same terminal.")

                        # Notify as to what is happening
                        msg = []
                        if len(pstack) > 1 and ps != production:
                            msg = ["Terminal " + first_terminal[0] +
                                    " is also", "added to First(" + ps +
                                    "),", "since " + ps + " derives " +
                                    production]
                            script = ps + " derives " + production + \
                            ", so we add " + first_terminal[0] + " to both. "
                        else:
                            msg = ["Terminal " + first_terminal[0] +
                                    " is ", "added to First(" + ps + ")"]
                            script = "Let's add terminal " + \
                            first_terminal[0] + " to the first set of " +\
                            "non-terminal " + ps
                        mg.display_msg(self, msg, script)

                        # fade in new terminal and corresponding element of 
                        # the cfg
                        cfg_element = self.manim_prod_dict[production][i][0]

                        # adds sound as the new element is added
                        sounds.add_sound_to_scene(self, sounds.CLICK)
                        self.add(new_element)

                        self.play(
                            m.Circumscribe(cfg_element, color=m.TEAL, 
                            shape = m.Circle),
                            m.FadeToColor(cfg_element, color=m.TEAL),
                        )

                        # notify about user epsilon if we are somewhere in 
                        # the stack
                        if first_terminal[0] == "#" and ps != start:
                            mg.display_msg(self, ["\\varepsilon found at \
                                production " + production + ",", "so " + 
                                production + " may disappear :)"], 
                                script = "The production may disappear \
                                    since it can lead to epsilon.")

                        # reset other colours to white
                        self.cfg.manim_firstset_contents[ps].fade_to(
                            color=config.get_opp_col(), alpha=1)

                        # reset all cfg lines to white except the one we are 
                        # looking at
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
            mg.display_msg(self, [production + " not given in the CFG."],
            script = "A production led by " + production + " is not " + 
            "given in the context free grammar.", error = True)
            error.ERR_key_not_given_in_CFG(production)





