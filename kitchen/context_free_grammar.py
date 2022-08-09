import configparser
from pathlib import Path
import re
from wsgiref import validate
import typer
from kitchen import CFG_ERROR_NT_FORMAT, SUCCESS, RE_TERMINAL, RE_NONTERMINAL, RE_PRODUCTION, error

DEFAULT_CFG_PATH = Path.home().joinpath(
    "." + Path.home().stem + "cfg.txt"
)
DEFAULT_REGEX_PATH = Path.home().joinpath(
    "." + Path.home().stem + "regex.yaml"
)

def get_cfg_path(config_file: Path) -> Path:
    """Return the current path to the cfg file."""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)
    return Path(config_parser["General"]["cfg"])

def get_prods(cfg_contents):
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

class ContextFreeGrammar:
    def __init__(self, cfg_path: Path) -> None:
        self._cfg_path = cfg_path
        self.cfg_contents = cfg_path.read_text()
        self.prods = get_prods(self.cfg_contents)

