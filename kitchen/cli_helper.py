""" Configuration for the application """

import configparser
from pathlib import Path
import typer

from kitchen import (
    CFG_WRITE_ERROR, DIR_ERROR, ERRORS, FILE_LOADING_ERROR, FILE_LOADING_EXISTS_ERROR, FILE_LOADING_NONE_ERROR, FILE_LOADING_DIR_ERROR, SUCCESS, __app_name__
)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

def init_app(cfg_path: str) -> int:
    """Initialize the application configuration file."""
    config_code = _init_config_file()
    if config_code != SUCCESS:
        return config_code
    cfg_code = _create_cfg_path(cfg_path)
    if cfg_code != SUCCESS:
        return cfg_code
    return SUCCESS

def _init_config_file() -> int:
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
    # check for valid paths
    for path in paths:
        if path is None:
           return FILE_LOADING_NONE_ERROR
        elif path.is_dir():
            return FILE_LOADING_DIR_ERROR
        elif not path.exists():
            return FILE_LOADING_EXISTS_ERROR
        return SUCCESS

""" Functions for the Kitchen environment """

# Helper function to print the welcome
def print_welcome():
    typer.echo(
        "\n -----------------------------------------------------------------------\n" +
        "\t\t\tWelcome to Kitchen\n" +
        " -----------------------------------------------------------------------\n" +
        "type \\m for the menu\n\n")


# Helper function to print the app menu
def _print_menu():
    typer.echo(
        " -----------------------------------------------------------------------")
    typer.echo(
        " COMMAND\t\tSHORTCUT\tDETAILS\n" +
        " -----------------------------------------------------------------------\n" +
        " \\menu \t\t\t\m\t\t Display menu\n" +
        " \\config \t\t\\c\t\t Configure animation settings\n" +
        " \\quit \t\t\t\\q\t\t Exit app\n\n"

        " \\load <cfg path> \t\\l <path>\t Load new CFG\n" +
        " \\show cfg \t\t\\cfg\t\t Displays the current CFG\n\n" +

        " \\dsl \t\t\t\t\t Launches the DSL design tool\n\n" +
        " \\firstset\t\t\\gfs\t\t Generates first set animation\n" +
        " \\show first\t\t\\fs\t\t Displays the first set\n" +
        " \\followset\t\t\\gfw\t\t Generates follow set animation\n" +
        " \\show follow\t\t\\fw\t\t Displays the follow set\n\n" +
        " \\show parsetable\t\\pt\t\t Displays the LL(1) parse table\n" +
        " \\show parsestructures\t\\ptss\t\t Shows the LL(1) parse table structures\n" +
        " \\ll1 <input> \t\t\t\t [Default] Parse input with LL(1)\n\n" +
        " \\lalr <input> \t\t\t\t Parse input with LALR\n\n"
    )
    typer.echo(
        " ------------------------------------------------------------------------")

def load_app(path):
    app_init_error = init_app(path)
    if app_init_error:
        typer.secho(
            f'Loading files failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"Re-initialisation successful! The new cfg path is " + path, 
                    fg=typer.colors.GREEN)

def handle_input(inp, cfg):
    if inp.strip()[0] == "\\":
        _process_command(inp, cfg)
    else:
        pass

def _process_command(inp, cfg):
    if inp == "\\m":
        _print_menu()
    elif inp == "\\q":
        raise typer.Exit()
    elif inp == "\\dsl":
        # TODO start DSL tool
        pass

    elif inp == "\\show firstset" or inp == "\\fs":
        cfg.show_first_set()

    elif inp == "\\followset" or inp == "\gfw":
        pass
      
    elif inp == "\\show follow" or inp == "\\fw":
        pass     
    elif inp == "\\show parse table" or inp == "\pt":
        pass
    elif inp == "\\parsetable" or inp == "\\vpt":
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
        # config = inp.strip()[4:7].strip()
        # if config == "\\v":
        #     to_parse = inp.strip()[7:].strip()
        #     if to_parse == "":
        #         ERR_no_input_given()
        #     else:
        #         kitchen.generate_parse_ll1(to_parse)
        # else:
        #     kitchen.parse_ll1(inp[4:].strip())
        pass

    elif inp[0:2] == "\\v":
        # to_parse = inp.strip()[2:].strip()
        # if to_parse == "":
        #     ERR_no_input_given()
        # else:
        #     kitchen.generate_parse_ll1(to_parse)
        pass
    
    else:
        typer.secho(f'Invalid command', fg=typer.colors.RED)


