""" Displays and handles error messages. """
# kitchen/helpers/error.py

import typer
import manim as m

from kitchen import SUCCESS

from kitchen.helpers import (
    config as c, 
    display, 
    sounds
)

def ERR_non_terminal_format(line, t):
    """Displays error when the non-terminal is in the wrong format.

    Args:
        line (int): Line number.
        t (str): Token.

    Raises:
        typer.Exit: Exits the application.
    """    
    g_err = ERR_get_general_error(line)
    typer.echo(g_err + ": Given non-terminal ("+t +
               ") in incorrect format (must be uppercase)")
    raise typer.Exit()

def ERR_no_regex(line, t):
    """Displays error when a token has no specification in the input
       when a spec has been provided.

    Args:
        line (int): Line number.
        t (str): Token.

    Raises:
        typer.Exit: Exits the application.
    """    
    g_err = ERR_get_general_error(line)
    typer.echo(g_err + ": Found a token '" + t +
               "' in the CFG but it has no regex specification.")
    raise typer.Exit()

def ERR_get_general_error(line):
    """Displays general error.

    Args:
        line (int): Line number of error.

    Returns:
        typer.Style: Formatted string.
    """    
    return typer.style("Error (line " + str(line) + ")", fg=typer.colors.WHITE,
        bg=typer.colors.RED)

def ERR_input_too_long():
    """Displays error when provided input is too long.
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Input too long (Maximum 10 strings permitted).")

def ERR_left_recursion_detected():
    """Displays error when a CFG contains left recursion.
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Left recursion detected- check your CFG!")

def ERR_unexpected_grammar_form():
    """Displays error when CFG format is invalid.

    Raises:
        typer.Exit: Exits the application.
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Unexpected form detected - check your CFG!")
    raise typer.Abort()

def ERR_key_not_given_in_CFG(p):
    """Displays an error when a referenced key is not in the CFG spec.

    Args:
        p (str): Production.

    Raises:
        typer.Exit: Exits the application.
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Production for [" + p + "] not found - check your CFG!")
    raise typer.Exit()

def ERR_cfg_loading_error():
    """Displays an error when the CFG cannot load.

    Raises:
        typer.Exit: Exits the application.
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Problem loading CFG.")
    raise typer.Exit()

def ERR_too_many_productions_ll1(nt, t):
    """Displays error when there is a conflict in the parsing table.

    Args:
        nt (str): Non-terminal (row).
        t (str): Terminal (column).
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " When building the parsing table, [" + nt + ", " + t +
               "] contains more than one production - this CFG is not \
                feasible to parse with LL(1).")

def ERR_parsing_error(root = None, detail=""):
    """Displays a parsing error.

    Args:
        root (Node, optional): Root node of the parse tree. Defaults to None.
        detail (str, optional): Detail message. Defaults to "".
    """    
    if detail != "":
        detail_msg = "" + detail
    else:
        detail_msg = detail
    err = typer.style("Error:", fg= typer.colors.WHITE, bg=typer.colors.RED)
    pt_state = typer.style("\nCurrent state of parse tree:", 
        fg=typer.colors.RED)
    typer.echo(err + " Parsing failed. " + detail_msg + pt_state)
    
    if root != None:
        display.print_parsetree(root)

def ERR_no_input_given():
    """Displays error for when no parsing input is given. 
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " No input provided.")

def ERR_ambiguous_grammar():
    """Displays an error when the grammar is ambiguous.
    """    
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    msg_str = (err + "\t The provided grammar contains ambiguity." +
               "\n\t This means that for some production S -> A | B," +
               " the same terminal t may be derived by A and B.\n\t From "+
               "this, we can't generate an LL(1) parsing table/ apply LL(1)"+
               " parsing to it.")
    typer.echo(msg_str)

def ERR_manim_parsing_error(scene, msg=[], script = ""):
    """Visualise the parsing error in Manim. 

    Args:
        scene (Scene): Scene to be animated. 
        msg (list, optional): Message to be displayed. Defaults to [].
        script (str, optional): Narration script. Defaults to "".

    Returns:
        int: Status code.
    """    
    err_msg = m.Tex("Parsing Error", color = m.RED)

    if msg != []:
        msg_group = m.VGroup()

        for ms in msg:
            msg_txt = m.Tex(display.to_tex(ms), color=c.get_opp_col())
            msg_group.add(msg_txt)
        msg_group.arrange(m.DOWN)
        
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=c.get_theme_col(), 
        fill_opacity=0.9)

        scene.play(
            m.FadeIn(rect),
        )

        # generate voiceover
        if script != "":
            sounds.narrate(script, scene)

        scene.play(
            m.Write(msg_group),
        )

        scene.wait()

        scene.play(
            m.FadeOut(msg_group),
            m.FadeOut(rect),
        )
    return SUCCESS