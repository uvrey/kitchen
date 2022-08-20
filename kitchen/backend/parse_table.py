
import typer
import manim as m
import re
import pandas as pd

from kitchen import (
    RE_TERMINAL,
)

from kitchen.helpers import (
    display,
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
        display.info_secho("First set:")
        display.pretty_print_dict(self.first_set)
        display.info_sechotyper.echo("Follow set")
        display.pretty_print_dict(self.follow_set)
        display.info_sechotyper.echo("Terminals")
        display.pretty_print_dictpprint.pprint(self.ts)
        display.info_sechotyper.echo("Non terminals")
        display.pretty_print_dictpprint.pprint(self.nts)

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
            self.pt_dict[n] = {}
            for t in self.ts:
                self.pt_dict[n][t] = "Error"

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

    def populate_table(self):
        """Populates the whole table with the first and follow set, if appropriate
        """

        for key in self.first_set.keys():
            for j, item in enumerate(self.first_set[key], start=0):
                # if the first set contains epsilon, it may disappear. So, we need to add elements in the follow set too.
                if item == "#":
                    for f in self.follow_set[key]:
                        prod = key + " -> " + item
                        if f == "$":
                            # make A->a in column of "$"
                            self.add_to_parsetable(key, "$", prod)
                        else:
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
            if self.pt_dict[nt][t] != "Error":
                error.ERR_too_many_productions_ll1(nt, t)
            else:
                self.pt_dict[nt][t] = production
        except KeyError:
            self.pt_dict[nt][t] = production

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
                    if item != None:
                        if re.match(RE_TERMINAL, item):
                            row.append(item)
                        else:
                            tmp = item.replace(
                                "->", "\\to").strip().replace("#", "\\varepsilon")
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
                ts_m.append("\\varepsilon")
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
        display.info_secho("Parse Table:")
        df = pd.DataFrame.from_dict(self.pt_dict).transpose().to_markdown()
        display.structure_secho(df)

    def print_parse_table_testing(self):
        """Prints the parse table for testing purposes
        """        
        # print heading
        typer.echo(self.pt_dict)






  