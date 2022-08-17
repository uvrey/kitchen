""" For reading and working with language specification files """

import configparser
from pathlib import Path
from kitchen import SUCCESS, display_helper, cli_helper
import typer

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

    if spec_path.exists():
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
        # TODO read in as yaml
        # store token/ regex sequences etc. 
        self.path = spec_path
        self.spec_contents = spec_path.read_text()
        self.token_spec = {}
        self.cfg = cfg

    def _populate_matches(self):
        pass

    def show_contents(self):
        display_helper.structure_secho(self.spec_contents)

    def get_tokens_from_input(self, inp):
        tokens = []
        inp_stream = inp.strip().split(" ")
        cleaned_stream = _clean_inp_stream(inp_stream)
        # TODO match tokens to regex here
        return []

