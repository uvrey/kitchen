""" General parser generator for Kitchen """
# kitchen/parser.py


import typer
import anytree
import re

from kitchen import (
    RE_NONTERMINAL, RE_PRODUCTION, RE_TERMINAL, display_helper, error, SUCCESS, PARSING_ERROR)

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


    def parse_ll1(self, input, tokens) -> int:
        """LL(1) Parser, which generates a parse tree and stores this to self.root

        Args:
            input (str): Input string to be parsed
            tokens (list): Corresponding token stream

        Returns:
            int: Status code
        """      

        original_tokens = tokens[:]
        self.stack = []

        # add start symbol to the stack
        start_symbol = list(self.cfg_dict.keys())[0]
        self.stack.append(start_symbol)
        self.root = Node(start_symbol, id=start_symbol)
        self.parents = []

        while self.stack != []:
            # in case we run out of input before the stack is empty
            if tokens == []:
                if re.match(RE_TERMINAL, self.stack[-1]):
                    error.ERR_parsing_error("Expected " + self.stack[-1])
                else:
                    error.ERR_parsing_error()
                return PARSING_ERROR

            top = self.stack[-1]
            next = tokens[0]

            if re.match(RE_TERMINAL, top) or top == "$":
                if top == next:
                    tokens.remove(next)
                    self.stack.pop()

                    # pops appropriately
                    if self.parents != []:
                        popped = self.parents.pop()
                        typer.echo(self.parents)

                        # always pop again if an epsilon was encountered
                        if self.parents != []:
                            done = False

                            i = 1
                            while not done:
                                p = self.parents[-i]
                                if re.match(RE_NONTERMINAL, p.id):
                                    # if we have encountered the first set which the production can fall under
                                    if popped.id in self.firstset[p.id]:
                                        # remove children if they were previously added
                                        if p.height != 0:
                                            p.children = []
                                        new_node = Node(
                                            popped.id, parent=p, id=popped.id)
                                     
                                        # check for epsilons
                                        rhs = self.parents[-i + 1:]
                                        for r in rhs:
                                            # check that production can actually lead somewhere and is not current prod
                                            # AND that it hasn't been explored yet
                                            if re.match(RE_NONTERMINAL, r.id) and r.id != p.id and r.height == 0:
                                                if "#" in self.firstset[r.id]:
                                                    new_node = Node(
                                                        "#", parent=r, id="eps")

                                        # pop as many productions off as necessary
                                        for j in range(i - 1):
                                            self.parents.pop()
                                        done = True
                                    else:
                                        i = i + 1
                                else:
                                    break

                else:
                    error.ERR_parsing_error(
                        "Unexpected token [" + top + "]")
                    return PARSING_ERROR

            elif re.match(RE_NONTERMINAL, top):
                try:
                    pt_entry = self.parsetable[top][next]
                    prods = pt_entry.split("->")
                    p = self.stack.pop()

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))

                    for p in reversed(ps):
                        # add to the tree
                        if top == start_symbol:
                            new_node = Node(p, parent=self.root, id=p)
                        else:
                            # add connecting node if it is a non-terminal
                            if re.match(RE_NONTERMINAL, p):
                                new_node = Node(
                                    p, id=p, parent=self.parents[-1])
                            else:
                                if p != "#":
                                    new_node = Node(
                                        p, id=p)

                        # we don't need to match epsilon, and we also only want non-terminals as parent nodes
                        if p != "#":
                            self.stack.append(p)
                            self.parents.append(new_node)

                except KeyError:
                    error.ERR_parsing_error(
                        "ParseTable[" + next + ", " + top + "] is empty.")
                    return PARSING_ERROR

        # in case parsing finishes but there are still tokens left in the stack
        if len(tokens) > 0:
            error.ERR_parsing_error()
            return PARSING_ERROR

        # display the parse tree
        # TODO change to parsing input specifically rather than tokens
        display_helper.success_secho("Successfully parsed token stream'" + " ".join(original_tokens) +
                              "'!")
        return SUCCESS



    