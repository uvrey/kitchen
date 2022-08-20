""" Contains functions for displaying information to the console. """
# kitchen/display.py

import typer
import anytree
from kitchen.helpers import sounds, config
import pandas as pd

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
    """Helper function to echo an informative message. 

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
        fg = typer.colors.YELLOW
    ) 

def highlight_error(s):
    if s == "Error" :
        return ['background-color: red']
    else:
        return ['background-color: white']

def show_config_opts():
    info_secho("Options:\n\t Quality: -q <high | med | low>\n\t Preview: -p <y | n>\n\t Narration: -n <y / n>")

def show_tokens(tokens):
    for t in tokens:
        structure_secho("Token < Type: " + t.type + ", Value: " + t.value + " >")

def pretty_print_dict(dict):
    """Prints a nicely-formatted dictionary.

    Args:
        dict (Dictionary): Dictionary to be formatted.
    """    
    structure_secho("\n".join("{}\t{}".format(k, v) for k, v in dict.items()))

def pretty_print_config_settings(output_config, narr):
    """Displays the

    Args:
        config (_type_): _description_
    """    
    if narr == sounds.NARR: narr_setting = True
    else: narr_setting = False

    structure_secho("\tQuality: " + output_config["quality"])
    structure_secho("\tPreview: " + str(output_config["preview"]))
    structure_secho("\tAnimation Theme: " + config.get_theme_name())
    structure_secho("\tNarration: " + str(narr_setting))

def print_welcome():
    """Helper function to print the welcome screen.
    """    
    info_secho(
        "Welcome to Kitchen\n"+
        "type \\m for the menu\n")

def print_menu():
    """Helper function to print the application menu.
    """    
    cmds = [("quit", "q", "Exit app"), 
            ("config", "c", "Configure animation settings"), 
            ("show cfg", "cfg", "Display CFG"), 
            ("show spec", "spec", "Display language specification"), 
            ("dsl tool", "dsl", "Open DSL tool"), 
            ("show first", "fs", "Display first set"), 
            ("vis first", "vfs", "Visualise first set calculation"), 
            ("show follow", "fw", "Display follow set"), 
            ("vis follow", "vfw", "Visualise follow set calculation"), 
            ("show parsetable", "pt", "Display parse table"), 
            ("vis parsetable", "vpt", "Visualise parse table calculation"), 
            ("ll1 <input>", "<input>", "Show LL(1) parse tree"), 
            ("ll1 v <input>", "v <input>", "Visualise LL(1) parse tree \
                construction")]
        
    df= pd.DataFrame(data=cmds,  columns = ["Command", "Shortcut", "Detail"])
    info_secho(df.to_markdown(index=False))

def print_parsetree(root):
        """Helper function to print the parse tree

        Args:
            root (_type_): _description_
        """        
        for pre, fill, node in anytree.RenderTree(root):
            structure_secho("%s%s" % (pre, node.id))

def to_tex(item):
    tex_item = item.replace(r'$', r'\$')
    tex_item = tex_item.replace(r'\varepsilon', r'$\varepsilon$').replace(r'#', r'$\varepsilon$').replace("\\subseteq", "$\\subseteq$").replace("->", "$\\to$").replace("(", "$($").replace(")", "$)$")
    return tex_item

def to_math_tex(item):
    tex_item = item.replace(r'$', r'\$').replace("#", r'\varepsilon').replace("->", "\\to")
    return tex_item