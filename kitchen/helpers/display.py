""" Contains functions for displaying information to the console. """
# kitchen/helpers/display.py

from distutils.log import info
from turtle import heading
import typer
import anytree
import pandas as pd

from kitchen.helpers import (
        sounds, 
        config
    )

def info_secho(msg):
    """Helper function to echo an informative message. 

    Args:
        msg (str): Message to be shown.
    """    
    typer.secho(
        f'{msg}',
        fg = typer.colors.BLUE
    ) 

def general_secho(msg):
    """Helper function to echo a general message. 

    Args:
        msg (str): Message to be shown.
    """    
    typer.secho(
        f'{msg}',
        fg = typer.colors.WHITE
    ) 

def success_secho(msg):
    """Helper function to echo a message when an action has succeeded.

    Args:
        msg (str): Message to be shown.
    """    
    typer.secho(
        f'{msg}',
        fg = typer.colors.GREEN
    ) 

def fail_secho(msg):
    """Helper function to echo a message when an action has failed.

    Args:
        msg (str): Message to be shown.
    """    
    typer.secho(
        f'{msg}',
        fg = typer.colors.RED
    ) 

def structure_secho(msg):
    """Helper function to print the components of a data structure.

    Args:
        msg (str): Message to be shown.
    """    
    typer.secho(
        f'{msg}',
        fg = typer.colors.CYAN
    ) 

def highlight_error(s):
    """Highlights the background of a string.

    Args:
        s (str): Input string.

    Returns:
        list: Background style specification.
    """    
    if s == "Error" :
        return ['background-color: red']
    else:
        return ['background-color: white']

def show_config_opts():
    """Shows the configuration options.
    """    
    opts_str = ("Options:\n\tQuality: \t \\c -q high | med | low\n\t" +
                "Preview:\t \\c -p y | n\n\tAnimation Theme: \\c -t dark | light\n\t" +
                "Narration:\t \\c -n y | n")
    info_secho(opts_str)

def show_tokens(tokens):
    """Displays the tokens.

    Args:
        tokens (list): Token list to be shown.
    """    
    for t in tokens:
        if t != None:
            structure_secho("Token < Type: " + t.type + ", Value: " + t.value + 
            " >")
        else:
            structure_secho("None")


def pretty_print_dict(dict):
    """Prints a nicely-formatted dictionary.

    Args:
        dict (Dictionary): Dictionary to be formatted.
    """    
    structure_secho("\n".join("{}\t{}".format(k, v) for k, v in dict.items()))

def pretty_print_config_settings(output_config, narr):
    """Displays the configuration settings.

    Args:
        config (list): Output configuration.
    """    
    if narr == sounds.NARR: narr_setting = True
    else: narr_setting = False

    structure_secho("\tQuality: " + output_config["quality"])
    structure_secho("\tPreview: " + str(output_config["preview"]))
    structure_secho("\tAnimation Theme: " + config.get_theme_name())
    structure_secho("\tNarration: " + str(narr_setting))

def print_set(set, name=""):
    """Prints the First or Follow Set in the correct format.

    Args:
        set (dict): First or Follow Set.
        name (str, optional): Name of set. Defaults to "".
    """    
    printable_set = {}
    for key in set.keys():
        printable_set[key] = ", ".join(set[key])
    df= pd.DataFrame(data=printable_set,  columns = set.keys(), index = \
        [name])
    structure_secho(df.transpose().to_markdown())

def print_welcome():
    """Helper function to print the welcome screen.
    """    
    info_secho(
        "Welcome to Kitchen\n"+
        "If it's your first time here, type \\tut for the tutorial,\n"+
        "or \\m for the menu!\n")

