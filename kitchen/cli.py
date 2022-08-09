""" Creates the Kitchen CLI"""
# kitchen/cli.py
import typer
from pathlib import Path
from typing import Optional
from kitchen import __app_name__, __version__, ERRORS, cli_helper, context_free_grammar as cfg, driver, manim_driver
app = typer.Typer()

@app.command()
def init(
     cfg_path: str = typer.Option(
            ...,
            "--cfg-path",
            "-cfg",
            prompt="Please provide the path to your CFG",
            ),
) -> None:
    """Initialize the configuration files."""
    cli_helper.load_app(cfg_path)


""" helper function to obtain the created cfg from the config path """
def get_cfg() -> cfg.ContextFreeGrammar:
    if cli_helper.CONFIG_FILE_PATH.exists():
        cfg_path = cfg.get_cfg_path(cli_helper.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please run "kitchen init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if cfg_path.exists():
        return cfg.ContextFreeGrammar(cfg_path)
    else:
        typer.secho(
            'CFG not found. Please run "kitchen init" first',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

@app.command(name="show-cfg")
def show_cfg() -> None:
    cfg = get_cfg()
    _check_cfg(cfg)

# helper function to report issues with the CFG contents
def _check_cfg(cfg) -> None:
    if cfg.prods in ERRORS:
        typer.secho(
            f'"CFG file invalid with "{ERRORS[cfg.prods]}"',
            fg=typer.colors.RED,
        )
        raise typer.Abort()

# driver function for the application
@app.command(name="run")
def run() -> None:
    cli_helper.print_welcome()
    cfg = get_cfg()
    while (True):
        input = typer.prompt("Input")
        cli_helper.handle_input(input, cfg)

# callback to display the version of the application
def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

# helper menu to start the application
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
    return
        

