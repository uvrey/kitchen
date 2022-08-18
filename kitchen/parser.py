""" General parser generator for Kitchen """
# kitchen/parser.py
from tracemalloc import start
import typer
import anytree
import re

from kitchen import (
    RE_NONTERMINAL, ERROR, RE_PRODUCTION, RE_TERMINAL, display_helper, error, SUCCESS, PARSING_ERROR, lang_spec)

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
        display_helper.info_secho("Note:\tNo language specification has been provided, so the given \n\tinput will be interpreted as tokens directly.")
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
                    anytree.Node("#", parent=node, id= "#")
        return SUCCESS

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

        if None in self.tokens:
            display_helper.fail_secho("Not all tokens from the input stream were matched :(\nParsing failed.")
            return

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
                if not semantic:
                    if re.match(RE_TERMINAL, self.stack[-1]):
                        error.ERR_parsing_error(self.root, "Expected " + self.stack[-1])
                    else:
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
                    typer.echo("MATCHED " + next)

                    # ALL NEW TODO
                    # pops appropriately
                    if self.parents != []:
                        popped = self.parents.pop()

                        # set up leading connections
                        # for index, node in enumerate(self.parents, start = 0):
                        #     if node == popped.token:
                        #         needs_connecting = self.parents[index + 1:]
                        #         break

                        # set up the terminal node
                        popped.parent = popped.token
                        # connect all nodes that lead to the token
                        # for nd in reversed(needs_connecting):
                        #     nd.parent = nd.token

                        # display_helper.print_parsetree(self.root)
                        # return

                        # typer.echo(needs_connecting)
                        # display_helper.structure_secho(self.parents)

                        # reversed so we find the first match
                    #     parent_count = 0
                    #     node_found = False
                    #     temp_parent = popped.tmp_p

                    #     # create node
                    #   #  display_helper.info_secho(popped.id + " has parent " + popped.token.id)
                    #     new_node = anytree.Node(popped.id, parent=popped.token, id=popped.id, token = popped.token)
                        
                    #     #linking new terminals to the tree
                    #     for node in reversed(self.parents):
                    #         if not node_found:
                    #             if (node.id == temp_parent):
                    #             #    display_helper.info_secho("appending " + popped.id + " with parent " + node.id)
                    #                # new_node = anytree.Node(popped.id, parent=node, id=popped.id, token = prev_token)
                    #                 node_found = True
                    #                 temp_parent = node.tmp_p
                    #         else:
                    #             if (node.id == temp_parent):
                    #                 parent_count = parent_count + 1
                    #                 temp_parent = node.tmp_p

                    #         # count how many to pop off based on node being found
                    #     #     parent_position = parent_position - 1
                    #    # typer.echo(popped.id + " has " + str(parent_count) + " parents. we pop them all off")

                    #     # pop all the direct parents of and including the node we just encountered
                    #     typer.echo("popping " + str(parent_count - 1) + " OFF!!")
                    #     if parent_count > 0:
                    #         for i in range(parent_count - 1):
                    #             p = self.parents.pop()
                    #             p.parent = p.token
                    #             typer.echo("LAST PARENT POPPED: " + str(p))

                    else:
                        display_helper.fail_secho("TODO!")

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
                  #  display_helper.success_secho("trying to find entry at " + str(top) + ", " + str(next))
                    pt_entry = self.pt_dict[top][next]
                    prods = pt_entry.split("->")
                  
                    pt = self.stack.pop()
                    display_helper.fail_secho("finding productions of " + prods[0])

                    if top != start_symbol:
                        # append new non-terminal path to the tree
                        to_be_appended = self.parents[-1]
                        if to_be_appended.parent == None:
                            to_be_appended.parent = to_be_appended.token

                    # add sequence of productions to the stack
                    ps = list(filter(None, re.findall(
                        RE_PRODUCTION, prods[1])))
                    typer.echo(ps)
                    nodes_to_append = []

                    # this is the direction we push to the stack
                    for p in reversed(ps):
                        # add to the tree
                        if top == start_symbol:
                            new_node = anytree.Node(p, parent=self.root, id=p, tmp_p = self.root.id, token = self.root)
                        else:
                            # add connecting node if it is a non-terminal
                            new_node = anytree.Node(
                                p, id=p, parent = None, tmp_p=prods[0].strip(), token = self.parents[-1])
                                    
                        # we don't need to match epsilon, and we also only want non-terminals as parent nodes
                        if p != "#":
                            self.stack.append(p)
                            nodes_to_append.append(new_node)

                    # pop off parents
                    if self.parents != []:
                        self.parents.pop()
                    
                    # add children
                    for t in nodes_to_append:
                        self.parents.append(t)

                    if top != start_symbol:
                        if self.parents != []:
                            for i, p in enumerate(self.parents, start=1):
                                typer.echo(i)
                                display_helper.structure_secho(p)
                     

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
        if not semantic:
            if not testing:
                display_helper.success_secho("\nSuccessfully parsed token stream '" + lang_spec.get_token_types(original_tokens) +
                                    "'\nfrom input stream '" + lang_spec.get_token_values(original_tokens) + "'.\n\nParse tree:")
                display_helper.print_parsetree(self.root)
            else:
                display_helper.success_secho("Success.")
                display_helper.structure_secho(anytree.RenderTree(self.root, style= anytree.AsciiStyle()).by_attr("id"))
        return SUCCESS

    def get_node(self, node_id):
        for node in self.root.children:
            if node_id == self.root:
                return node
        return None

