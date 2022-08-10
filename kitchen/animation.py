""" Creates Kitchen animations """
# kitchen/animation.py

from re import S
import manim as m

COLOURS = [m.BLUE_B, m.TEAL_B, m.GREEN_B, m.YELLOW_B, m.GOLD_B,
                     m.RED_B, m.MAROON_B, m.PURPLE_A, m.LIGHT_PINK, m.LIGHT_BROWN]
class Notify:
    scene = None
    def __init__(self, s):
        global scene
        scene = s

        # Helper function to put a message on the screen
    def notify(message, next_to_this):
        # returns a keys group, which is the cfg representation
        msg_text = m.Text(message, color=m.WHITE, weight=m.BOLD).scale(0.5).next_to(
            next_to_this, m.RIGHT)
        scene.play(
           m.Write(msg_text),
        )
        scene.wait()
        scene.play(
            m.FadeOut(msg_text)
        )

    def fullscreen_notify(message):
        err_msg = message
        err_m_msg = m.Text(err_msg, color=m.WHITE)
        rect = m.Rectangle(width=20, height=10, color=m.BLACK, fill_opacity=0.85)
        err_m_msg.move_to(rect.get_center())
        scene.play(
            m.FadeIn(rect),
        )
        scene.play(
            m.FadeIn(err_m_msg),
            run_time=0.5
        )
        scene.wait()

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

class Animation:
    def setup(self):
        self.frame_width = m.config["frame_width"]
        self.frame_height = m.config["frame_height"]

    def __init__(self, cfg):
        self.cfg = cfg

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

    class ManimFirstSet(m.Scene):
        def construct(self):
            keys = self.get_manim_cfg_group()
            self.play(
                m.FadeIn(m.Text("WOW")),
            )

    class ManimFollowSet():
        pass

    class ManimParsingTable():
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
            t_new = Tex(new_val)
            t_new.move_to(t_old)
            t_new.fade_to(TEAL, alpha=1)

            # fade out old value and into new value
            self.play(
                FadeIn(t_new),
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

            self.table = MathTable(
                [self.xs, self.ys],
                row_labels=[MathTex(rl) for rl in self.row_labels],
                col_labels=[MathTex(cl) for cl in self.col_labels],
                include_outer_lines=True)

            # Table
            lab = self.table.get_labels()
            lab.set_color(LIGHT_GRAY)
            self.table.get_horizontal_lines()[2].set_stroke(
                width=8, color=LIGHT_GRAY)
            self.table.get_vertical_lines()[2].set_stroke(
                width=8, color=LIGHT_GRAY)

    class ManimParseTree():
        pass