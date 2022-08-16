""" General parser generator for Kitchen """
# kitchen/parser.py
import typer
import anytree
import re

from kitchen import (
    RE_NONTERMINAL, ERROR, RE_PRODUCTION, RE_TERMINAL, display_helper, error, SUCCESS, PARSING_ERROR)

def init_input(self, inp) -> int:
    """Helper function to (re-)initialise the input of a Parser.
    Args:
        inp (_type_): _description_
    Returns:
        _type_: _description_
    """    
    if len(inp) < 1:
        error.ERR_no_input_given()
        return ERROR
    else:
        self.inp = inp
        self.tokens = _get_tokens_from_input(inp)
    return SUCCESS

def _get_tokens_from_input(inp) -> list:
    """Obtains the token stream of an input string. 
    Args:
        inp (str): Input string
    Returns:
        list: Token stream
    """    
    return list(filter(None, inp.split(" ")))


class ParserLL1:
    def __init__(self, inp, cfg):
        init_input(self, inp)
        self.cfg = cfg
        self.pt_dict = cfg.parsetable.pt_dict

    def check_for_epsilons(self):
        # look for any epsilons that came before and add. 
        for node in self.root.descendants:
            if re.match(RE_NONTERMINAL, node.id):
                if len(node.children) == 0 and "#" in self.cfg.first_set[node.id]:
                    anytree.Node("#", parent=node, id= "#")
        return SUCCESS

    def parse_ll1(self, start_symbol, inp="") -> int:
        """LL(1) Parser, which generates a parse tree and stores this to self.root
        Args:
            input (str): Input string to be parsed
            tokens (list): Corresponding token stream
        Returns:
            int: Status code
        """      
        # if new input is supplied to an existing LL(1) parser object
        if inp == "":
            inp = self.inp
        else:
            init_input(self, inp)

        # set up structures
        tokens = self.tokens[:]
        original_tokens = self.tokens[:]
        self.stack = []

        # add start symbol to the stack
        self.stack.append(start_symbol)
        self.root = anytree.Node(start_symbol, id=start_symbol)
        self.parents = []

        while self.stack != []:
            # in case we run out of input before the stack is empty
            if tokens == []:
                if re.match(RE_TERMINAL, self.stack[-1]):
                    error.ERR_parsing_error(self.root, "Expected " + self.stack[-1])
                else:
                    error.ERR_parsing_error(self.root)
                return PARSING_ERROR

            top = self.stack[-1]
            next = tokens[0]

            display_helper.print_parsetree(self.root)

            if re.match(RE_TERMINAL, top) or top == "$":
                if top == next:
                    tokens.remove(next)
                    p = self.stack.pop()

                    # ALL NEW TODO
                    # pops appropriately
                    if self.parents != []:
                        popped = self.parents.pop()

                        # reversed so we find the first match
                        index = len(self.parents) - 1

                        # linking new terminals to the tree
                        for node in reversed(self.parents):
                            if node.id == popped.tmp_p:
                                new_node = anytree.Node(popped.id, parent=node, id=popped.id)
                                break
                            index = index - 1

                        # pop off as many as needed
                        for j in range(index - 1):
                            self.parents.pop()

                    else:
                        display_helper.fail_secho("TODO!")

                    # if we have matched our last token
                    if len(tokens) == 1:
                        self.check_for_epsilons()
                    
                else:
                    error.ERR_parsing_error(self.root,
                        "Unexpected token [" + top + "]")
                    return PARSING_ERROR

            elif re.match(RE_NONTERMINAL, top):
                try:
                    typer.echo("looking for entry at " + top + ", " + next)

                    display_helper.pretty_print_dict(self.pt_dict)
                    pt_entry = self.pt_dict[top][next]
                    typer.echo(pt_entry)
                    if pt_entry == None:
                        typer.echo("NOPE")
                        return
                    prods = pt_entry.split("->")
                    pt = self.stack.pop()

                    typer.echo("Adding to productions of " + prods[0].strip())

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))
                    nodes_to_append = []

                    # this is the direction we push to the stack
                    for p in reversed(ps):
                        # add to the tree
                        if top == start_symbol:
                            # typer.echo("linking " + p + " and " + self.root.id)
                            new_node = anytree.Node(p, parent=self.root, id=p, tmp_p = self.root.id, connected=True)
                        else:
                            # add connecting node if it is a non-terminal
                            
                            if re.match(RE_NONTERMINAL, p):
                                # typer.echo("** linking " + p + " to parent " + self.parents[-1].id)
                                new_node = anytree.Node(
                                    p, id=p, parent=self.parents[-1], tmp_p=prods[0].strip(),  connected=True)
                            else:
                                if p != "#":
                                    new_node = anytree.Node(
                                        p, id=p,  tmp_p=prods[0].strip(), connected=False)
                                    
                        # we don't need to match epsilon, and we also only want non-terminals as parent nodes
                        if p != "#":
                            self.stack.append(p)
                            nodes_to_append.append(new_node)

                    # TODO NEW! only append parents once whole list has been processed
                    for t in nodes_to_append:
                        self.parents.append(t)

                except KeyError:
                    error.ERR_parsing_error(self.root,
                        "ParseTable[" + top + ", " + next + "] is empty.")
                    return PARSING_ERROR

        # in case parsing finishes but there are still tokens left in the stack
        if len(tokens) > 0:
            error.ERR_parsing_error(self.root, "Unexpected end of input.")
            return PARSING_ERROR

        # display the parse tree
        # TODO change to parsing input specifically rather than tokens
        display_helper.success_secho("Successfully parsed token stream '" + " ".join(original_tokens) +
                              "'!\nParse tree:")
        display_helper.print_parsetree(self.root)
        return SUCCESS

    def get_node(self, node_id):
        for node in self.root.children:
            if node_id == self.root:
                return node
        return None
    