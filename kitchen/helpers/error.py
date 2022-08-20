# Program for printing error messages
from kitchen.helpers import display_helper, config as c, sounds
from kitchen import SUCCESS
import typer
import manim as m

def ERR_non_terminal_format(line, t):
    g_err = ERR_get_general_error(line)
    typer.echo(g_err + ": Given non-terminal ("+t +
               ") in incorrect format (must be uppercase)")
    raise typer.Abort()

def ERR_no_regex(line, t):
    g_err = ERR_get_general_error(line)
    typer.echo(g_err + ": Found a token '" + t +
               "' in the CFG but it has no regex specification.")
    raise typer.Abort()

def ERR_get_general_error(line):
    return typer.style("Error (line " + str(line) + ")", fg=typer.colors.WHITE, bg=typer.colors.RED)

def ERR_input_too_long():
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Input too long (Maximum 10 strings permitted).")

def ERR_left_recursion_detected():
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Left recursion detected- check your CFG!")

def ERR_unexpected_grammar_form():
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Unexpected form detected - check your CFG!")
    raise typer.Abort()

def ERR_key_not_given_in_CFG(p):
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Production for [" + p + "] not found - check your CFG!")
    raise typer.Abort()

def ERR_cfg_loading_error():
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " Problem loading CFG.")
    raise typer.Abort()

def ERR_too_many_productions_ll1(nt, t):
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " When building the parsing table, [" + nt + ", " + t +
               "] contains more than one production - this CFG is not feasible to parse with LL(1).")

def ERR_parsing_error(root = None, detail=""):
    if detail != "":
        detail_msg = "" + detail
    else:
        detail_msg = detail
    err = typer.style("Error:", fg= typer.colors.WHITE, bg=typer.colors.RED)
    pt_state = typer.style("\nCurrent state of parse tree:", fg=typer.colors.RED)
    typer.echo(err + " Parsing failed. " + detail_msg + pt_state)
    
    if root != None:
        display_helper.print_parsetree(root)

def ERR_no_input_given():
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + " No input provided.")

def ERR_ambiguous_grammar():
    err = typer.style("Error:", fg=typer.colors.WHITE, bg=typer.colors.RED)
    typer.echo(err + "\t The provided grammar contains ambiguity. \n\t This means that for some production S -> A | B, the same terminal t may be derived by A and B.\n\t From this, we can't generate an LL(1) parsing table/ apply LL(1) parsing to it.")

def ERR_manim_parsing_error(scene, msg=[], raw_msg = ""):
    err_msg = m.Tex("Parsing Error", color = m.RED)

    if msg != []:
        msg_group = m.VGroup()

        for ms in msg:
            msg_txt = m.Tex(display_helper.to_tex(ms), color=c.opp_col())
            msg_group.add(msg_txt)
        msg_group.arrange(m.DOWN)
        
        # create fading area
        rect = m.Rectangle(width=20, height=10, color=c.theme_col(), fill_opacity=0.9)

        scene.play(
            m.FadeIn(rect),
        )

        # generate voiceover
        if raw_msg != "":
            sounds.narrate(raw_msg, scene)

        scene.play(
            m.Write(msg_group),
        )

        scene.wait()

        scene.play(
            m.FadeOut(msg_group),
            m.FadeOut(rect),
        )
    return SUCCESS