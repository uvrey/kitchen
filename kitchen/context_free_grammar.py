""" creates the context free grammar """
# kitchen/context_free_grammar.py

import configparser
from itertools import chain
from pathlib import Path
import re
from manim import *
from wsgiref import validate
import typer
import pprint
from kitchen import (
    CFG_ERROR_NT_FORMAT,
    ERROR, 
    SUCCESS, RE_TERMINAL, 
    RE_NONTERMINAL, 
    RE_PRODUCTION,
    error,
    animation
)

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
    return Path(config_parser["General"]["cfg"])

def get_prods(cfg_contents):
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
        if not re.match(RE_NONTERMINAL, pps[0]):
            typer.echo("Error at line " + line + "-> " + pps[0])
            return CFG_ERROR_NT_FORMAT

        tmp_prod.append(re.sub('[\s+]', '', pps[0]))

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

def generate_first_set(self):
    a = animation.Animation()
    a.setup_manim("", [], [], self.parser, self.parsetable, True, False)
    a.render()

def generate_follow_set(self):
    a = animation.Animation()
    a.setup_manim("", [], [], self.parser, self.parsetable, False, True)
    a.render()

def generate_parse_table(self):
    a = animation.Animation()
    a.setup_manim("", [], [], self.parser, self.parsetable,
                    False, False, True, False)
    a.render()

def generate_parse_ll1(self, input):
    a = animation.Animation()
    inp_list = input.split(" ")
    a.setup_manim(input, inp_list, [], self.parser, self.parsetable,
                    False, False, False, True)
    a.render()



def populate_manim_cfg(cfg_dict, lead_to):
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
            manim_cfg[key] = [Text(key, weight=BOLD)]

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
                            Text("ε", weight=BOLD, slant=ITALIC))
                    else:
                        tmp_split_list.append(
                            Text(specific, weight=BOLD, slant=ITALIC))
                tmp_item.append(tmp_split_list)

            # append this list of manim productions to the manim cfg dictionary
            manim_cfg[key].append(tmp_item)
        return manim_cfg
    except:
        typer.echo("SOME ERROR POPULATING MANIM CFG OCCURED")
        raise typer.Abort()


def get_next_production(first_set):
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


class ContextFreeGrammar:

    def __init__(self, cfg_path: Path) -> None:
        """Initialises the ContextFreeGrammar object.

        Args:
            cfg_path (Path): Path to the provided CFG file
        """
        # set up the cfg information
        self._cfg_path = cfg_path
        self.cfg_contents = cfg_path.read_text()
        prods = get_prods(self.cfg_contents)

        # initialise the stuctures of the cfg
        if prods != None:
            self._init_structures(prods)
            self.manim_cfg = populate_manim_cfg(self.cfg_dict, self.lead_to)
        else:
            prods = ERROR
        typer.secho(
            f'CFG loaded :)',
            fg = typer.colors.GREEN
        )

    def _init_structures(self, prods) -> None:
        """ Creates the structures to be used in the algorithms.

        Args:
            prods (List): List of productions as scraped from the CFG contents.
        """        
        self.nonterminals = []
        self.terminals = []
        self.lead_to = []
        self.cfg_dict = {}

        # structures for first set
        self.first_set = {}
        self.manim_firstset_contents = {}
        self.manim_firstset_lead = {}
        self.firstset_index = {}
        self.fstack = []

        # structures for follow set
        self.followset = {}
        self.manim_followset_contents = {}
        self.manim_followset_lead = {}
        self.vis_has_epsilon = False
        
        # assigns initial values to these structures
        self._assign_structures(prods)

    def _assign_structures(self, prods) -> None:
        """ Initialises the structures to be used in the CFG. 

        Args:
            prods (List): List of productions.
        """
        # initialise base structures
        for p_seq in prods:
            self.cfg_dict[p_seq[0]] = p_seq[1]

            self.first_set[p_seq[0]] = []
            self.manim_firstset_contents[p_seq[0]] = VGroup()
            self.firstset_index[p_seq[0]] = []

            self.followset[p_seq[0]] = []
            self.manim_followset_contents[p_seq[0]] = VGroup()
            self.manim_followset_lead[p_seq[0]] = None
            self.nonterminals.append(p_seq[0])
            self.lead_to.append(p_seq[1])

        # get all lead-to elements in a list
        tmp = []
        for t in list(chain(*self.lead_to)):
            splitp = list(filter(None, re.findall(RE_PRODUCTION, t)))
            tmp.append(splitp)

        # add only terminals to list, as well as create empty follow set for them
        for t in set(list(chain(*tmp))):
            if re.match(RE_TERMINAL, t) and t != "#":
                self.terminals.append(t)
                self.followset[t] = []
                self.manim_followset_contents[t] = VGroup()
            elif t == "#":
                self.terminals.append(t)
    
    def show_contents(self) -> None:
        """Helper function to display the CFG contents.
        """        
        typer.echo(self.cfg_contents)

    def show_first_set(self) -> None:
        """Helper function to display the first set. 
        """        
        start_symbol = list(self.cfg_dict.keys())[0]
        self._calculate_first_set(start_symbol, [])
        self._clean_first_set()
        typer.secho(
            f'Showing first set...',
            fg= typer.colors.GREEN
        )
        pprint.pprint(self.first_set)

    def _calculate_first_set(self, production, pstack) -> None:
        """Recursively calculates the first set and stores it to the internal first set structure

        Args:
            production (String): The production being examined. Initially it is the start symbol.
            pstack (List): The production stack. 
        """        
        global has_epsilon
        pstack.append(production)

        # if production does not have a first set
        try:
            if self.first_set[production] == []:
                # loop through values which a production leads to
                for p in self.cfg_dict[production]:
                    # add the appended production to fstack
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
                                    if current_item not in self.firstset[ps]:
                                        # add popped element to the parse table
                                        self.firstset_index[ps].append(
                                            self.fstack[j])
                                        self.first_set[ps].append(current_item)
                                # reset the fstack
                                self.fstack.pop()
                                break
                            else:
                                self._calculate_first_set(
                                    current_item, pstack)
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
                        for j, ps in enumerate(pstack, start=0):
                            if first_terminal[0] not in self.first_set[ps]:
                                self.firstset_index[ps].append(self.fstack[j])
                                self.first_set[ps].append(first_terminal[0])
                        # reset the stack once we have looked at it
                        self.fstack.pop()

            # by this point, we have recursively found a bunch of first sets
            # so let's find those that are still empty
            if len(pstack) == 1:
                pstack = []
                empty_set_nt = get_next_production(self.first_set)
                if empty_set_nt != -1:
                    self._calculate_first_set(empty_set_nt, [])
            else:
                pstack.pop()

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

    
