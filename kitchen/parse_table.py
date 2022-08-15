import typer
import manim as m
import re
from kitchen import (
    RE_TERMINAL,
    display_helper,
    error
)

class ParsingTable:
    def __init__(self, terminals, nonterminals, cfgd):
        """Initialises a ParsingTable object.

        Args:
            terminals (List): List of terminals. 
            nonterminals (List): List of non-terminals. 
            cfgd (Dictionary): Dictionary containing non-terminals and their productions. 
        """        
        self.first_set = {}
        self.follow_set = {}
        self.ts = sorted(terminals)
        self.nts = sorted(nonterminals)
        self.cfg_dict = cfgd
        self.pt_dict = {}
        self.init_parsetable()
        self.calculated = False

        """ initialises the parsing table """
    def show_structures(self) -> None:
        """Displays the structures involved in forming the parse table. 
        """        
        display_helper.info_secho("First set:")
        display_helper.pretty_print_dict(self.first_set)
        display_helper.info_sechotyper.echo("Follow set")
        display_helper.pretty_print_dict(self.follow_set)
        display_helper.info_sechotyper.echo("Terminals")
        display_helper.pretty_print_dictpprint.pprint(self.ts)
        display_helper.info_sechotyper.echo("Non terminals")
        display_helper.pretty_print_dictpprint.pprint(self.nts)

    def set_internals(self, fs, fw, fs_index):
        """Sets up the internal components of the parsing table. 

        Args:
            fs (Dictionary): First set
            fw (Dictionary): Follow set
            fs_index (Dictionary): First set indices.
        """        
        self.firstset_index = fs_index
        self.first_set = fs
        self.follow_set = fw


    def init_parsetable(self):
        """ Initialises the parsing table. 
        """        
        for n in self.nts:
            for t in self.ts:
                self.pt_dict[n] = {}
                self.pt_dict[n][t] = None

    def row(self, nt):
        """Obtain the row index of a given non-terminal.

        Args:
            nt (String): Non-terminal

        Returns:
            int: Row index
        """        
        return self.nts.index(nt) + 1

    def col(self, t):
        """Obtain the column index of a terminal.

        Args:
            t (String): Terminal

        Returns:
            int: Column index
        """        
        return self.ts.index(t) + 1

    # 
    def init_ll1_parsetable(self):
        """Sets up the parse table structure without generating an animation_summary_
        """        
        # draw establishing table animations
        row_labels = self.nts
        col_labels = self.ts_m_epsilon()

        # gets the row values
        row_vals = self.get_row_contents()

    # TODO convert this to ManimParsingTable
        self.mtable = self.init_m_table(
            row_vals, row_labels, col_labels)

        self.mtable.get_row_labels().fade_to(color=m.RED, alpha=1)
        self.mtable.get_col_labels().fade_to(color=m.TEAL, alpha=1)



    def populate_table(self):
        """Populates the whole table with the first and follow set, if appropriate
        """
        for i, key in enumerate(self.first_set.keys(), start=0):
            for j, item in enumerate(self.first_set[key], start=0):
                # if the first set contains epsilon, may disappear
                if item == "#":
                    for f in self.follow_set[key]:
                        if f == "$":
                            prod = key + " -> $"
                        else:
                            prod = key + " -> #"
                        self.add_to_parsetable(key, f, prod)
                else:
                    # add item to the parse table
                    prod = self.firstset_index[key][j]
                    self.add_to_parsetable(key, item, prod)

    def add_to_parsetable(self, nt, t, production):
        """Adds a production to the parsetable at a given index. 

        Args:
            nt (String): Non-terminal
            t (String): Terminal
            production (String): Production at ParseTable[nt, t]
        """
        try:
            if self.pt_dict[nt][t] != None:
                error.ERR_too_many_productions_ll1(nt, t)
            else:
                self.pt_dict[nt][t] = production

        except KeyError:
            self.pt_dict[nt][t] = production

    def init_manim_parsetable(self):
        self.m_parsetable = ParsingTable()
        rows = sorted(self.nts)
        cols = sorted(self.ts)
        self.m_parsetable.init_table([], [], rows, cols)

    def get_row_contents(self):
        """Gets the rows as a list of lists. 

        Returns:
            List: Row contents lists.
        """        
        row_vals = []
        for n in self.nts:
            row = []
            for t in self.ts:
                try:
                    item = self.pt_dict[n][t]
                    typer.echo(item)
                    if item != None:
                        if re.match(RE_TERMINAL, item):
                            row.append(item)
                        else:
                            tmp = item.replace(
                                "->", "\\to").strip().replace("#", "\epsilon")
                            row.append(tmp)
                    else:
                        row.append("")
                except KeyError:
                    row.append("")
            row_vals.append(row)
        return row_vals

    def init_row_contents(self):
        """Initialises the row contents (MANIM)

        Returns:
            List: Row values.
        """        
        row_vals = []
        for n in self.nts:
            row = []
            for t in self.ts:
                row.append(".")
            row_vals.append(row)
        return row_vals

    def ts_m_epsilon(self):
        """Replaces an epsilon terminal with its LaTeX equivalent.

        Returns:
            str: Epsilon
        """        
        ts_m = []
        for t in self.ts:
            if t == "#":
                ts_m.append("\epsilon")
            else:
                ts_m.append(t)
        return ts_m


    def dbg_ll1(self):
        typer.echo(self.stack)
        typer.echo(self.parents)
        typer.echo("------")
        self.print_pt(self.root)

    # helper function to print the parsing table

    def print_parse_table(self):
        """Prints the parse table.
        """        
        # print heading
        display_helper.info_secho("Parse Table:")

        # print column labels
        col_label = "\t"
        for t in self.ts:
            col_label += t + "\t"
        display_helper.structure_secho(col_label)

        # print rows and contents
        for nts in self.nts:
            row = nts + ":\t"
            for t in self.ts:
                if t in self.first_set[nts]:
                    term_index = self.first_set[nts].index(t)
                    row += re.sub(r'\s+', '',
                                  self.firstset_index[nts][term_index]) + "\t"
                else:
                    row += "\t"
            display_helper.structure_secho(row)

    def init_manim_parsetable(self):
        self.m_parsetable = ManimParsingTable()
        rows = sorted(self.nts)
        cols = sorted(self.ts)
        self.m_parsetable.init_table([], [], rows, cols)


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



