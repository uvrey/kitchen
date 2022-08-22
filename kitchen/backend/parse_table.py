""" Generates a visualisation of the parse table calculation. """
# kitchen/backend/parse_table.py

import manim as m
import pandas as pd
import re
import typer

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
            terminals (list): List of terminals. 
            nonterminals (list): List of non-terminals. 
            cfgd (dict): Dictionary containing non-terminals and their 
            productions. 
        """        
        self.first_set = {}
        self.follow_set = {}
        self.ts = sorted(terminals)
        self.nts = sorted(nonterminals)
        self.cfg_dict = cfgd
        self.pt_dict = {}
        self.init_parsetable()
        self.calculated = False

    def set_internals(self, fs, fw, fs_index):
        """Sets up the internal components of the parsing table. 

        Args:
            fs (Dictionary): First set.
            fw (Dictionary): Follow set.
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
        """Obtains the row index of a given non-terminal.

        Args:
            nt (String): Non-terminal

        Returns:
            int: Row index
        """        
        return self.nts.index(nt) + 1

    def col(self, t):
        """Obtains the column index of a terminal.

        Args:
            t (String): Terminal.

        Returns:
            int: Column index
        """        
        return self.ts.index(t) + 1

    def populate_table(self):
        """Populates the whole table with the first and follow set, if 
        appropriate
        """
        for key in self.first_set.keys():
            for j, item in enumerate(self.first_set[key], start=0):
                # if the first set contains epsilon, it may disappear. So, 
                # we need to add elements in the follow set too.
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
            nt (str): Non-terminal.
            t (str): Terminal.
            production (str): Production at ParseTable[nt, t].
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
            list: Row contents lists.
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
                            tmp = display.to_math_tex(item)
                            row.append(tmp)
                    else:
                        row.append("")
                except KeyError:
                    row.append("")
            row_vals.append(row)
        return row_vals

    def ts_m_epsilon(self):
        """Replaces an epsilon terminal with its LaTeX equivalent.

        Returns:
            str: Epsilon
        """        
        ts_m = []
        for t in self.ts:
            ts_m.append(display.to_math_tex(t))
        return ts_m

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






  