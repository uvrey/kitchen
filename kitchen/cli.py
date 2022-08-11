""" Creates the Kitchen CLI"""
# kitchen/cli.py
import typer
from pathlib import Path
from typing import Optional
from kitchen import (
    __app_name__,
     __version__, 
     ERRORS, 
     cli_helper, 
     context_free_grammar as cfg, 
     display_helper,
     sounds)

app = typer.Typer()

def _version_callback(value: bool) -> None:
    """Callback to display the version of the application

    Args:
        value (bool): Version setting.

    Raises:
        typer.Exit: Exits the app once version has been displayed.
    """    
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

def get_cfg() -> cfg.ContextFreeGrammar:
    """Helper function to obtain the created cfg from the config path

    Raises:
        typer.Exit: Closes the app session if the configuration file is not found.
        typer.Exit: Closes the app session if the CFG file path is not found. 

    Returns:
        cfg.ContextFreeGrammar: ContextFreeGrammar object associated with the given CFG.
    """    
    if cli_helper.CONFIG_FILE_PATH.exists():
        cfg_path = cfg.get_cfg_path(cli_helper.CONFIG_FILE_PATH)
    else:
        display_helper.fail_secho(
            'Config file not found. Please run "kitchen init"',
        )
        raise typer.Exit(1)

    if cfg_path.exists():
        return cfg.ContextFreeGrammar(cfg_path)
    else:
        display_helper.fail_secho('CFG not found. Please run "kitchen init" first')
        raise typer.Exit(1)

def _check_cfg(cfg) -> None:
    """Helper function to report issues with the CFG contents.

    Args:
        cfg (ContextFreeGrammar): CFG Object.

    Raises:
        typer.Abort: Aborts when CFG is invalid.
    """    
    if cfg.prods in ERRORS:
        display_helper.fail_secho('"CFG file invalid with "{ERRORS[cfg.prods]}"')
        raise typer.Abort()

@app.command()
def init(
     cfg_path: str = typer.Option(
            ...,
            "--cfg-path",
            "-cfg",
            prompt="Please provide the path to your CFG",
            ),
) -> None:
    """Initializes the configuration files.

    Args:
        cfg_path (str): Path to the CFG file.
    """
    cli_helper.load_app(cfg_path)

@app.command(name="run")
def run() -> None:
    """Application driver.
    """    
    # set configuration options
    sounds.set_config(sounds.NARR)

    display_helper.info_secho("config settings:\nNarration: Yes")
    display_helper.print_welcome()
    cfg = get_cfg()
    while (True):
        input = typer.prompt("Input")
        cli_helper.handle_input(input, cfg)

@app.command(name="show-cfg")
def show_cfg() -> None:
    """Displays the contents of the given CFG file.
    """    
    cfg = get_cfg()
    _check_cfg(cfg)
    typer.echo(cfg.cfg_contents)

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    """Displays application options.

    Args:
        version (Optional[bool], optional): Version option. Defaults to typer.Option( None, "--version", "-v", help="Show the application's version and exit.", callback=_version_callback, is_eager=True, ).
    """
    return

