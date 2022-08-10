""" Contains functions for displaying information to the console. """
# kitchen/display_helper.py

import typer
import anytree

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

def pretty_print_dict(dict):
    """Prints a nicely-formatted dictionary.

    Args:
        dict (Dictionary): Dictionary to be formatted.
    """    
    structure_secho("\n".join("{}\t{}".format(k, v) for k, v in dict.items()))

def print_welcome():
    """Helper function to print the welcome screen.
    """    
    info_secho(
        "Welcome to Kitchen\n"+
        "type \\m for the menu\n")

def print_menu():
    """Helper function to print the application menu.
    """    
    info_secho(" COMMAND\t\tSHORTCUT\tDETAILS\n")
    general_secho(
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

def print_parsetree(root):
        """Helper function to print the parse tree

        Args:
            root (_type_): _description_
        """        
        for pre, fill, node in anytree.RenderTree(root):
            structure_secho("%s%s" % (pre, node.name))