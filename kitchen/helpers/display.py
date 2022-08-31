""" Contains functions for displaying information to the console. """
# kitchen/helpers/display.py

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
        "If it's your first time here, type \\m for the menu!\n")

def print_menu():
    """Helper function to print the application menu.
    """    
    app_cmds = [("Exit app", "\\quit", "\\q"), 
            ("Configure animation settings", "\\config", "\\c"), 
            ("Display context-free-grammar", "\\show cfg", "\\cfg"), 
            ("Display language specification", "\\show spec", "\\spec")]

    dsl = [("Open DSL tool", "\\dsl tool", "\\dsl")]

    calcs=  [("Display first set", "\\show first", "\\fs"), 
            ("Display follow set", "\\show follow", "\\fw"), 
            ("Display parse table", "\\show parsetable", "\\pt"),
            ("Display LL(1) parse tree", "\\ll1 <input>", "<input>")]
    
    anims = [("Visualise parse table calculation", "\\vis parsetable", "\\vpt"), 
             ("Visualise first set calculation", "\\vis first", "\\vfs"), 
            ("Visualise follow set calculation", "\\vis follow", "\\vfw"), 
            ("Visualise LL(1) parse tree "+
                "construction", "\\ll1 v <input>", "\\v <input>")]
    
    structure_secho("Use these commands to see what files are loaded\n" +
    " and adjust the animation settings.")
    df= pd.DataFrame(data=app_cmds,  columns = ["Detail", "Command", "Shortcut"])
    info_secho(df.to_markdown(index=False))

    structure_secho("\n\nUse this command to open the domain-specific language" +
    " design tool.")
    df= pd.DataFrame(data=dsl,  columns = ["Detail", "Command", "Shortcut"])
    info_secho(df.to_markdown(index=False))

    structure_secho("\n\nUse these commands to check your calculations")
    df= pd.DataFrame(data=calcs,  columns = ["Detail", "Command", "Shortcut"])
    info_secho(df.to_markdown(index=False))

    structure_secho("\n\nUse these commands to generate an explanation video.")
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