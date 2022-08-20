from kitchen import (
        SUCCESS, 
        DARK, 
        LIGHT, 
        __app_name__, 
        FILE_LOADING_ERROR, 
        DIR_ERROR,
        FILE_LOADING_NONE_ERROR,
        CFG_WRITE_ERROR,
        FILE_LOADING_DIR_ERROR,
        FILE_LOADING_EXISTS_ERROR,
        ERRORS
    )
from kitchen.helpers import (sounds, display, config)
from datetime import datetime
import manim as m
from pathlib import Path
import typer
import configparser

OUTPUT_CONFIG = None
# set theme to dark by default
THEME = DARK

(
    FOLLOW_SET,
    FIRST_SET,
    PARSETABLE,
    LL1_PARSING,
) = range(4)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
PARTIALS_PATH = ""

def init_config_file() -> int:
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

# Helper function to validate that the given cfg path is valid
def validate_path(paths):
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

def create_paths(cfg_path: str, spec_path = None) -> int:
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
    path_error = validate_path([cfg_path])

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


def init_config():
    global OUTPUT_CONFIG
    OUTPUT_CONFIG = {"quality": "medium_quality", "preview": True, 'flush_cache': True, "output_file": '', 'background_color': m.BLACK}

def set_theme(tm):
    global THEME, OUTPUT_CONFIG
    THEME = tm
    if tm == DARK:
        OUTPUT_CONFIG["background_color"] = m.BLACK
    else:
        OUTPUT_CONFIG["background_color"] = m.WHITE

def opp_col():
    if config.get_theme() == DARK:
        return m.WHITE
    else:
        return m.BLACK

def theme_col():
    if THEME == LIGHT:
        return m.WHITE
    else:
        return m.BLACK

def get_theme():
    return THEME

def get_theme_name():
    if THEME == LIGHT:
        return "light"
    else:
        return "dark " 

def edit_config(inp):
    code = False
    if inp != "":
        split_inp = inp.split(" ")
        for i in split_inp:
            i = i.strip() 
        code = _adjust_settings(split_inp)
    else:
        _show_config()
    return code

def get_time():
    now = datetime.now()
    return now.strftime("%d-%m_%H-%M-%S")

def configure_output_file_name(file_type, inp = ""):
    global OUTPUT_CONFIG
    file_name = ""
    if file_type == LL1_PARSING and inp != "":
        file_name = inp[0:5] + "_ParsingLL1_" + get_time()
    elif file_type == FOLLOW_SET:
        file_name = "FollowSet_" + get_time()
    elif file_type == FIRST_SET:
        file_name = "FirstSet_" + get_time()
    elif file_type == PARSETABLE:
        file_name = "ParseTable_" + get_time()
    
    # if clear name given, set new output file name
    if file_name != "":
        OUTPUT_CONFIG["output_file"] = file_name
    return SUCCESS
    
def _set_quality(inp) -> bool:
    global OUTPUT_CONFIG
    qs = ["low_quality", "medium_quality", "high_quality"]
    opts = ['low', 'med', 'high']
    try:
        q_index = inp.index("-q")
        if inp[q_index + 1] not in opts:
            display.fail_secho("\t Options: -q <high | med | low>")
        else:
            OUTPUT_CONFIG["quality"] = qs[opts.index(inp[q_index + 1])]
            display.success_secho("Success: set 'quality' to '" + OUTPUT_CONFIG["quality"] + "'\n")
            return True
    except:
        return False

def _set_theme(inp) -> bool:
    global OUTPUT_CONFIG
    global THEME
    ts = [DARK, LIGHT]
    opts = ['dark', 'light']
    try:
        t_index = inp.index("-t")
        if inp[t_index + 1] not in opts:
            display.fail_secho("\t Options: -t <dark | light>")
        else:
            set_theme(ts[opts.index(inp[t_index + 1])])
            display.success_secho("Success: set 'theme' to '" + inp[t_index + 1] + "'\n")
            return True
    except:
        return False

def _set_preview(inp):
    global OUTPUT_CONFIG
    ps = ['True', 'False']
    opts = ['y', 'n']
    try:
        p_index = inp.index("-p")
        if inp[p_index + 1] not in opts:
            display.fail_secho("\t Options: -p <y | n>")
        else:
            OUTPUT_CONFIG["preview"] = ps[opts.index(inp[p_index + 1])]
            display.success_secho("Success: set 'preview' to '" + OUTPUT_CONFIG["preview"] + "'\n")
            return True
    except:
        return False   

def _set_narration(inp):
    global OUTPUT_CONFIG
    opts = ["y", "n"]
    ns = [True, False]
    try:
        n_index = inp.index("-n")
        if inp[n_index + 1] in opts:
            narr = ns[opts.index(inp[n_index + 1])]
            if narr:
                sounds.set_config(sounds.NARR)
            else:
                sounds.set_config(sounds.NO_NARR)
            display.success_secho("Success: set 'narration' to '" + str(narr) + "'\n")
            return True
        else:
            display.fail_secho("\t Options: -n <y | n>")          
    except:
        return False   

def _adjust_settings(inp):
    qcode = _set_quality(inp)
    pcode = _set_preview(inp)
    ncode = _set_narration(inp)
    tcode = _set_theme(inp)
    if not (qcode or pcode or ncode or tcode):
        display.fail_secho("Invalid configuration.\n")
    return

def _show_config():
    global OUTPUT_CONFIG
    display.info_secho("Current configuration settings:")
    display.pretty_print_config_settings(OUTPUT_CONFIG, sounds.get_config())
    display.show_config_opts()

