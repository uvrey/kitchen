""" Configuration for the application """

from ast import BoolOp, excepthandler
from cgitb import reset
import configparser
from glob import glob
from pathlib import Path
from re import L
from xmlrpc.client import Boolean
import typer
import os
import shutil
import manim as m
import subprocess

from kitchen import (
    CFG_WRITE_ERROR, 
    DIR_ERROR, 
    ERROR,
    ERRORS, 
    FILE_LOADING_ERROR, 
    FILE_LOADING_EXISTS_ERROR, 
    FILE_LOADING_NONE_ERROR, 
    FILE_LOADING_DIR_ERROR, 
    AMBIGUOUS_ERROR,
    SUCCESS, 
    __app_name__,
    display_helper,
    parse_table as pt,
    animation as anim,
    error, 
    parser as p,
    config,
    dsl_tool
)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
PARTIALS_PATH = ""

def init_app(cfg_path: str, spec_path = None) -> int:
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

    # create cfg path
    cfg_code = _create_paths(cfg_path, spec_path)

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

def _create_paths(cfg_path: str, spec_path = None) -> int:
    """Creates a path to the CFG in the configuration of the application.

    Args:
        cfg (str): Path to the CFG file.

    Raises:
        typer.Exit: Exits when CFG path could not be written to the configuration.

    Returns:
        int: Status code.
    """    
    # check that the cfg file exists
    cfg_path = Path(cfg_path)
    path_error = _validate_path([cfg_path])

    if path_error:
        typer.secho(
            f'Loading the CFG file failed with "{ERRORS[path_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # load up the cfg config
    config_parser = configparser.ConfigParser()
    config_parser['General'] = {}
    config_parser['General']['cfg_path'] = str(cfg_path)
    config_parser['General']['spec_path'] = ''
    typer.echo(CONFIG_FILE_PATH)

    # load the specification path if it is provided
    if spec_path != None:
        spec_path = Path(spec_path)

        if path_error:
            typer.secho(
                f'Loading the specification file failed with "{ERRORS[path_error]}"',
                fg=typer.colors.RED,
            )

        # load up the cfg 
        config_parser['General']['spec_path'] = str(spec_path)

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

def load_app(cfg_path, spec_path = None, testing = False) -> None:
    """Loads the application given a CFG path.
    Args:
        path (String): Path to the CFG file.
    Raises:
        typer.Exit: When CFG loading is unsuccesful. 
    """    
    app_init_error = init_app(cfg_path, spec_path)
    if app_init_error:
        if not testing:
            typer.secho(
                f'Loading files failed with "{ERRORS[app_init_error]}"',
                fg=typer.colors.RED,
            )
        raise typer.Exit(1)
    else:
        if not testing:
            typer.secho(f"Initialisation successful!\n\t The cfg path is " + cfg_path, 
                        fg=typer.colors.GREEN)
            if spec_path != None:
                typer.secho(f"\t The language specification path is " + cfg_path, 
                        fg=typer.colors.GREEN)

def _set_parsetable(cfg) -> int:
    if not cfg.parsetable_calculated:
    # reset cfg structures before we begin if needed
        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        if not cfg.follow_set_calculated:
            cfg.reset_follow_set()

        if not cfg.is_ambiguous:
            # initialise parsetable
            cfg.setup_parsetable()

            # calculate parsetable
            code = cfg.calculate_parsetable()
        else:
            code = AMBIGUOUS_ERROR
        return code
    return SUCCESS
    
def _show_parsetable(cfg) -> None:
    """Displays the calculated parse table. 

    Args:
        cfg (ContextFreeGrammar): CFG for which the parse table is to be calculated.
    """    
    code = _set_parsetable(cfg)
    if code == SUCCESS:
        cfg.parsetable.print_parse_table()
    return code

def handle_input(inp, cfg, spec) -> None:
    """Handles user input by performing commands or otherwise parsing using the default method, LL(1)

    Args:
      inp (String): User input. 
      cfg (ContextFreeGrammar): ContextFreeGrammar Object based on loaded CFG.     
    """    
    if inp.strip()[0] == "\\":
        _process_command(inp, cfg, spec)
    else:
        code = _init_parsing_ll1(inp.strip(), cfg, spec)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()

def _init_parsing_ll1_via_cmd(inp, cfg, spec) -> int:
    """Initialises LL(1) parsing via the command \\ll1 <input>

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object

    Returns:
        int: _description_
    """    
    config = inp.strip()[4:7].strip()
    # parse \ll1 \v <input>
    if config == "\\v":
        to_parse = inp.strip()[7:].strip()
        if to_parse == "":
            error.ERR_no_input_given()
        else:
            if to_parse == "":
                error.ERR_no_input_given()
            else:
                config.configure_output_file_name(config.LL1_PARSING, to_parse)
                with m.tempconfig(config.OUTPUT_CONFIG):
                    animation = anim.ManimParseTree()
                    animation.setup_manim(to_parse, cfg, spec)
                    animation.render()       
    else:
        # parse \ll1 <input>
        _init_parsing_ll1(inp[4:].strip(), cfg, spec)
    return SUCCESS

def _init_parsing_ll1(inp, cfg, spec) -> int:
    """Initialise parsing using LL(1) by associating the CFG with its own LL(1) Parser object.

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object
    
    Returns:
        int: Status code
    """    
    # calculate the parse table if it has not yet been done so
    code = SUCCESS
    if not cfg.parsetable_calculated:
        code = _set_parsetable(cfg)

    if code == SUCCESS:
        # set up the cfg parser 
        code = _set_cfg_parser_ll1(inp, cfg, spec)

        # parse the input
        if code == SUCCESS:
            if inp == cfg.parser_ll1.inp:
                inp = ""
            cfg.parser_ll1.parse_ll1(cfg.start_symbol, inp)
        return SUCCESS
    return code
            
def _set_cfg_parser_ll1(inp, cfg, spec) -> int:
    """Initialises a new ParserLL1 object if it has not been initialised in this app session yet.

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object    Args:

    Returns:
        int: Status code
    """    
    code = SUCCESS
    if not cfg.is_parser_ll1_set_up:
        code = cfg.set_parser_ll1(p.ParserLL1(inp, cfg, spec))
    return code

def _prepare_to_parse(cfg):
        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        if not cfg.follow_set_calculated:
            cfg.reset_follow_set()

        if not cfg.is_ambiguous:
            if not cfg.parsetable_calculated:
                cfg.setup_parsetable()
                cfg.calculate_parsetable()
            return SUCCESS
        else:
            return AMBIGUOUS_ERROR

def _init_parsing_vis_shortcut(inp, cfg, spec) -> int:
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
        config.configure_output_file_name(config.LL1_PARSING, to_parse)
        with m.tempconfig(config.OUTPUT_CONFIG):
            animation = anim.ManimParseTree()
            animation.setup_manim(to_parse, cfg, spec)
            animation.render()       
    return SUCCESS

def _process_command(inp, cfg, spec) -> None:
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
        dsl_tool.main()

    elif inp == "\\show first" or inp == "\\fs":
        cfg.show_first_set()
    
    elif inp == "\\vis first" or inp == "\\vfs":
        if cfg.first_set_calculated:
            cfg.reset_first_set(calculate_again = False)
            cfg.first_set_calculated = False

        config.configure_output_file_name(config.FIRST_SET)
        with m.tempconfig(config.OUTPUT_CONFIG):
            animation = anim.ManimFirstSet()
            animation.setup_manim(cfg)
            animation.render()
      
    elif inp == "\\show follow" or inp == "\\fw":
        if not cfg.first_set_calculated:
            cfg.reset_first_set()
            cfg.first_set_calculated = True

        cfg.show_follow_set()
        
    elif inp == "\\vis follow" or inp == "\\vfw":
        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        # reset the follow set to be visualised again
        if cfg.follow_set_calculated:
            cfg.reset_follow_set(calculate_again = False)
            cfg.follow_set_calculated = False

        config.configure_output_file_name(config.FOLLOW_SET)
        with m.tempconfig(config.OUTPUT_CONFIG):
            animation = anim.ManimFollowSet()
            animation.setup_manim(cfg)
            animation.render()

    elif inp == "\\show parsetable" or inp == "\\pt":
        code = _show_parsetable(cfg)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()

    elif inp == "\\vis parsetable" or inp == "\\vpt":
        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        if not cfg.follow_set_calculated:
            cfg.reset_follow_set()

        if not cfg.is_ambiguous:
            if cfg.parsetable_calculated:
                # re-initialise parsetable
                cfg.setup_parsetable()
            
            config.OUTPUT_CONFIG["output_file"] = "Parsetable"
            config.configure_output_file_name(config.PARSETABLE)
            with m.tempconfig(config.OUTPUT_CONFIG):
                animation = anim.ManimParseTable()
                animation.setup_manim(cfg)
                animation.render()
        else:
            error.ERR_ambiguous_grammar()

    # elif inp == "\\l":
    #     new_path = typer.prompt("New path to CFG")
    #     load_app(new_path)
    #     # TODO reload CFG structure
      
    elif inp == "\\show cfg" or inp == "\\cfg":
        cfg.show_contents()

    elif inp == "\\show spec" or inp == "\\spec":
        if spec != None:
            spec.show_contents()
        else:
            display_helper.fail_secho("No specification provided.")

    elif inp.strip()[0:2] == "\\c":
        config.edit_config(inp.strip()[2:].strip())

    elif inp[0:4] == "\\ll1":
        code = _prepare_to_parse(cfg)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()
        else:
            _init_parsing_ll1_via_cmd(inp, cfg, spec)

    elif inp[0:2] == "\\v":
        code = _prepare_to_parse(cfg)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()
        else:
            _init_parsing_vis_shortcut(inp, cfg, spec)
    
    else:
        display_helper.fail_secho('Invalid command')



