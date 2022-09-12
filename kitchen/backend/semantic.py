""" Generates semantic analysis. """
# kitchen/backend/semantic.py

import anytree
import pandas as pd

from kitchen.helpers import display

from kitchen import COLOURS_LIGHT, COLOURS_DARK

class SemanticAnalyser:
    def __init__(self, cfg, root, inp):
        """Initialises the SemanticAnalyser.

        Args:
            cfg (ContextFreeGrammar): Loaded CFG.
            root (Node): Root of parse tree.
            inp (str): Input to be analysed.
        """        
        self.cfg = cfg
        self.root = root
        self.input = inp
        self.symbol = {'Symbol': [], 'Type': []}

    def _call_error(self, msg = ""):
        """Display an error in the type-checking process.

        Args:
            msg (str, optional): Details. Defaults to "".
        """        
        display.fail_secho("Type Error: "+ msg)
        self.print_symbol_table()
        return 

    def init_analysis(self):
        """Analyses a given input based on two basic semantic rules:
           Variable uniqueness and mutability.
        """        
        lhs = True
        lh_type = None
        for node in anytree.PreOrderIter(self.root):
            display.info_secho(node.id)
            if node.token != None:
                try:
                    if not lhs:
                        if node.token.value not in self.symbol['Symbol'] \
                            and lh_type == node.token.type:
                            self._call_error(node.token.value + 
                            " has not yet been defined.")
                            return
                        lhs = True
                    else:
                        if node.token.value != "=":
                            if node.token.value in self.symbol['Symbol']:
                                self._call_error(node.token.value + 
                                " has already been defined.")
                                return
                            else:
                                lh_type = node.token.type
                        else:
                            lhs = False
                    
                    self.symbol['Symbol'].append(node.token.value)
                    self.symbol['Type'].append(node.token.type)

                except:
                    self._call_error("Cannot semantically analyse only "+
                        "a token stream.")
                    return
        self.print_symbol_table()

    def print_symbol_table(self):
        """Displays the symbol table.
        """        
        display.info_secho("Symbol Table:")
        df = pd.DataFrame.from_dict(self.symbol).to_markdown()
        display.structure_secho(df)



