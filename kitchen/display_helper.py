import typer

def info_secho(msg):
    """Helper function to echo an informative message. 

    Args:
        msg (str): Message to be shown.
    """    
    typer.secho(
        f'{msg}',
        fg = typer.colors.BLUE
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


def pretty_print_dict(dict):
    """Prints a nicely-formatted dictionary.

    Args:
        dict (Dictionary): Dictionary to be formatted.
    """    
    typer.secho("\n".join("{}\t{}".format(k, v) for k, v in dict.items()), fg=typer.colors.YELLOW)
