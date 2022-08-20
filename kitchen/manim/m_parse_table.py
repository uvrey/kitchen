""" Generates a visualisation of the parse table calculation. """
# kitchen/manim/m_parse_table.py

import manim as m

from kitchen import (
        CFG_SCALE_HEIGHT, 
        CFG_SCALE_WIDTH, 
        ERROR, 
        GRID_ITEM_SCALE,
        SUCCESS
)

from kitchen.helpers import config, error, sounds
from kitchen.backend import context_free_grammar as cfg
from kitchen.manim import m_general as mg

class MParseTable(m.Scene):
    def setup_manim(self, cfg: cfg.ContextFreeGrammar):
        """Sets up the structures which the animation will make use of.

        Args:
            cfg (ContextFreeGrammar): Loaded CFG.
        """        
        self.ts = sorted(cfg.terminals)
        self.nts = sorted(cfg.nonterminals)
        self.cfg = cfg

    def construct(self):
        """Creates a scene to visualise the parsing table construction.
        """        
        self._vis_populate_table()

    def _init_pt_dict(self):
        """Set up parsing table structure.
        """
        for n in self.nts:
            for t in self.ts:
                self.pt_dict[n] = {}
                self.pt_dict[n][t] = "Error"

    def _init_row_contents(self):
        """Initialises the row values in the parse table.

        Returns:
            List: List of lists, where these contain the row contents of the parse table.
        """        
        row_vals = []
        for n in self.nts:
            row = []
            for t in self.ts:
                row.append(".")
            row_vals.append(row)
        return row_vals

    def _init_m_table(self, row_vals: list, row_labels: list, col_labels: list):
        """Initialises the Manim MathTable structure.

        Args:
            row_vals (list): Row values.
            row_labels (list): Row labels.
            col_labels (list): Column labels.

        Returns:
            MathTable: Initialised Manim MathTable structure.
        """        
        row_labels = row_labels
        col_labels = col_labels

        table = m.MathTable(
            row_vals,
            row_labels=[m.MathTex(mg.to_math_tex(rl)) for rl in row_labels],
            col_labels=[m.MathTex(mg.to_math_tex(cl)) for cl in col_labels],
            include_outer_lines=True)

        lab = table.get_labels()
        lab.set_color(m.LIGHT_GRAY)
        table.get_horizontal_lines()[2].set_stroke(width=3, color=m.LIGHT_GRAY)
        table.get_vertical_lines()[2].set_stroke(width=3, color=m.LIGHT_GRAY)
        return table

    def _vis_populate_table(self):
        """Visualises the algorithm that constructs the parsing table.

        Args:
            scene (Scene): Manim parse table object, which extends a Manim Scene.
        """
        self.pt_dict = {}
        self._init_pt_dict()

        all_elements = m.VGroup()

        # sets up the title
        ll1_title = mg.get_title_mobject("LL(1) parsing: parse table")
        sounds.narrate("Let's find the parse table for this grammar.", self)
        keys = mg.get_manim_cfg_group(self)
        keys.scale_to_fit_height(CFG_SCALE_HEIGHT/3)
        all_elements.add(keys)

        # shows key for colour coding
        cfg_heading = m.Tex("Context-Free Grammar", tex_template = m.TexFontTemplates.french_cursive).next_to(keys, m.UP).align_to(keys.get_center)
        cfg_heading.scale(0.6)

        # draws establishing table animations
        row_labels = self.nts
        col_labels = mg.ts_m_epsilon(self)

        # builds up the row values
        row_vals = self._init_row_contents()

        # adds the table to the element group
        self.mtable = self._init_m_table(
            row_vals, row_labels, col_labels)
        self.mtable.get_row_labels().fade_to(color=m.RED, alpha=1)
        self.mtable.get_col_labels().fade_to(color=m.TEAL, alpha=1)
        self.mtable.scale_to_fit_height(CFG_SCALE_HEIGHT)
        all_elements.add(self.mtable)

        # adds the guide 
        guide = mg.get_guide(arr_right= True)
        guide.scale(0.6)
        
        # arranges all items
        all_elements.arrange_in_grid(rows = 1, buff = 1.2)
        all_elements.center()

        # scales everything nicely
        all_elements.scale_to_fit_width(CFG_SCALE_WIDTH)

        # makes sure elements are showing
        if all_elements.height > CFG_SCALE_HEIGHT or len(self.ts) > 4:
            all_elements.scale_to_fit_height(CFG_SCALE_HEIGHT)

        # adds cfg's heading
        cfg_heading.next_to(keys, m.UP)

        sounds.add_sound_to_scene(self, sounds.MOVE)

        self.play(
            ll1_title.animate.to_edge(m.UP),
            guide.animate.to_edge(m.DOWN),
            m.FadeIn(cfg_heading),
            m.LaggedStart(*(m.FadeIn(k, shift=m.UP)
                        for k in keys)),
        )

        sounds.add_sound_to_scene(self, sounds.TYPE)

        self.play(
           m.Write((self.mtable).get_labels()),
            run_time=1
        )
        
        # fades in table lines
        self.play(
            m.Create((self.mtable).get_horizontal_lines()[2]),
            m.Create((self.mtable).get_vertical_lines()[2]),
            run_time=2
        )

        # populates the whole table with the first and follow set, if appropriate
        for key in self.cfg.first_set.keys():
            # resets all lines to gray
            keys.fade_to(m.GRAY, 1)

            # highlights the CFG line
            cfg_line = self.manim_production_groups[key][:]
            self.play(
                    m.FadeToColor(cfg_line, color=config.opp_col())
            )

            for j, item in enumerate(self.cfg.first_set[key], start=0):

                # handles case where a first set contains an epsilon
                if item == "#":

                    for f in self.cfg.follow_set[key]:
                        # adds production to table if # in First(A) and $ in Follow(A)
                        prod = key + " -> " + item

                        if f == "$":
                            code = self.vis_add_to_parsetable(key, "$", prod)
                        else:
                            code = self.vis_add_to_parsetable(key, f, prod)
                        
                        # narrates events
                        mg.display_msg(self, ["Following " + prod + "adds #", " to First(" + mg.to_tex(key) + ")"], raw_msg = "If we follow "+key+"'s production, we find an epsilon. So, we add this production to the parse table.")
                        self.wait()

                        if code == ERROR:
                            sounds.add_sound_to_scene(self, sounds.FAIL)
                            return
                else:
                    # adds item to the parse table
                    prod = self.cfg.firstset_index[key][j]
                    mg.display_msg(self, ["Following " + prod + " adds " +
                                 self.cfg.first_set[key][j], " to First(" + key + ")"], raw_msg = "If we follow " + key + "'s production, we encounter terminal " + self.cfg.first_set[key][j] + ". So, let's add this production to the parse table at row " + key + " and column " + self.cfg.first_set[key][j])
                    
                    code = self.vis_add_to_parsetable(
                         key, item, prod)
                    if code == ERROR:
                        sounds.add_sound_to_scene(self, sounds.FAIL)
                        return
        
        self.wait()
        self.wait()
        sounds.add_sound_to_scene(self, sounds.YAY)
        sounds.narrate("The parse table is complete. Yay!", self)
        return SUCCESS

    def vis_add_to_parsetable(self, nt: str, t: str, prod: str):
        """Adds a new entry to the parse table visualisation.

        Args:
            nt (str): Non-terminal (row).
            t (str): Terminal (column).
            prod (str): Production to be added.

        Returns:
            int: Status code. 
        """        
        try:
            if self.pt_dict[nt][t] != "Error":
                mg.display_msg(self, ["Cannot add entry: There is already a production", "at ParseTable[" + nt +", " + t +"].", "NOTE: This grammar cannot be parsed with LL(1)." ], raw_msg = "There's already an entry, so this grammar is unsuitable for LL(1) parsing.")
                error.ERR_too_many_productions_ll1(nt, t)
                return ERROR
            else:
                self.pt_dict[nt][t] = prod
                self.swap(mg.row(self.nts, nt), mg.col(self.ts, t), prod)

        except KeyError:
            self.pt_dict[nt][t] = prod
            self.swap(mg.row(self.nts, nt), mg.col(self.ts, t), prod)
        return SUCCESS

    def swap(self, row: int, col: int, new_val: str) -> m.MathTable:
        """Swaps two elements in a parse table visualisation.

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
        t_new = m.MathTex(mg.to_math_tex(new_val))
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

        # pause before concluding
        self.wait()

    def tear_down(self):
        """Concludes the scene by clearing the narrations directory.
        """        
        mg.clear_narrs()