""" creates the context free grammar """
# kitchen/context_free_grammar.py

import configparser
from itertools import chain
from math import prod
from pathlib import Path
import re
from typing import Dict
import manim as m
import typer
import pprint
from kitchen import (
    CFG_ERROR_NT_FORMAT,
    CFG_FILE_ERROR,
    ERROR, 
    SUCCESS, RE_TERMINAL, 
    RE_NONTERMINAL, 
    RE_PRODUCTION,
    display_helper,
    error,
    parse_table as pt)

DEFAULT_CFG_PATH = Path.home().joinpath(
    "." + Path.home().stem + "cfg.txt"
)
DEFAULT_REGEX_PATH = Path.home().joinpath(
    "." + Path.home().stem + "regex.yaml"
)

def get_cfg_path(config_file: Path) -> Path:
    """Obtains the path to the currently-loaded CFG file.

    Returns:
        Path: Path to the CFG file.
    """    
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["cfg_path"])

def get_prods(cfg_contents) -> list:
    """Obtains a list of productions given the contents of a CFG.

    Args:
        cfg_contents (String): Contents of the CFG as obtained at the provided path.

    Returns:
        List: Productions in a given CFG.
    """    
    line = 0

    # store productions
    prods = []
    cfg_list = list(filter(None, cfg_contents.split("\n")))

    # store
    for production in cfg_list:
        tmp_prod = []
        pps = list(filter(None, production.split("->")))

        # check that non-terminal doesn't start productions
        # TODO handle this error properly
        if not re.match(RE_NONTERMINAL, pps[0]):
            display_helper.fail_secho("CFG Error at line " + str(line) + "-> " + pps[0])
            raise typer.Exit()
            return CFG_ERROR_NT_FORMAT

        tmp_prod.append(re.sub(r'[\s+]', '', pps[0]))

        # split into separate groups (eg. A | B)
        spaced_groups = list(filter(None, pps[1].split("|")))

        # remove all whitespace from the productions
        groups = []
        for g in spaced_groups:
            t = g.strip()
            groups.append(t)

        # append [A], [B] to production group
        tmp_prod.append(groups)
        prods.append(tmp_prod)
        line = line + 1
    return prods

def populate_manim_cfg(cfg_dict, lead_to) -> Dict:
    """_summary_Returns an equivalent cfg in manim where each non-terminal has an associated set of MObject

    Args:
        cfg_dict (Dictionary): Dictionary of the CFG productions.
        lead_to (Dictionary): Dictionary holding the Mobjects for each CFG element.

    Raises:
        typer.Abort: If Left Recursion is detected, the app session is terminated.

    Returns:
        Dictionary: A dictionary of the Mobjects which a non-terminal leads to.
    """    
    manim_cfg = {}
    try:
        for index, key in enumerate(cfg_dict.keys(), start=0):
            # append the text of the leading NT
            manim_cfg[key] = [m.Text(key, weight=m.BOLD)]

            # make a list of sub-productions which are led to by this NT
            tmp_item = []
            for i, item in enumerate(lead_to[index], start=0):
                split_item = list(filter(None, re.findall(
                    RE_PRODUCTION, item)))
                tmp_split_list = []
                for j, specific in enumerate(split_item, start=0):
                    # gets manim equivalent of this text
                    if specific == "#":
                        tmp_split_list.append(
                            m.Text("ε", weight=m.BOLD, slant=m.ITALIC))
                    else:
                        tmp_split_list.append(
                            m.Text(specific, weight=m.BOLD, slant=m.ITALIC))
                tmp_item.append(tmp_split_list)

            # append this list of manim productions to the manim cfg dictionary
            manim_cfg[key].append(tmp_item)
        return manim_cfg
    except:
        error.ERR_left_recursion_detected()
        return CFG_FILE_ERROR

