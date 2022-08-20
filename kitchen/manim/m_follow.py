""" Generates a visualisation of the follow set calculation. """
# kitchen/manim/m_follow.py

import manim as m
import re

from kitchen import (
        CFG_SCALE_HEIGHT, 
        CFG_SCALE, 
        RE_PRODUCTION, 
        RE_TERMINAL, 
        RE_NONTERMINAL,
        TEXT_SCALE
)

from kitchen.helpers import sounds, config, display
from kitchen.manim import m_general as mg

class MFollowSet(m.Scene):
    
    def setup_manim(self, cfg):  
        """Sets up the structures which the animation will make use of.

        Args:
            cfg (ContextFreeGrammar): Loaded CFG.
        """              
        self.cfg = cfg

    def construct(self):   
        """Creates the follow set calculation scene.
        """          
        sounds.narrate("Let's find the follow set.", self)
        display.info_secho("Visualising follow set calculation:")
        self.vis_follow_set(True)
    
    def tear_down(self):
        """Concludes the scene.
        """        
        for key in self.cfg.follow_set.keys():
            self.cfg.follow_set[key] = []
        mg.clear_narrs()

    def vis_follow_set(self, is_start_symbol):
        """Visualises the follow set calculation.

        Args:
            is_start_symbol (bool): Whether the initial pass is the start.
        """        

        # Set up CFG keys
        keys = mg.get_manim_cfg_group(self).to_edge(m.LEFT)
        keys.scale_to_fit_height(CFG_SCALE_HEIGHT)
        keys.fade_to(m.GRAY, 1).to_edge(m.LEFT)

        # draw follow set title
        fw_title = mg.get_title_mobject("follow set calculation") 
        guide = mg.get_guide().scale(CFG_SCALE)

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

            # Rule 1: $ ∈ Follow(S)
            if is_start_symbol:
                self.cfg.follow_set[production].append("$")
                self._add_to_follow_vis(
                    production, "$", keys, [production + " is the start \
                        symbol,", "so we append $", "to Follow(" +
                    production + ")"], raw_msg = production + ", is the \
                        start symbol, so we append $ to its follow set.")
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
                            
                            mg.display_msg(self, ["Follow(" + mg.to_tex(ti) + ") may not exist"], raw_msg = "A standalone non epsilon terminal won't have a follow set.")


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
                            mg.display_msg(self, [next_item +", is already in Follow(" + item + ")"], raw_msg=item + "is already in the follow set.")                                   
                    
                    elif index < len(pps) - 1:
                        next_item = pps[index + 1]
                        # if an item is directly followed by a terminal, it is appended to its follow set
                        if re.match(RE_TERMINAL, next_item):
                            if next_item not in self.cfg.follow_set[item]:
                                self.cfg.follow_set[item].append(next_item)
                                self._add_to_follow_vis(
                                    item, next_item, keys)
                            else:
                                mg.display_msg(self, [next_item +", is already in Follow(" + item + ")"], raw_msg=item + "is already in the follow set.")   
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
                            
                            mg.display_msg(self, ["{First ("+next_item+") - #}", "\\subseteq Follow (" + item + ")"], raw_msg = "The first set of " + next_item + " without epsilon is a subset of " + item + "'s follow set.")

                            for t in tmp_follow:
                                if t != "#":
                                    if t not in self.cfg.follow_set[item]:
                                        self.cfg.follow_set[item].append(t)
                                        self._add_to_follow_vis(
                                            item, t, keys, [t + " \\in \{First("+next_item+"\\) - \\varepsilon\}"])
                                else:

                                    if index + 1 == len(pps) - 1:
                                        # if B -> # and A -> aB, then follow(a) = Follow(A) 
                                        if production not in self.follow_set[item]: 
                                            self.follow_set[item].append(production)
                                            self._add_to_follow_vis(
                                            item, production, keys, ["\\varepsilon \\subseteq First("+next_item+"),", "so "+next_item+ "may not", "actually appear after "+item, " From this, Follow(" + item + ") \\subseteq Follow(" + production +")"], raw_msg = "Epsilon is in the first set of " + item + " so the non terminal "+next_item + " might not actually appear after " + item)
                                    else:
                                        self.follow_set[item].append(next_item)
                                        self._add_to_follow_vis(
                                            item, next_item, keys, ["\\varepsilon \\subseteq First("+next_item+"),", "so "+next_item+ "may not", "actually appear after "+item], raw_msg = "Epsilon is in the first set of " + item + " so the non-terminal "+next_item + " might not actually appear after " + item)

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
                            m.Tex(mg.to_tex(item), color = m.BLUE).scale(TEXT_SCALE))

                # puts $ at end of list for consistency
                if has_eos:
                    new_fs_group.add(
                        m.Tex(mg.to_tex("$"), color = m.BLUE).scale(TEXT_SCALE))
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
                element = mg.to_tex(item) 
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
                mg.display_msg(self, msg, raw_msg = raw_msg)
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
            anims.append(m.FadeToColor(cfg_line, config.config.get_opp_col()))

            # add the follow set titles to the canvas
            if self.cfg.manim_followset_lead[production] == None:
                self.cfg.manim_followset_lead[production] = m.Tex("Follow(" + production + "):", color = config.config.get_opp_col()).align_to(cfg_line, m.UP).shift(m.LEFT)
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
