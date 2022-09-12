""" Stack class. """
# kitchen/backend/m_stack.py

import manim as m
from typer import *
from anytree import *
import re

from kitchen import (
    RE_TERMINAL,
)

from kitchen.helpers import (
    config,
    display,
    sounds
)

class Stack:
    def __init__(self, scene, left_edge, height):
        """Initialises the Stack.

        Args:
            scene (Scene): Manim Scene.
            left_edge (int): X co-ordinate of left edge.
            height (int): Height of Stack.
        """        
        self.stack = []
        self.texts = []
        self.mstack_height = height
        self.le = left_edge
        self.mstack = m.VMobject()
        self.scene = scene
        # draws the stack
        self.mstack.set_points_as_corners(
            [left_edge + height*m.UP, left_edge, left_edge + m.RIGHT, 
            (left_edge + m.RIGHT) + height*m.UP])
        self.mstack.set_stroke(width=2, color = m.GRAY)


    def pop(self, msg, tok_cols = None, ti = -1, vertex=None, anim=[], 
    token = None, matching=False):
        """Pops an element from the top of the stack.

        Args:
            msg (str): Accompanying message.
            tok_cols (list, optional): List of token colours. Defaults to None.
            ti (int, optional): Terminal index. Defaults to -1.
            vertex (Dot, optional): Graph vertex. Defaults to None.
            anim (list, optional): List of animations. Defaults to [].
            token (str, optional): Token. Defaults to None.
            matching (bool, optional): If the token matched a terminal. 
            Defaults to False.
        """    
        # sets up stack in backend
        if self.stack == []:
            return
        else:
            self.stack.pop()

            m_msg = m.MathTex(msg, color = config.get_opp_col()).next_to(self.mstack, m.DOWN)
            m_msg.scale_to_fit_width(3*self.mstack.width)

            if self.texts != []:
                # animate fading out
                top_text = self.texts[-1]

                # replace a non-terminal in the stack with its productions
                if not matching:
                    self.scene.play(
                        m.Write(m_msg),
                        m.Indicate(top_text, color=m.BLUE_D),
                    )
                    for a in anim:
                        self.scene.play(
                            a
                        )

                    sounds.add_sound_to_scene(self.scene, sounds.POP)
                    self.scene.play(m.FadeOut(top_text))

                else:
                    # match a terminal in the stack
                    self.scene.play(
                        m.FadeIn(m_msg),
                        m.FadeToColor(top_text, tok_cols[ti]),
                    )

                    sounds.add_sound_to_scene(self.scene, sounds.TWINKLE)
                    self.scene.play(
                        m.Flash(top_text, line_length=0.3,
                              num_lines=30, color=tok_cols[ti],
                              flash_radius=0.3,
                              time_width=0.3),
                        m.Flash(vertex, line_length=0.4,
                              num_lines=30, color=tok_cols[ti],
                              flash_radius=0.3,
                              time_width=0.3),
                        m.Flash(token, line_length=0.2,
                            num_lines=20, color=tok_cols[ti],
                            flash_radius=0.3,
                            time_width=0.3),
                        m.FadeOut(top_text))

                self.scene.play(m.FadeOut(m_msg))
                self.texts.pop()

    def write_under_stack(self, msg, fade_out=True):
        """Writes a message underneath the Stack. 

        Args:
            msg (str): Message to be written.
            fade_out (bool, optional): Whether to fade out the message. 
            Defaults to True.
        """        
        # set up message
        m_msg = m.MathTex(msg, color = config.get_opp_col()).next_to(self.mstack, m.DOWN)\
            .scale_to_fit_width(3*self.mstack.width)
        self.scene.play(
            m.Write(m_msg),
        )
        if fade_out:
            self.scene.play(
                m.FadeOut(m_msg),
            )

    def push(self, a, msg=None, anim=[]):
        """Pushes an element onto the stack.

        Args:
            a (str): Element to be pushed.
            msg (str, optional): Accompanying message. Defaults to None.
            anim (list, optional): List of animations. Defaults to [].
        """        
        # set up message
        if msg != None:
            m_msg = m.Tex(msg, color = config.get_opp_col())\
                .next_to(self.mstack, m.DOWN)
            m_msg.scale_to_fit_width(3*self.mstack.width)


        # add to backend stack
        self.stack.append(a)

        # create base of the stack
        if self.texts == []:
            t = m.MathTex(a, color = config.get_opp_col())\
                .move_to(self.mstack.get_center())\
                    .shift((3*self.mstack_height/2)/4 * m.DOWN)
            t.scale(0.6)
            self.texts.append(t)

        else:
            # align above last element
            t = m.MathTex(a).shift(self.le).fade_to(color=m.RED, alpha=1)
            if re.match(RE_TERMINAL, a):
                t.fade_to(color=m.TEAL, alpha=1)
            t.scale(0.6)
            t.move_to(self.texts[-1].get_top()).shift(m.UP*0.5)
            self.texts.append(t)
        
        if msg != None:
            sounds.add_sound_to_scene(self.scene, sounds.CLANG)
            self.scene.play(
                    m.FadeIn(t, shift=m.DOWN),
                    m.Write(m_msg)
            )

            self.scene.play(
                m.FadeToColor(t, color=config.get_opp_col()),
                m.FadeOut(m_msg),
            )
        else:
            if anim != None:
                sounds.add_sound_to_scene(self.scene, sounds.CLANG)
                self.scene.play(
                    m.FadeIn(t, shift=m.DOWN),
                    *[a for a in anim]
                )
            else:
                self.scene.play(
                    m.FadeIn(t, shift=m.DOWN),
                )

            self.scene.play(
                m.FadeToColor(t, color=config.get_opp_col()),
            )
