""" Top-level        cfg_heading.next_to(keys, m.UP/232# # # # 
        all_elemeall_elements.arrange_in_grid()rows = 1, buff = 1.45
        # 
        #  package for Kitchen """
# kitchen/__init__.py
from sqlite3 import DateFromTicks
import manim as m
import typer
from pathlib import Path

__app_name__= "kitchen"
__version__ = "0.1.0"

RE_TERMINAL = '[a-z][a-z]*|$|#|\+|-|/|\*|\(|\)|,'
RE_NONTERMINAL = '[A-Z][A-Z]*'
RE_PRODUCTION = '[A-Z][A-Z]*|[a-z][a-z]*|$|#|\+|-|/|\*|\(|\)|,'


TEXT_SCALE = 1
CFG_SCALE_HEIGHT = 6.25*m.config["frame_height"]/10
CFG_SCALE_WIDTH = 0.8*m.config["frame_width"]
CFG_SCALE = 0.7
COLOURS = [m.BLUE_B, m.TEAL_B, m.GREEN_B, m.YELLOW_B, m.GOLD_B,
                     m.RED_B, m.MAROON_B, m.PURPLE_A, m.LIGHT_PINK, m.LIGHT_BROWN]

(
    DARK,
    LIGHT
) = range(2)


(
    SUCCESS,
    DIR_ERROR,
    CFG_FILE_ERROR,
    FILE_LOADING_NONE_ERROR,
    FILE_LOADING_EXISTS_ERROR,
    FILE_LOADING_DIR_ERROR,
    FILE_LOADING_ERROR,
    NO_FILE_ERROR,
    CFG_ERROR_NT_FORMAT,
    REGEX_ERROR_NO_TOKEN,
    CFG_WRITE_ERROR,
    REGEX_WRITE_ERROR,
    INPUT_TOO_LONG,
    ERROR,
    PARSING_ERROR,
    SOUND_ERROR
) = range(16)

ERRORS = {
    DIR_ERROR: "config directory error",
    CFG_FILE_ERROR: "cfg file not found - check your path",
    FILE_LOADING_ERROR: "error loading regex yaml or cfg file",
    FILE_LOADING_DIR_ERROR: "directory given, but file expected",
    FILE_LOADING_EXISTS_ERROR: "file does not exist",
    FILE_LOADING_NONE_ERROR: "no path provided",
    CFG_ERROR_NT_FORMAT: "cfg error, non-terminal must be uppercase",
    REGEX_ERROR_NO_TOKEN: "token in cfg has no spec",
    REGEX_WRITE_ERROR: "error writing regex file to dir",
    CFG_WRITE_ERROR: "error writing cfg file to dir",
    INPUT_TOO_LONG: "input too long",
    SOUND_ERROR: "couldn't find sound or 'asset/sounds' folder"
}