def print_menu(help = False):
    """Helper function to print the application menu.
    """    
    app_cmds = [("Exit app", "\\quit", "\\q"), 
            ("Configure animation settings", "\\config", "\\c"), 
            ("Start the tutorial", "\\tutorial", "\\tut"), 
            ("Display Context-Free Grammar", "\\show cfg", "\\cfg"), 
            ("Display Language Specification", "\\show spec", "\\spec")]

    dsl = [("Open DSL tool", "\\dsl tool", "\\dsl")]

    calcs=  [("Display First Set", "\\show first", "\\fs"), 
            ("Display Follow Set", "\\show follow", "\\fw"), 
            ("Display Parse Table", "\\show parsetable", "\\pt"),
            ("Display LL(1) Parse Tree", "\\ll1 <input>", "<input>"),
            ("Export LL(1) Parse Tree as .png", "\\tree <input>", ""),
            ("Display Symbol Table", "\\sem <input>", "")]
    
    anims = [("Visualise Parsing Table calculation", "\\vis parsetable", "\\vpt"), 
             ("Visualise First Set calculation", "\\vis first", "\\vfs"), 
            ("Visualise Follow Set calculation", "\\vis follow", "\\vfw"), 
            ("Visualise LL(1) Parse Tree "+
                "construction", "\\ll1 v <input>", "\\v <input>"),
            ("Visualise Semantic Analysis", "\\vsem <input>", "")]
    
    if help:
        success_secho("\nWith these commands, you can see the contents of files"+
        "\nand adjust the animation settings.\nFor example, you can change "+
        "\nthe video's resolution (high: 1080p, medium:720p, low: 480p)")

    structure_secho("Use these commands to see what files are loaded\n" +
    " and adjust the animation settings.")
    df= pd.DataFrame(data=app_cmds,  columns = ["Detail", "Command", "Shortcut"])
    info_secho(df.to_markdown(index=False))

    if help: 
        success_secho("\nThis command opens up another tool.")

    structure_secho("\nUse this command to open the domain-specific language" +
    " design tool.")
    df= pd.DataFrame(data=dsl,  columns = ["Detail", "Command", "Shortcut"])
    info_secho(df.to_markdown(index=False))

    if help:
        success_secho("\nWhen you are practicing problems, this is the place to be.")

    structure_secho("\nUse these commands to check your calculations")
    df= pd.DataFrame(data=calcs,  columns = ["Detail", "Command", "Shortcut"])
    info_secho(df.to_markdown(index=False))

    if help:
        success_secho("If you need a bit more explanation, generate it here!"+
        "\nThese videos live in the 'kitchen\\media\\videos' directory.")
    structure_secho("\nUse these commands to generate an explanation video.")
    df= pd.DataFrame(data=anims,  columns = ["Detail", "Command", "Shortcut"])
    info_secho(df.to_markdown(index=False))

def print_parsetree(root):
        """Helper function to print the parse tree.

        Args:
            root (Node): Root node of the parse tree.
        """        
        for pre, fill, node in anytree.RenderTree(root):
            structure_secho("%s%s" % (pre, node.id))

def to_tex(item: str):
    """Converts a string to Tex format.

    Args:
        item (str): Item to be converted to Tex.

    Returns:
        str: Tex item.
    """    
    tex_item = item.replace(r'$', r'\$')
    tex_item = tex_item.replace(r'\varepsilon', r'$\varepsilon$')\
        .replace(r'#', r'$\varepsilon$').replace("\\subseteq", \
        "$\\subseteq$").replace("->", "$\\to$").replace("(", "$($")\
            .replace(")", "$)$")
    return tex_item

def to_math_tex(item):
    """Converts a string to MathTex format.

    Args:
        item (str): Item to be converted to MathTex.

    Returns:
        str: MathTex item.
    """    
    tex_item = item.replace(r'$', r'\$').replace("#", r'\varepsilon')\
    .replace("->", "\\to")
    return tex_item


def display_tutorial():
    success_secho("Welcome to the tutorial!\nType \\q to quit\n")
    done = False
    success_secho("Kitchen uses several commands.\n" +
                    "You can see these at any time by typing \\m")
    input = typer.prompt("Try this now")
    if _compare_input("\\m", input):
        print_menu(help = True)
        success_secho("Great job!\nScroll up to see information about the menu.")
        success_secho("(You can come back to this tutorial anytime using \\tut)")

def _compare_input(expected, input):
    if input == expected:
        return True
    elif input == "\\q":
        return -1
    else:
        success_secho("Hmm.. that wasn't quite right. Try again?")
        return 0