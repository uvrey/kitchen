""" For reading and working with language specification files """

import configparser
from pathlib import Path
from kitchen import SUCCESS, display_helper, cli_helper
import typer
import re

def get_spec_path(config_file: Path) -> Path:
    """Obtains the path to the currently-loaded language specification file

    Returns:
        Path: Path to the CFG file.
    """    
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["spec_path"])

def get_spec(cfg):
    if cli_helper.CONFIG_FILE_PATH.exists():
            spec_path = get_spec_path(cli_helper.CONFIG_FILE_PATH)
    else:
        display_helper.fail_secho(
            'Config file not found. Please run "kitchen init"',
        )
        raise typer.Exit(1)

    # only create the spec if the file exists and can be read
    if spec_path.exists() and str(spec_path) != "" and str(spec_path) != ".":
        return Specification(spec_path, cfg)
    else:
        return None
    
def _clean_inp_stream(inps):
    cleaned = []
    for i in inps:
        cleaned.append(i.strip())
    return cleaned

class Specification:
    def __init__(self, spec_path, cfg):
        # store token/ regex sequences 
        self.path = spec_path
        self.spec_contents = spec_path.read_text()
        self.token_spec = {}
        self.cfg = cfg

        # associate spec regex with token types
        self.read_to_spec()

    def read_to_spec(self):
        contents = self.spec_contents.split("\n")
        read_toks = False
        for line in contents:
            if len(line) > 0 and line.strip()[0] != "#":
                if line == "Tokens:":
                    read_toks = True
                else:
                    if read_toks:
                        if line.strip() == "---":
                            return
                        else:
                            self._process_regex_spec(line)
    
    def _process_regex_spec(self, line):
        split = line.split(" ")
        cleaned_specs = _clean_inp_stream(split)
        typer.echo(cleaned_specs)
        try:
            t = cleaned_specs[1]
            regex = cleaned_specs[2]
            # add regex for each terminal
            if t in self.cfg.terminals:
                self.token_spec[t] = regex
            else:
                display_helper.info_secho("Note: " + t + " is defined in specificiation but does not appear in CFG.")
        except:
            display_helper.fail_secho("Some error with regex spec file occurred.")
            return

    def show_contents(self):
        display_helper.structure_secho(self.spec_contents)

    def _match(self, inp):
        for key in self.token_spec:
            if re.match(self.token_spec[key], inp):
                return key

    def get_tokens_from_input(self, inp):
        tokens = []
        inp_stream = inp.strip().split(" ")
        cleaned_stream = _clean_inp_stream(inp_stream)
        for c in cleaned_stream:
            tokens.append(self._match(c))
        
        if len(tokens) != len(cleaned_stream):
            display_helper.fail_secho("Could not match all tokens.")
            return None
        return tokens

