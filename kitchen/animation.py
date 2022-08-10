""" Creates Kitchen animations """
# kitchen/animation.py

class Animation:
    def __init__(self):
        pass

class ManimFirstSet:
    pass

class ManimFollowSet:
    pass

class ManimParsingTable:
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
            FadeOut(t_old),
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

class ManimParseTree:
    pass