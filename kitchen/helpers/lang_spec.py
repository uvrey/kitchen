""" Reads and handles language specification files. """
# kitchen/helpers/lang_spec.py

import configparser
from pathlib import Path
import typer
import re


from kitchen import ERROR 
from kitchen.helpers import (
        display, 
        config,
)

def get_spec_path(config_file: Path) -> Path:
    """Obtains the path to the currently-loaded language specification file.

    Returns:
        Path: Path to the CFG file.
    """    
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["spec_path"])

def get_spec(cfg):
    if config.CONFIG_FILE_PATH.exists():
            spec_path = get_spec_path(config.CONFIG_FILE_PATH)
    else:
        display.fail_secho(
            'Config file not found. Please run "kitchen init"',
        )
        raise typer.Exit(1)

    # only create the spec if the file exists and can be read
    if spec_path.exists() and str(spec_path) != "" and str(spec_path) != ".":
        return Specification(spec_path, cfg)
    else:
        return None
    
def clean_inp_stream(inps) -> list:
    cleaned = []
    for i in inps:
        cleaned.append(i.strip())
    return cleaned

class Specification:
    def __init__(self, spec_path: str, cfg):
        """Initialises the Specification object.

        Args:
            spec_path (str): Path to spec file.
            cfg (ContextFreeGrammar): Loaded CFG.
        """        
        # store token/ regex sequences 
        self.path = spec_path
        self.spec_contents = spec_path.read_text()
        self.token_spec = {}
        self.cfg = cfg
        self.reserved_words = []

        # associate spec regex with token types
        self.read_to_spec()

    def read_to_spec(self) -> None:
        """Reads the contents of the language specification file to the 
           Specification object.
        """        
        contents = self.spec_contents.split("\n")
        line_count = 0
        read_toks = False
        reserved = False
        for line in contents:
            if len(line) > 0 and line.strip()[0] != "#":
                if line == "Reserved words:":
                    reserved = True
                else:
                    if line == "Tokens:":
                        read_toks = True
                    else:
                        if read_toks:
                            if line.strip() == "---":
                                break
                            else:
                                self._process_regex_spec(line)
                                line_count = line_count + 1
                        if reserved:
                            if line.strip() == "---":
                                reserved = False
                            else:
                                self._process_reserved_words(line.strip())

        # if line_count != len(self.cfg.terminals): TODO
        #     display.fail_secho("Note: Some terminals in the CFG are 
        # missing regex definitions :(")
    
    def _process_reserved_words(self, line: str) -> None:
        """Processes reserved words in the specification.

        Args:
            line (str): Line to be processed.
        """        
        split = line.split(" ")
        cleaned_specs = clean_inp_stream(split)
        try:
            self.reserved_words.append(cleaned_specs[2])
        except:
            display.fail_secho("Some error with reserved words occurred.")

    def _process_regex_spec(self, line: str) -> None:
        """Processes the regex specifications inside the file.

        Args:
            line (str): Line to be processed.
        """        
        split = line.split(" ")
        cleaned_specs = clean_inp_stream(split)
        try:
            t_found = cleaned_specs[1]
            regex = cleaned_specs[2]
            # add regex for each terminal
            if t_found in self.cfg.terminals:
                self.token_spec[t_found] = regex
            # else: TODO
            #     display.info_secho("Note: " + t_found + " is defined 
            # in specificiation but does not appear in CFG.")
        except:
            display.fail_secho("Some error with regex processing occurred.")
            return

    def show_contents(self) -> None:
        """Displays the contents of the specification file.
        """        
        display.structure_secho(self.spec_contents)

    def _match(self, inp: str) -> str:
        """Matches an input to a token in the specification file. 

        Args:
            inp (str): Input to be matched.

        Returns:
            str: Token.
        """        
        for key in self.token_spec:
            if inp in self.reserved_words:
                return inp
            if re.match(self.token_spec[key], inp):
                return key
        return ERROR

    def get_tokens_from_input(self, inp: str) -> list:
        """Obtains tokens from several inputs in one string.

        Args:
            inp (str): Input to be processed.

        Returns:
            list: Token stream.
        """        
        tokens = []
        inp_stream = inp.strip().split(" ")
        cleaned_stream = clean_inp_stream(inp_stream)
        for c in cleaned_stream:
            matched = self._match(c)
            if matched != ERROR:
                tokens.append(Token(matched, c))
            else:
                display.fail_secho("\tCould not match [" + c + "] to a token.")
                return ERROR
        if len(tokens) != len(cleaned_stream):
            display.fail_secho("Could not match all tokens.")
            return None
        return tokens

def get_index_by_token_type(tokens: list, t) -> int:
    """Gets the index of some token in a token list, given that the list may
       contain either Token objects or strings. 

    Args:
        tokens (list): Token list.
        t (str/ Token): Token to be located.

    Returns:
        int: Index of t in tokens.
    """    
    for i, t in enumerate(tokens, start = 0):
        try:
            if tokens.type == t:
                return i
        except:
            return tokens.index(t)

def get_token_format(tokens, values = False, types = False, as_list = False) \
-> None:
    """Creates list of token types or returns the list itself if it is empty.

    Args:
        tokens (list): List of tokens.
        as_list (bool, optional): If list format is required. 
                                  Defaults to False.

    Returns:
        str/ list: Tokens formatted as a string or a list.
    """    
    ts = []
    try:
        for t in tokens:
            if types:
                ts.append(t.type)
            elif values:
                ts.append(t.value)
        if as_list: 
            return ts
        else:
            return " ".join(ts)
    except:
        if as_list: 
            return tokens
        return " ".join(tokens)

class Token:
    def __init__(self, type: str, value: str):
        """Initialises a Token object.

        Args:
            type (str): Token type, from the specification file.
            value (str): Token value, based on processed input.
        """        
        self.type = type
        self.value = value
        
    
