""" General parser generator for Kitchen """
# kitchen/parser.py

from kitchen import error
import typer
import anytree

def init_parse_ll1(self, inp):
    if len(inp) < 1:
        error.ERR_no_input_given()
    else:
        _parse_ll1(inp, list(filter(None, inp.split(" "))))

def _parse_ll1(input, tokens):
    pass



class Parser:
    def __init__(self):
        pass


class ParserLL1:
    def __init__(self):
        pass

    def show_parse_table(self):
        self.parsetable.print_parse_table()

    def show_parse_structures(self):
        self.parsetable.show_structures()


            # helper function to print the parse tree

    def print_pt(self, root):
        """Helper function to print the parse tree

        Args:
            root (_type_): _description_
        """        
        for pre, fill, node in RenderTree(root):
            typer.echo("%s%s" % (pre, node.name))



    