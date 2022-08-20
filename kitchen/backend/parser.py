""" General parser generator for Kitchen """
# kitchen/parser.py
from tracemalloc import start
import typer
import anytree
import re

from kitchen import (
    RE_NONTERMINAL, ERROR, RE_PRODUCTION, RE_TERMINAL, SUCCESS, PARSING_ERROR,)
from kitchen.helpers import (display, error, lang_spec)

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
        self.tokens = _get_tokens_from_input(inp, self.spec)
    return SUCCESS

# TODO read the spec file and match
def _get_tokens_from_input(inp, spec = None) -> list:
    """Obtains the token stream of an input string. 
    Args:
        inp (str): Input string
    Returns:
        list: Token stream
    """    
    if spec != None:
        tokens = spec.get_tokens_from_input(inp)
        return tokens
    else:
        return list(filter(None, inp.split(" ")))

class ParserLL1:
    def __init__(self, inp, cfg, spec = None):
        self.cfg = cfg
        self.pt_dict = cfg.parsetable.pt_dict
        self.spec = spec
        init_input(self, inp)

    def check_for_epsilons(self):
        # look for any epsilons that came before and add.
        for node in self.root.descendants:
            if re.match(RE_NONTERMINAL, node.id):
                if len(node.children) == 0 and "#" in self.cfg.first_set[node.id]:
                    anytree.Node("#", parent=node, id= "#", token = None)
        return SUCCESS

    def _parsing_successful(self, tokens, semantic: bool, testing = False, verbose = True):
        types = lang_spec.get_token_format(tokens, types=True)
        values = lang_spec.get_token_format(tokens, values=True)
        
        if not semantic:
            if testing:
                display.success_secho("Success.")
                display.structure_secho(anytree.RenderTree(self.root, style= anytree.AsciiStyle()).by_attr("id"))
                return

            if verbose:
                display.success_secho("\nSuccessfully parsed token stream '" + types +
                                            "'\nfrom input stream '" + values + "'.\n\nParse tree:")
                display.print_parsetree(self.root)

    def parse_ll1(self, start_symbol, inp="", semantic = False, testing = False) -> int:
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

        # display.info_secho("MAPPED TO TOKENS:")
        # display.show_tokens(self.tokens)

        if None in self.tokens:
            display.fail_secho("Not all tokens from the input stream were matched :(\nParsing failed.")
            return

        # set up structures
        tokens = self.tokens[:]
        original_tokens = self.tokens[:]
        self.stack = []

        # add start symbol to the stack
        self.stack.append(start_symbol)
        self.root = anytree.Node(start_symbol, id = start_symbol, token = None)
        self.parents = []

        while self.stack != []:
            # in case we run out of input before the stack is empty
            if tokens == []:
                if re.match(RE_TERMINAL, self.stack[-1]):
                    if not semantic:
                        error.ERR_parsing_error(self.root, "Expected " + self.stack[-1])
                else:
                    # parsing is successful if the remaining non-terminal may tend to epsilon
                    if "#" in self.cfg.first_set[self.stack[-1]] and len(self.stack) == 1:
                        self._parsing_successful(original_tokens, semantic, testing)
                        return SUCCESS
                    if not semantic:
                        error.ERR_parsing_error(self.root)
                return PARSING_ERROR

            top = self.stack[-1]
            try:
                next = tokens[0].type
            except:
                next = tokens[0]

            if re.match(RE_TERMINAL, top) or top == "$":
                if top == next:
                    prev_token = tokens[0]
                    tokens = tokens[1:]
                    p = self.stack.pop()

                    if self.parents != []:
                        popped = self.parents.pop()

                        # set up the terminal node
                        popped.parent = popped.tmp_parent
                        popped.token = prev_token
                    else:
                        display.fail_secho("TODO!")

                    # if we have matched our last token
                    if len(tokens) == 1:
                        self.check_for_epsilons()
                    
                else:
                    if not semantic:
                        error.ERR_parsing_error(self.root,
                            "Unexpected token [" + top + "]")
                    return PARSING_ERROR

            elif re.match(RE_NONTERMINAL, top):

                try:
                  #  display.success_secho("trying to find entry at " + str(top) + ", " + str(next))
                    pt_entry = self.pt_dict[top][next]
                    prods = pt_entry.split("->")
                  
                    self.stack.pop()
                    # display.fail_secho("finding productions of " + prods[0])

                    if top != start_symbol:
                        # append new non-terminal path to the tree
                        to_be_appended = self.parents[-1]
                        if to_be_appended.parent == None:
                            to_be_appended.parent = to_be_appended.tmp_parent

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))
                   
                    nodes_to_append = []
                    stack_to_append = []

                    # this is the direction we push to the stack
                    for p in ps:
                        # add to the tree
                        if top == start_symbol:
                            new_node = anytree.Node(p, parent=self.root, id=p, tmp_p = self.root.id, tmp_parent = self.root, token = None)
                        else:
                            # add connecting node if it is a non-terminal
                            new_node = anytree.Node(
                                p, id=p, parent = None, tmp_p=prods[0].strip(), tmp_parent = self.parents[-1], token = None)
                                    
                        # we don't need to match epsilon, and we also only want non-terminals as parent nodes
                        if p != "#":
                            stack_to_append.append(p)
                            nodes_to_append.append(new_node)

                    # pop off parents
                    if self.parents != []:
                        self.parents.pop()
                    
                    # add children
                    for n in reversed(nodes_to_append):
                        self.parents.append(n)
                    
                    for s in reversed(stack_to_append):
                        self.stack.append(s)

                except:
                    if not semantic:
                        error.ERR_parsing_error(self.root,
                            "ParseTable[" + top + ", " + next + "] is empty.")
                    return PARSING_ERROR

        # in case parsing finishes but there are still tokens left in the stack
        if len(tokens) > 0:
            if not semantic:
                error.ERR_parsing_error(self.root, "Unexpected end of input.")
            return PARSING_ERROR

        # display the parse tree
        self._parsing_successful(original_tokens, semantic, testing)               
        return SUCCESS

    def get_node(self, node_id):
        for node in self.root.children:
            if node_id == self.root:
                return node
        return None

