""" Configuration for the application """

import configparser
from pathlib import Path
import typer

from kitchen import (
    CFG_WRITE_ERROR, 
    DIR_ERROR, 
    ERRORS, 
    FILE_LOADING_ERROR, 
    FILE_LOADING_EXISTS_ERROR, 
    FILE_LOADING_NONE_ERROR, 
    FILE_LOADING_DIR_ERROR, 
    SUCCESS, 
    __app_name__,
    display_helper,
    parse_table as pt,
    animation,
    error, 
    parser as p,
)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

def init_app(cfg_path: str) -> int:
    """Initialises the application by creating its configuration file and CFG path.

    Args:
        cfg_path (str): CFG path.

    Returns:
        int: Status code.
    """    
    """Initialize the application configuration file."""
    config_code = _init_config_file()
    if config_code != SUCCESS:
        return config_code
    cfg_code = _create_cfg_path(cfg_path)
    if cfg_code != SUCCESS:
        return cfg_code
    return SUCCESS

def _init_config_file() -> int:
    """Initialises the configuration file directory and file. 

    Returns:
        int: Status code.
    """    
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return FILE_LOADING_ERROR
    return SUCCESS

def _create_cfg_path(cfg: str) -> int:
    """Creates a path to the CFG in the configuration of the application.

    Args:
        cfg (str): Path to the CFG file.

    Raises:
        typer.Exit: Exits when CFG path could not be written to the configuration.

    Returns:
        int: Status code.
    """    
    # check that the cfg file exists
    cfg_path = Path(cfg)
    path_error = _validate_path([cfg_path])

    if path_error:
        typer.secho(
            f'Loading files failed with "{ERRORS[path_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # create the CFG
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {"cfg": cfg_path}
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return CFG_WRITE_ERROR
    return SUCCESS

# Helper function to validate that the given cfg path is valid
def _validate_path(paths):
    """Checks the validity of paths.

    Args:
        paths (List): List of paths to be validated.
    """    
    for path in paths:
        if path is None:
           return FILE_LOADING_NONE_ERROR
        elif path.is_dir():
            return FILE_LOADING_DIR_ERROR
        elif not path.exists():
            return FILE_LOADING_EXISTS_ERROR
        return SUCCESS

def load_app(path) -> None:
    """Loads the application given a CFG path.

    Args:
        path (String): Path to the CFG file.

    Raises:
        typer.Exit: When CFG loading is unsuccesful. 
    """    
    app_init_error = init_app(path)
    if app_init_error:
        typer.secho(
            f'Loading files failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"Initialisation successful! The cfg path is " + path, 
                    fg=typer.colors.GREEN)

def _set_parsetable(cfg) -> int:
    if not cfg.parsetable_calculated:
    # reset cfg structures before we begin if needed
        if not cfg.follow_set_calculated:
            cfg.reset_follow_set()

        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        # initialise parsetable
        cfg.setup_parsetable()

        # calculate parsetable
        code = cfg.calculate_parsetable()
        return code
    
def _show_parsetable(cfg) -> None:
    """Displays the calculated parse table. 

    Args:
        cfg (ContextFreeGrammar): CFG for which the parse table is to be calculated.
    """    
    _set_parsetable(cfg)
    cfg.parsetable.print_parse_table()

def handle_input(inp, cfg) -> None:
    """Handles user input by performing commands or otherwise parsing using the default method, LL(1)

    Args:
      inp (String): User input. 
      cfg (ContextFreeGrammar): ContextFreeGrammar Object based on loaded CFG.     
    """    
    if inp.strip()[0] == "\\":
        _process_command(inp, cfg)
    else:
        _init_parsing_ll1(inp.strip(), cfg)

def _init_parsing_ll1_via_cmd(inp, cfg) -> int:
    """Initialises LL(1) parsing via the command \\ll1 <input>

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object

    Returns:
        int: _description_
    """    
    config = inp.strip()[4:7].strip()
    if config == "\\v":
        to_parse = inp.strip()[7:].strip()
        if to_parse == "":
            error.ERR_no_input_given()
        else:
           # kitchen.generate_parse_ll1(to_parse)
           pass
    else:
        _init_parsing_ll1(inp[4:].strip(), cfg)
    return SUCCESS

def _init_parsing_ll1(inp, cfg) -> int:
    """Initialise parsing using LL(1) by associating the CFG with its own LL(1) Parser object.

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object
    
    Returns:
        int: Status code
    """    
    # calculate the parse table if it has not yet been done so
    if not cfg.parsetable_calculated:
        _set_parsetable(cfg)

    # set up the cfg parser 
    code = _set_cfg_parser_ll1(inp, cfg)

    # parse the input
    if code == SUCCESS:
        if inp == cfg.parser_ll1.inp:
            inp = ""
        cfg.parser_ll1.parse_ll1(cfg.start_symbol, inp)
    return SUCCESS
            
def _set_cfg_parser_ll1(inp, cfg) -> int:
    """Initialises a new ParserLL1 object if it has not been initialised in this app session yet.

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object    Args:

    Returns:
        int: Status code
    """    
    code = SUCCESS
    if not cfg.is_parser_ll1_set_up:
        code = cfg.set_parser_ll1(p.ParserLL1(inp, cfg))
    return code

def _init_parsing_vis_shortcut(inp) -> int:
    """Initialises the visualisation of LL(1) parsing on some input, via the app shortcut '\\v <input>'.

    Args:
        inp (str): Input string

    Returns:
        int: Status code
    """    
    to_parse = inp.strip()[2:].strip()
    if to_parse == "":
        error.ERR_no_input_given()
    else:
        #kitchen.generate_parse_ll1(to_parse)
        pass
    return SUCCESS

def _process_command(inp, cfg) -> None:
    """Helper function to process a command from the user.

    Args:
        inp (String): User input.
        cfg (ContextFreeGrammar): ContextFreeGrammar Object based on loaded CFG.

    Raises:
        typer.Exit: Exits the application when the user requests this. 
    """    

    if inp == "\\m":
        display_helper.print_menu()
    elif inp == "\\q":
        raise typer.Exit()
    elif inp == "\\dsl":
        # TODO start DSL tool
        pass

    elif inp == "\\show first" or inp == "\\fs":
        cfg.show_first_set()
    
    elif inp == "\\vis first" or inp == "\\vfs":
        pass
      
    elif inp == "\\show follow" or inp == "\\fw":
        cfg.show_follow_set()

    elif inp == "\\vis follow" or inp == "\\vfw":
        pass

    elif inp == "\\show parsetable" or inp == "\pt":
        _show_parsetable(cfg)

    elif inp == "\\vis parsetable" or inp == "\\vpt":
        # a = animation.Animation()
        # a.setup_manim("", [], [], None, None,
        #               False, False, True, False)
        # a.render()
        pass
        
    elif inp == "\\show parse structures" or inp == "\ptss":
        pass
    elif inp == "\\l":
        new_path = typer.prompt("New path to CFG")
        load_app(new_path)
        # TODO reload CFG structure
      
    elif inp == "\\show cfg" or inp == "\\cfg":
        cfg.show_contents()

    elif inp == "\\c":
        typer.echo("Configuring animation settings")

    elif inp[0:4] == "\\ll1":
        _init_parsing_ll1_via_cmd(inp, cfg)

    elif inp[0:2] == "\\v":
        _init_parsing_vis_shortcut(inp, cfg)
    
    else:
        display_helper.fail_secho('Invalid command')



