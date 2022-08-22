""" Sets up and handles application configuration settings. """
# kitchen/helpers/config.py

import configparser
from datetime import datetime
import manim as m
from pathlib import Path
import typer

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

from kitchen.helpers import sounds, display

OUTPUT_CONFIG = None
THEME = DARK

(
    FOLLOW_SET,
    FIRST_SET,
    PARSETABLE,
    LL1_PARSING,
) = range(4)

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"

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

def validate_path(paths: list) -> int:
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

    # loads the config parser
    config_parser = configparser.ConfigParser()
    config_parser['General'] = {}

    # sets up the default CFG and spec paths
    config_parser['General']['cfg_path'] = str(cfg_path)
    config_parser['General']['spec_path'] = ''

    # loads the specification path if it is provided
    if spec_path != None:
        spec_path = Path(spec_path)

        if path_error:
            typer.secho(
                f'Loading the specification file failed with \
                    "{ERRORS[path_error]}"',
                fg=typer.colors.RED,
            )

        # sets the specifications path
        config_parser['General']['spec_path'] = str(spec_path)

    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return CFG_WRITE_ERROR
    return SUCCESS

def init_config() -> None:
    """Initialises the default configuration settings.
    """    
    global OUTPUT_CONFIG
    OUTPUT_CONFIG = {"quality": "medium_quality", 
                    "preview": True, 
                    'flush_cache': True, 
                    "output_file": '', 
                    'background_color': m.BLACK,
                    'include_sound': True
                    }

def set_theme(tm: int) -> None:
    """Sets the animation theme.

    Args:
        tm (int): Theme code.
    """    
    global THEME, OUTPUT_CONFIG
    THEME = tm
    if tm == DARK:
        OUTPUT_CONFIG["background_color"] = m.BLACK
    else:
        OUTPUT_CONFIG["background_color"] = m.WHITE

def get_opp_col():
    """Retrieves the contrast colour of the current theme.

    Returns:
        Color: Manim Color.
    """    
    if _get_theme_code() == DARK:
        return m.WHITE
    else:
        return m.BLACK

def get_theme_col():
    """Retrieves the background colour of the given theme.

    Returns:
        Color: Manim Color.
    """    
    if THEME == LIGHT:
        return m.WHITE
    else:
        return m.BLACK

def get_theme_name() -> str:
    """Retrieves the name of the current theme.

    Returns:
        str: Theme name.
    """    
    if THEME == LIGHT:
        return "light"
    else:
        return "dark " 

def _get_theme_code()  -> int:
    """Retrieves the current theme code.

    Returns:
        int: Theme code.
    """    
    return THEME

def edit_config(inp: str) -> int:
    """Edits the configuration settings based on user preferences.

    Args:
        inp (str): User configuration selection.

    Returns:
        int: Status code.
    """    
    code = False
    if inp != "":
        split_inp = inp.split(" ")
        for i in split_inp:
            i = i.strip() 
        code = _adjust_settings(split_inp)
    else:
        _show_config()
    return code

def get_time() -> str:
    """Retrieves the current time, for setting unique video file names.

    Returns:
        str: Formatted time.
    """    
    now = datetime.now()
    return now.strftime("%d-%m_%H-%M-%S")

def configure_output_file_name(file_type: int, inp = "") -> None:
    """Sets unique file names for generated videos.

    Args:
        file_type (int): File type code.
        inp (str, optional): LL(1) Parsing input. Defaults to "".

    Returns:
        str: Unique file name.
    """    
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
    
def _set_quality(inp: str) -> bool:
    """Edits the video quality settings.

    Args:
        inp (str): User input.

    Returns:
        bool: Success status.
    """    
    global OUTPUT_CONFIG
    qs = ["low_quality", "medium_quality", "high_quality"]
    opts = ['low', 'med', 'high']
    try:
        q_index = inp.index("-q")
        if inp[q_index + 1] not in opts:
            display.fail_secho("\t Options: -q <high | med | low>")
        else:
            OUTPUT_CONFIG["quality"] = qs[opts.index(inp[q_index + 1])]
            display.success_secho("Success: set 'quality' to '" + 
            OUTPUT_CONFIG["quality"] + "'\n")
            return True
    except:
        return False

def _set_theme(inp: str) -> bool:
    """Edits the video theme settings.

    Args:
        inp (str): User input.

    Returns:
        bool: Success status.
    """    
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
            display.success_secho("Success: set 'theme' to '" + 
            inp[t_index + 1] + "'\n")
            return True
    except:
        return False

def _set_preview(inp: str) -> None:
    """Edits the video preview settings.

    Args:
        inp (str): User input.

    Returns:
        bool: Success status.
    """    
    global OUTPUT_CONFIG
    ps = ['True', 'False']
    opts = ['y', 'n']
    try:
        p_index = inp.index("-p")
        if inp[p_index + 1] not in opts:
            display.fail_secho("\t Options: -p <y | n>")
        else:
            OUTPUT_CONFIG["preview"] = ps[opts.index(inp[p_index + 1])]
            display.success_secho("Success: set 'preview' to '" + 
            OUTPUT_CONFIG["preview"] + "'\n")
            return True
    except:
        return False   

def _set_narration(inp: str) -> None:
    """Edits the video narration settings.

    Args:
        inp (str): User input.

    Returns:
        bool: Success status.
    """    
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
            display.success_secho("Success: set 'narration' to '" + 
            str(narr) + "'\n")
            return True
        else:
            display.fail_secho("\t Options: -n <y | n>")          
    except:
        return False   

def _adjust_settings(inp: str) -> None:
    """Handles all adjustments to the settings.

    Args:
        inp (str): User input.
    """    
    qcode = _set_quality(inp)
    pcode = _set_preview(inp)
    ncode = _set_narration(inp)
    tcode = _set_theme(inp)
    if not (qcode or pcode or ncode or tcode):
        display.fail_secho("Invalid configuration.\n")
    return

def _show_config() -> None:
    """Initialises display of configuration settings.
    """    
    global OUTPUT_CONFIG
    display.info_secho("Current configuration settings:")
    display.pretty_print_config_settings(OUTPUT_CONFIG, sounds.get_config())
    display.show_config_opts()

