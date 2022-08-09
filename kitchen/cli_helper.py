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
           typer.echo("1")
           return FILE_LOADING_NONE_ERROR
        elif path.is_dir():
            typer.echo("2")
            return FILE_LOADING_DIR_ERROR
        elif not path.exists():
            typer.echo("3")
            return FILE_LOADING_EXISTS_ERROR
        return SUCCESS


# # Helper function to initialise loading up the CFG and showing progress to the user
# def _init_files(cfg_path, regex_path) -> int:
#     # validate and create the files
#     # _validate_path([cfg_path, regex_path])

#     # create the directory where the loaded files will be stored
#     code = _init_config_dir()
#     if code != SUCCESS:
#         return code

#     # create the files inside this directory based on supplied arguments
#     # code = _create_files(cfg_path, regex_path)
#     # if code != SUCCESS:
#     #     return code
#     return SUCCESS

#     # # load their contents
#     # try:
#     #     REGEX = yaml.load(open(regex_path), Loader=SafeLoader)
#     #     with open(cfg_path) as f:
#     #         _CFG_CONTENTS = cfg_path.read_text()
#     #         return SUCCESS
#     # except:
#     #     return FILE_LOADING_ERROR



# # configure the directory and contents
# def _init_config_dir() -> int:
#     try:
#         CONFIG_DIR_PATH.mkdir(exist_ok=True)
#     except OSError:
#         return DIR_ERROR
#     try:
#         CONFIG_CFG_PATH.touch(exist_ok=True)
#         CONFIG_REGEX_PATH.touch(exist_ok=True)
#         # TODO simon's config file here
#     except OSError:
#         return FILE_LOADING_ERROR
#     return SUCCESS

# # create the cfg file
# def _create_cfg(cfg_path: str) -> int:
#     # write the cfg file to the appropriate directory
#     config_cfg_parser = configparser.ConfigParser()
#     config_cfg_parser["General"] = {"cfg": cfg_path}
#     try:
#         with CONFIG_CFG_PATH.open("w") as file:
#             config_cfg_parser.write(file)
#     except OSError:
#         return CFG_WRITE_ERROR
    
# # create the regex file
# def _create_regex(regex_path: str) -> int:
#     # write the regex file to the same directory
#     config_regex_parser = configparser.ConfigParser()
#     config_regex_parser["General"] = {"regex": regex_path}
#     try:
#         with CONFIG_REGEX_PATH.open("w") as file:
#             config_regex_parser.write(file)
#     except OSError:
#         return REGEX_WRITE_ERROR
#     return SUCCESS


# # Helper function to print the app menu
# def print_menu():
#     typer.echo(
#         " -----------------------------------------------------------------------")
#     typer.echo(
#         " COMMAND\t\tSHORTCUT\tDETAILS\n" +
#         " -----------------------------------------------------------------------\n" +
#         " \\menu \t\t\t\m\t\t Display menu\n" +
#         " \\config \t\t\\c\t\t Configure animation settings\n" +
#         " \\quit \t\t\t\\q\t\t Exit app\n\n"

#         " \\load <cfg path> \t\\l <path>\t Load new CFG\n" +
#         " \\show cfg \t\t\\cfg\t\t Displays the current CFG\n\n" +

#         " \\dsl \t\t\t\t\t Launches the DSL design tool\n\n" +
#         " \\firstset\t\t\\gfs\t\t Generates first set animation\n" +
#         " \\show first\t\t\\fs\t\t Displays the first set\n" +
#         " \\followset\t\t\\gfw\t\t Generates follow set animation\n" +
#         " \\show follow\t\t\\fw\t\t Displays the follow set\n\n" +
#         " \\show parsetable\t\\pt\t\t Displays the LL(1) parse table\n" +
#         " \\show parsestructures\t\\ptss\t\t Shows the LL(1) parse table structures\n" +
#         " \\ll1 <input> \t\t\t\t [Default] Parse input with LL(1)\n\n" +
#         " \\lalr <input> \t\t\t\t Parse input with LALR\n\n"
#     )
#     typer.echo(
#         " ------------------------------------------------------------------------")



# # Helper function to handle user input
# def handle_input(inp):
#     if inp == "\\m":
#         print_menu()
#     elif inp == "\\q":
#         raise typer.Exit()
#     elif inp == "\\dsl":
#         # TODO start DSL tool
#         pass
#     elif inp == "\\firstset" or inp == "\gfs":
#         #kitchen.generate_first_set()
#         pass
#     elif inp == "\\followset" or inp == "\gfw":
#         # kitchen.generate_follow_set()
#         pass
#     elif inp == "\\show first" or inp == "\\fs":
#        #  kitchen.show_first_set()
#        pass
#     elif inp == "\\show follow" or inp == "\\fw":
#         # kitchen.show_follow_set()
#         pass
#     elif inp == "\\show parse table" or inp == "\pt":
#         # kitchen.show_parse_table()
#         pass
#     elif inp == "\\parsetable" or inp == "\\vpt":
#         # kitchen.generate_parse_table()
#         pass
#     elif inp == "\\show parse structures" or inp == "\ptss":
#         # kitchen.show_parse_structures()
#         pass
#     elif inp == "\\l":
#          new_path = typer.prompt("Path to CFG")
#          pass
#     elif inp == "\\show cfg" or inp == "\\cfg":
#          # kitchen.show_cfg()
#          pass
#     elif inp == "\\c":
#         typer.echo("Configuring animation settings")
#         pass
#     elif inp[0:4] == "\\ll1":
#         pass
#         # config = inp.strip()[4:7].strip()
#         # if config == "\\v":
#         #     to_parse = inp.strip()[7:].strip()
#         #     if to_parse == "":
#         #         error.ERR_no_input_given()
#         #     else:
#         #         kitchen.generate_parse_ll1(to_parse)
#         # else:
#         #     kitchen.parse_ll1(inp[4:].strip())
#     elif inp[0:2] == "\\v":
#         pass
#         # to_parse = inp.strip()[2:].strip()
#         # if to_parse == "":
#         #     error.ERR_no_input_given()
#         # else:
#         #     kitchen.generate_parse_ll1(to_parse)
#     else:
#         return True
#     return False