class ContextFreeGrammar:

    def __init__(self, cfg_path: Path) -> None:
        """Initialises the ContextFreeGrammar object.

        Args:
            cfg_path (Path): Path to the provided CFG file
        """
        # set up the cfg information
        self._cfg_path = cfg_path
        self.cfg_contents = cfg_path.read_text()
        self.prods = get_prods(self.cfg_contents)
        self.is_ambiguous = False

        # initialise the stuctures of the cfg
        if self.prods != None:
            self._init_structures()
            self.manim_cfg = populate_manim_cfg(self.cfg_dict, self.lead_to)
        else:
            self.prods = ERROR

    def _init_structures(self) -> None:
        """ Creates the structures to be used in the algorithms.
        """        
        self.nonterminals = []
        self.terminals = []
        self.lead_to = []
        self.cfg_dict = {}

        # structures for first set
        self.first_set = {}
        self.first_set_calculated = False
        self.manim_firstset_contents = {}
        self.manim_firstset_lead = {}
        self.firstset_index = {}
        self.fstack = []

        # structures for follow set
        self.follow_set = {}
        self.follow_set_calculated = False
        self.manim_followset_contents = {}
        self.manim_followset_lead = {}
        self.vis_has_epsilon = False

        # structures for parsetable
        self.parsetable = {}
        self.parsetable_calculated = False

        # structures for the LL(1) parser
        self.parser_ll1 = None
        self.is_parser_ll1_set_up = False
        
        # assigns initial values to these structures
        self._assign_structures()

    def _assign_structures(self) -> None:
        """ Initialises the structures to be used in the CFG. 

        Args:
            prods (List): List of productions.
        """
        # initialise base structures
        self.start_symbol = self.prods[0][0]

        for p_seq in self.prods:
            self.cfg_dict[p_seq[0]] = p_seq[1]

            self.first_set[p_seq[0]] = []
            self.manim_firstset_contents[p_seq[0]] = m.VGroup()
            self.firstset_index[p_seq[0]] = []

            self.follow_set[p_seq[0]] = []
            self.manim_followset_contents[p_seq[0]] = m.VGroup()
            self.manim_followset_lead[p_seq[0]] = None

            self.nonterminals.append(p_seq[0])
            self.lead_to.append(p_seq[1])

        # get all lead-to elements in a list
        tmp = []
        for t in list(chain(*self.lead_to)):
            splitp = list(filter(None, re.findall(RE_PRODUCTION, t)))
            tmp.append(splitp)

        # add only terminals to list, as well as create empty follow set for them
        # append $ to terminals by default
        self.terminals.append("$")
        for t in set(list(chain(*tmp))):
            if re.match(RE_TERMINAL, t) and t != "#":
                self.terminals.append(t)
                self.follow_set[t] = []
                self.manim_followset_contents[t] = m.VGroup()


        # set start symbol
        self.start_symbol = list(self.cfg_dict.keys())[0]

    def get_next_production(self, first_set) -> int:
        """Helper function to get the index of the first-encountered production with an empty first set.

        Args:
            first_set (Dictionary): The first set of a given CFG.

        String: The production which requires a first set to be calculated. 
            Integer: 
        """    
        for item in first_set.items():
            if item[1] == []:
                return item[0]
        return -1

    def show_contents(self) -> None:
        """Helper function to display the CFG contents.
        """        
        typer.echo(self.cfg_contents)

    def show_first_set(self) -> None:
        """Helper function to display the first set. 
        """        
        if not self.first_set_calculated:
            self._calculate_first_set(self.start_symbol, [])
            self._clean_first_set()
            self.first_set_calculated = True

        display_helper.info_secho("Showing first set:")
        display_helper.pretty_print_dict(self.first_set)
        self.first_set_calculated = True

    def show_first_set_testing(self) -> None:
        self._calculate_first_set(self.start_symbol, [])
        self._clean_first_set()
        typer.echo(self.first_set) 

    def reset_first_set(self, calculate_again = True) -> None:
        """Resets the first sets in preparation for another calculation
        """        
        self.first_set = {}

        # reset structures
        for p_seq in self.prods:
            self.first_set[p_seq[0]] = []
            self.firstset_index[p_seq[0]] = []

        # calculate first set
        if calculate_again:
            self._calculate_first_set(self.start_symbol, [])
            self.first_set_calculated = True

    def _calculate_first_set(self, production, pstack) -> None:
        """Recursively calculates the first set and stores it to the internal first set structure

        Args:
            production (String): The production being examined. Initially it is the start symbol.
            pstack (List): The production stack. 
        """        
        global has_epsilon

        # prevents deep recursion
        if production in pstack and len(pstack) > 1:
            return

        pstack.append(production)

        # if production does not have a first set
        try:
            # loop through values which a production leads to
            for p in self.cfg_dict[production]:

                # add the appended production to fstack
                # TODO check this thing
                self.fstack.append(production + " -> " + p)
                # if a production is/ starts with a non-terminal
                if p in self.cfg_dict or p[0].isupper():
                    # find all the productions which are led by a non-terminal
                    p_nt = list(
                        filter(None, re.findall(RE_PRODUCTION, p)))

                    for index, item in enumerate(p_nt, start=0):
                        current_item = item.strip()
                        # if a terminal is encountered after the list
                        if re.match(RE_TERMINAL, current_item):
                            for j, ps in enumerate(pstack, start=0):
                                # add First(Y) - #
                                if current_item not in self.first_set[ps]:
                                    # add production which led to this to the parse table
                                    # typer.echo("WE GOT TO " + current_item + " VIA ")
                                    # typer.echo(self.fstack[j])
                                    self.firstset_index[ps].append(
                                        self.fstack[j])
                                    self.first_set[ps].append(current_item)
                                else:
                                    self.is_ambiguous = True

                            # reset the fstack
                            self.fstack.pop()
                            break
                        else:
                            # we should add A without epsilon if we are the top level production
                            had_eps = "#" in self.first_set[current_item]
                            self._calculate_first_set(
                                current_item, pstack)
                            has_eps = "#" in self.first_set[current_item]

                            # we don't include the last epsilon if we 
                            # 1) found it in the first set of a non-terminal AND
                            # 2) we didn't have it in this first set beforehand AND
                            # 3) we are the top level production (ie. not in the middle of recursion)
                            # 4) we are not the LAST production 

                            if not had_eps and has_eps and len(pstack) == 1 and index != len(p_nt) - 1:
                                self.first_set[production].remove("#")
                            
                            if not self.vis_has_epsilon:
                                break
                    self.vis_has_epsilon = False
                else:
                    # if a production starts with a terminal
                    first_terminal = list(
                        filter(None, re.findall(RE_TERMINAL, p)))

                    if first_terminal[0] == "#":
                        # the non-terminal which led to this may disappear in the original production
                        self.vis_has_epsilon = True
                        # appends this terminal to the first set of previous non-terminals

                    # typer.echo("state of fstack: len -> " + str(len(self.fstack)) + " vs pstack " + str(len(pstack)))
                    for j, ps in enumerate(pstack, start=0):
                        # add First(P) - # if down the stack
                        if first_terminal[0] not in self.first_set[ps]:
                            self.firstset_index[ps].append(self.fstack[j])
                            self.first_set[ps].append(first_terminal[0]) 
                        else:
                            self.is_ambiguous = True

                    # TODO unpack why fstack works like this for bla but not all others    
                    # for p in range(len(pstack)):
                    #     self.fstack.pop()

                    # TODO fstack for the next round
                    # display_helper.info_secho("....")
                    # display_helper.structure_secho(pstack)
                    # typer.echo(self.firstset_index)
                    # display_helper.structure_secho(self.first_set)
                    # typer.echo(self.fstack)
                    # display_helper.success_secho("....")

            # by this point, we have recursively found a bunch of first sets
            # so let's find those that are still empty
            if len(pstack) == 1:
                pstack = []
                self.fstack = []
                empty_set_nt = self.get_next_production(self.first_set)
                if empty_set_nt != -1:
                    self._calculate_first_set(empty_set_nt, [])
            else:
                pstack.pop()
                self.fstack = self.fstack[1:]

        except KeyError:
            error.ERR_key_not_given_in_CFG(production)

    def _clean_first_set(self) -> None:
        """Helper function to standardise the appearance of the first set by placing epsilons at the end of the list.
        """        
        for key in self.first_set.keys():
            for i in self.first_set[key]:
                if i == "#":
                    self.first_set[key].remove(i)
                    self.first_set[key].append(i)

    def show_follow_set(self) -> None:
        """Displays the calculated follow set. 
        """        
        if not self.follow_set_calculated:
            self._calculate_follow_set(True)
            self.follow_set_calculated = True

        display_helper.info_secho("Showing follow set:")
        display_helper.pretty_print_dict(self.follow_set)
        self.follow_set_calculated = True

    def show_follow_set_testing(self) -> None:
        """Displays the calculated follow sets for each non-terminal
        """        
        self._calculate_follow_set(True)
        nt_follow = {}
        for key in self.follow_set.keys():
            if re.match(RE_NONTERMINAL, key):
                nt_follow[key] = self.follow_set[key]
        typer.echo(nt_follow)

    def reset_follow_set(self, calculate_again = True) -> None:
        """Resets the first sets in preparation for another calculation
        """        
        # reset the follow set structure and set non-terminal sets to empty
        self.follow_set = {}
        for p_seq in self.prods:
            self.follow_set[p_seq[0]] = []

        # obtain the productions
        tmp = []
        for t in list(chain(*self.lead_to)):
            splitp = list(filter(None, re.findall(RE_PRODUCTION, t)))
            tmp.append(splitp)

        # create an empty follow set for the terminals
        for t in set(list(chain(*tmp))):
            if re.match(RE_TERMINAL, t) and t != "#":
                self.follow_set[t] = []

        if calculate_again:
            # calculate the follow set
            self._calculate_follow_set(True)
            self.follow_set_calculated = True

    def _calculate_follow_set(self, is_start_symbol) -> None:
        """Algorithm for calculating the follow set of a given CFG.

        Args:
            is_start_symbol (bool): Whether or not we begin with the start symbol.
        """
        for production in self.cfg_dict.keys():
            # Rule 1
            if is_start_symbol:
                self.follow_set[production].append("$")
                is_start_symbol = False

            # inspect each element in the production
            for p in self.cfg_dict[production]:

                # split up the productions which are contained within this list
                pps = list(filter(None, re.findall(RE_PRODUCTION, p)))

                # examine each production and obtain follow sets
                for index, item in enumerate(pps, start=0):

                    if index == len(pps) - 1 and item != "#" and item != production:
                        # temporarily append production to let us then iterate over and replace it
                        if production not in self.follow_set[item]:
                            self.follow_set[item].append(production)

                    elif index < len(pps) - 1:
                        next_item = pps[index + 1]
                        # if an item is directly followed by a terminal, it is appended to its follow set
                        if re.match(RE_TERMINAL, next_item) and next_item not in self.follow_set[item]:
                            self.follow_set[item].append(next_item)
                        else:
                            # we add the first of the non-terminal at this next index
                            tmp_first= self.first_set[next_item]
                            for t in tmp_first:
                                if t != "#" and t not in self.follow_set[item]:
                                    self.follow_set[item].append(t)
                                else:
                                    # we found an epsilon, so this non-terminal may disappear
                                    # we add its follow to the follow set of item
                                    # as long as this item is NOT at the end of the list
                                    if t == "#":
                                        if index + 1 == len(pps) - 1:
                                            # if B -> # and A -> aB, then follow(a) = Follow(A) 
                                            if production not in self.follow_set[item]: self.follow_set[item].append(production)
                                        else:
                                            self.follow_set[item].append(next_item)
                          

        # clean the follow set
        start_symbol = list(self.cfg_dict.keys())[0]
        self.is_cleaned = []
        self.is_cleaned = self.get_reset_cleaned_set()
        self.clean_follow_set(start_symbol, [])

    def get_reset_cleaned_set(self) -> Dict:
        """Helper function to obtain a dictionary which holds whether or not the follow sets have been cleaned.

        Returns:
            Dictionary: Contains {NT: False} for each non-terminal NT.
        """        
        tmp_c = {}
        for fc in self.follow_set.keys():
            tmp_c[fc] = False
        return tmp_c

    def clean_follow_set(self, start, pstack) -> None:
        """Cleans the follow set after the calculation: Replaces non-terminals with their respective follow sets and removes epsilon elements. 

        Args:
            start (String): The start symbol.
            pstack (List): Production stack. 
        """      
        tmp_nts = []
        pstack.append(start)

        # clean up the sets
        items = self.follow_set[start]

        # loop through the items in a given follow set and replace non-terminals with
        # their associated follow sets
        for index, item in enumerate(items, start=0):
            # we have an item in the set
            if re.match(RE_NONTERMINAL, item):
                # temporarily remove the non-terminal from the list to prevent recursion
                items.remove(item)
                tmp_nts.append(item)
                self.clean_follow_set(item, pstack)
            else:
                # we append the descended terminals to the upwards stacks
                for p in pstack:
                    if p != start and item not in self.follow_set[p]:
                        self.follow_set[p].append(item)

        self.is_cleaned[start] = True

        if len(pstack) == 1:
            pstack = []
            # gets the next not cleaned set
            for c in self.is_cleaned.keys():
                if self.is_cleaned[c] == False:
                    self.clean_follow_set(c, pstack)
        else:
            pstack.pop()
    
    def set_parser_ll1(self, parser) -> int:
        """Sets the internal parser. 

        Args:
            parser (ParserLL1): ParserLL1 Object
        """        
        # set pt internals
        self.parser_ll1 = parser
        self.is_parser_ll1_set_up = True
        return SUCCESS

    def setup_parsetable(self) -> int:
        self.parsetable = pt.ParsingTable(self.terminals, self.nonterminals, self.cfg_dict)
        self.parsetable.set_internals(
                self.first_set, self.follow_set, self.firstset_index)
        return SUCCESS

    def calculate_parsetable(self) -> int:
        self.parsetable.populate_table()
        self.parsetable_calculated = True
        return SUCCESS