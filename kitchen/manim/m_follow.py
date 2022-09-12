""" Generates a visualisation of the follow set calculation. """
# kitchen/manim/m_follow.py

import manim as m
import re

from kitchen import (
        CFG_SCALE_HEIGHT, 
        CFG_SCALE_WIDTH, 
        RE_PRODUCTION, 
        RE_TERMINAL, 
        RE_NONTERMINAL
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
        mg.display_msg(self, ["The Follow Set of X contains all the TERMINALS",\
        "which can appear straight AFTER X."], central = \
        True)
        sounds.narrate("Let's find the Follow Set.", self)
        display.info_secho("Visualising the Follow Set calculation:")
        self.vis_follow_set(True)
    
    def tear_down(self):
        """Concludes the scene.
        """        
        for key in self.cfg.follow_set.keys():
            self.cfg.follow_set[key] = []
        sounds.clear_narrs()

    def vis_follow_set(self, is_start_symbol):
        """Visualises the follow set calculation.

        Args:
            is_start_symbol (bool): Whether the initial pass is the start.
        """        

        # sets up CFG keys
        keys = mg.get_manim_cfg_group(self)

        keys.scale(0.8)
        if keys.width > CFG_SCALE_WIDTH/ 3:
            keys.scale_to_fit_width(CFG_SCALE_WIDTH/ 3)
        
        if keys.height > 6/5*CFG_SCALE_HEIGHT/2:
            keys.scale_to_fit_height(6/5*CFG_SCALE_HEIGHT/ 2)

        keys.fade_to(m.GRAY, 1).to_edge(m.LEFT)

        # draws follow set title
        fw_title = mg.get_title_mobject("follow set calculation") 
        guide = mg.get_guide(arr_right = True).scale_to_fit_width\
            (CFG_SCALE_WIDTH/2)

        # sets the stage
        self.play(
            fw_title.animate.to_edge(m.UP),
            guide.animate.to_edge(m.DOWN),
            m.FadeIn(keys)
        )
        
        # obtains set for each production
        for production in self.cfg.cfg_dict.keys():

            # fades the other keys to gray
            self._prepare_follow_set_line(production, keys)

            # Rule 1: $ ∈ Follow(S)
            if is_start_symbol:
                self.cfg.follow_set[production].append("$")
                self._add_to_follow_vis(
                    production, "$", keys, [production + " is the start " +
                        "symbol,", "so we append $", "to Follow(" +
                    production + ")"], script = production + ", is the " +
                        "start symbol, so we append $ to its Follow Set.")
                is_start_symbol = False

            # inspect each element in the production
            for i, p in enumerate(self.cfg.cfg_dict[production]):

                # split up the productions which are contained within this list
                pps = list(filter(None, re.findall(RE_PRODUCTION, p)))

                for index, item in enumerate(pps, start=0):
                    # highlight the element we are inspecting
                    cfg_element = self.manim_prod_dict[production][i][index]

                    # highlight CFG items as we inspect them
                    if re.match(RE_TERMINAL, item):

                        # observe that the follow of a standalone terminal may
                        # be ε
                        if index == len(pps) - 1:
                            # prepare simultaneous animations
                            anims = []
                            tmp_anim = [m.Circumscribe(cfg_element, 
                                        color=m.TEAL, 
                                        shape = m.Circle),
                                        m.FadeToColor(cfg_element, 
                                                      color=m.TEAL)]

                            for t in tmp_anim:
                                anims.append(t) 

                            mg.display_msg(self, ["Follow(" + item +
                            ") may not exist"], script = "Nothing can " +
                            "follow " + item + " so it does not have a "+
                            "Follow Set.")

                        else:
                            # just highlight the terminal
                            self.wait()
                            sounds.narrate(item + " , is a terminal.", self)
                            self.play(
                                m.Circumscribe(cfg_element, color=m.TEAL, 
                                                shape = m.Circle),
                                m.FadeToColor(cfg_element, color=m.TEAL),
                            )

                    else:
                        self.wait()
                        sounds.narrate("Let's now look at " +item +", which " +
                            "is a non terminal.", self)

                        self.play(
                            m.Circumscribe(cfg_element, color=m.RED, 
                                            shape = m.Circle),
                            m.FadeToColor(cfg_element, color=m.RED),
                        )
                        self.wait()

                    # starts processing
                    if index == len(pps) - 1 and item != "#" and \
                        item != production:
                        # temporarily appends production to let us then iterate 
                        # over and replace it
                        if production not in self.cfg.follow_set[item]:
                            self.cfg.follow_set[item].append(production)
                            self.wait()
                            self._add_to_follow_vis(
                                item, production, keys, ["Follow(" + 
                                production + ") \\subseteq Follow(" +
                                item + ")"], script = "The Follow Set of " +
                                production + " is a subset of that of " + 
                                item + " ")
                        else:
                            mg.display_msg(self, [next_item + ", is already " +
                                "in Follow(" + item + ")"], script=item +
                                "is already in the Follow Set.")                                   
                    
                    elif index < len(pps) - 1:
                        next_item = pps[index + 1]
                        # if an item is directly followed by a terminal, it 
                        # is appended to its follow set
                        if re.match(RE_TERMINAL, next_item):
                            if next_item not in self.cfg.follow_set[item]:
                                self.cfg.follow_set[item].append(next_item)
                                self._add_to_follow_vis(
                                    item, next_item, keys)
                            else:
                                mg.display_msg(self, [next_item +", is "+
                                    "already in Follow(" + item + ")"], 
                                    script=item + "is already in the Follow " +
                                    "Set.")   
                        else:
                            # we add the first of the non-terminal at this 
                            # next index
                            tmp_first = self.cfg.first_set[next_item]
                            next_cfg_element = self.manim_prod_dict\
                                [production][i][index + 1]

                            # highlights the next element we are looking at
                            if re.match(RE_TERMINAL, next_item):
                                self.play(
                                    m.Circumscribe(
                                        next_cfg_element, color=m.TEAL, 
                                        shape = m.Circle),
                                    m.FadeToColor(next_cfg_element, 
                                    color=m.TEAL),
                                )
                            else:
                                self.play(
                                    m.Circumscribe(
                                        next_cfg_element, color=m.RED, 
                                        shape = m.Circle),
                                    m.FadeToColor(next_cfg_element, 
                                    color=m.RED),
                                )
                            
                            mg.display_msg(self, [r'{First (' +next_item +
                                r') - #}', r'\subseteq Follow (' + item + 
                                r')'], script = "The First Set of " + 
                                next_item + " without epsilon is a subset of "+
                                    "of " + item + "'s Follow Set.")

                            for t in tmp_first:
                                if t != "#":
                                    if t not in self.cfg.follow_set[item]:
                                        self.cfg.follow_set[item].append(t)
                                        self._add_to_follow_vis(
                                            item, t, keys, 
                                            [t + r'in {First(' + next_item +
                                            r') - \varepsilon}'])
                                else:

                                    if index + 1 == len(pps) - 1:
                                        # if B -> # and A -> aB, then 
                                        # follow(a) = Follow(A) 
                                        if production not in self.cfg.follow_set\
                                            [item]: 
                                            self.cfg.follow_set[item].append\
                                                (production)
                                            self._add_to_follow_vis(
                                            item, production, keys, 
                                            [r'\varepsilon \subseteq First (' +
                                            next_item+r'),', r'so '+ 
                                            next_item + r'may not', 
                                            r'actually appear after' + item,
                                            r' From this, Follow (' + item +
                                             r') \subseteq Follow (' + 
                                             production + r')'], 
                                             script = "Epsilon is in the \
                                             first set of " + item + " so the \
                                             non terminal "+ next_item + 
                                             " might not actually appear \
                                                after " + item)
                                    else:
                                        self.cfg.follow_set[item].append(next_item)
                                        self._add_to_follow_vis(
                                            item, next_item, keys,
                                            [r'\varepsilon \subseteq First ('+
                                            next_item+r'),', r'so '+next_item+
                                            r'may not', r'actually appear after '
                                            +item], script = "Epsilon is in \
                                            the First Set of " + item + " so \
                                            the non-terminal "+next_item + 
                                            " might not actually appear after " 
                                            + item)

        # starts cleaning the follow set
        is_cleaned = []
        is_cleaned = self.cfg.get_reset_cleaned_set()
        self.cfg.clean_follow_set(self.cfg.start_symbol, [], is_cleaned)
        sounds.narrate("Time to simplify the sets.", self)
        self.wait()

        # transforms current follow sets to cleaned versions
        for key in reversed(self.cfg.follow_set.keys()):
            if not re.match(RE_TERMINAL, key):
                new_fs_group = m.VGroup()
                has_eos = False

                # rewrites the elements of the set
                for item in self.cfg.follow_set[key]:
                    if item == "$":
                        has_eos = True
                    else:
                        new_fs_group.add(m.Tex(mg.to_tex(item), color = m.BLUE_D))

                # puts $ at end of list for consistency
                if has_eos:
                    new_fs_group.add(m.Tex(mg.to_tex("$"), color = m.BLUE_D))
                new_fs_group.arrange_in_grid(rows=1, buff=0.5).next_to(
                    self.cfg.manim_followset_lead[key], m.RIGHT)
                new_fs_group.scale_to_fit_height(\
                    self.cfg.manim_followset_lead[key].height)

                # transforms to new contents
                self.play(
                    m.Transform(
                        self.cfg.manim_followset_contents[key], new_fs_group),
                )

        # shows success
        sounds.add_sound_to_scene(self, sounds.YAY)
        self.play(
            m.Flash(keys, line_length=0.3,
            num_lines=30, color=m.BLUE_D,
            flash_radius=0.3,
            time_width=0.3),
        )
        sounds.narrate("We found the follow set!", self)
                            

    def _add_to_follow_vis(self, production, item, keys, msg=[], script = ""):
        """Visualises the addition of an element to a follow set.

        Args:
            production (str): Production whose follow set is to be appended to.
            item (str): Item to be appended.
            keys (VGroup): CFG Mobject group.
            msg (list, optional): Set of messages which will be displayed
            as the item is added to the set. Defaults to [].
            script (str, optional): Narration script for the action. 
            Defaults to "".
        """        
        new_element = None

        if not re.match(RE_TERMINAL, production) and item != production:
            # display adding to the non-terminal followsets
            self._prepare_follow_set_line(production, keys)

            # check if item to be added is a non-terminal
            if re.match(RE_NONTERMINAL, item):
                # non terminal
                new_element = m.Tex(
                    r'Follow(', mg.to_tex(item), ')', color=m.BLUE_D).\
                        scale(0.8)

            else:
                # append it directly as a terminal
                element = mg.to_tex(item) 
                new_element = m.Tex(
                    element, color=m.TEAL).scale(0.8)
                    
            if new_element.height > self.cfg.manim_followset_lead\
                    [production].height:
                    new_element.scale_to_fit_height\
                (self.cfg.manim_followset_lead[production].height)

            # add to the content group
            self.cfg.manim_followset_contents[production].add(
                new_element)
            self.cfg.manim_followset_contents[production].\
                arrange_in_grid(rows=1, buff=0.5)
            self.cfg.manim_followset_contents[production].next_to(
                self.cfg.manim_followset_lead[production], m.RIGHT)

        # Play the addition of the item to the followset and message, if given
            if msg != []:
                mg.display_msg(self, msg, script = script)
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
        """Creates a MObject group for each follow set.

        Args:
            production (str): Group to be created.
            keys (VGroup): CFG Mobject group.
        """        
        # only prepares a follow set for non-terminals
        if not re.match(RE_TERMINAL, production):
            # creates anims buffer
            anims = []

            # highlights manim production
            keys.fade_to(color=m.GRAY, alpha=1)
            cfg_line = self.manim_production_groups[production][:]
            anims.append(m.FadeToColor(cfg_line, config.get_opp_col()))

            # adds the follow set titles to the canvas
            if self.cfg.manim_followset_lead[production] == None:
                self.cfg.manim_followset_lead[production] = \
                    m.Tex("Follow(" + production + "):", 
                    color = config.get_opp_col())
                    
                if self.cfg.manim_followset_lead[production].height > \
                    1.5*cfg_line.height:
                    self.cfg.manim_followset_lead[production].scale_to_fit_height\
                        (1.5*cfg_line.height)
                self.cfg.manim_followset_lead[production].align_to(cfg_line, \
                    m.UP)      

                # prepares content group
                self.cfg.manim_followset_contents[production].next_to(
                    self.cfg.manim_followset_lead[production], m.RIGHT)
                self.cfg.manim_followset_contents[production].arrange(m.RIGHT)

                # shows the new follow area
                anims.append(
                    m.FadeIn(self.cfg.manim_followset_lead[production]),
                )

            # animates the cfg line being highlighted
            self.play(
                *[a for a in anims]
            )
