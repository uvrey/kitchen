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
    app_init_error = cli_helper.init_app(cfg_path)
    if app_init_error:
        typer.secho(
            f'Loading files failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"Initialisation successful! The cfg path is " + cfg_path, 
                    fg=typer.colors.GREEN)


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
        typer.echo("cfg path found: " + str(cfg_path))
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
    if cfg.prods in ERRORS:
        typer.secho(
            f'"CFG file invalid with "{ERRORS[cfg.prods]}"',
            fg=typer.colors.RED,
        )
    else:
        typer.echo(cfg.cfg_contents)

# set up app
def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

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
        

