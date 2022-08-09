""" General parser generator for Kitchen """
# kitchen/parser.py

from kitchen import error

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



    