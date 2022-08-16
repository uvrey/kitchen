""" Creates the Kitchen CLI"""
# kitchen/cli.py
from sre_constants import SUCCESS
import typer
from pathlib import Path
from typing import Optional
from kitchen import (
    __app_name__,
     __version__, 
     ERRORS, 
     SUCCESS, 
     cli_helper, 
     context_free_grammar as cfg, 
     display_helper,
     sounds,
     ERROR,
     config)

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
    pass
    #typer.echo(cfg.prods)  
    # TODO fix
    # if cfg.prods in ERRORS:
    #     display_helper.fail_secho('"CFG file invalid with "{ERRORS[cfg.prods]}"')
    #     raise typer.Abort()

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


@app.command(name="init-tests")
def init_tests(
     cfg_path: str = typer.Option(
            ...,
            "--cfg-path",
            "-cfg",
            prompt="Please provide the path to your CFG",
            ),
) -> int:
    """Initializes the configuration files within a testing context.

    Args:
        cfg_path (str): Path to the CFG file.
    """
    code = cli_helper.load_app(cfg_path, testing=True)
    if code== SUCCESS:
        return code
    else:
        return ERROR

@app.command(name="run")
def run() -> None:
    """Application driver.
    """    
    # set configuration options and initialise narration directory
    sounds.set_config(sounds.NARR)
    sounds.init_narr_dir()
    config.init_config()

    display_helper.print_welcome()
    cfg = get_cfg()
    display_helper.success_secho("CFG loaded successfully.")
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

""" Helper functions for testing """
@app.command(name = "test-fs")
def find_fs() -> None:
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.show_first_set_testing()


@app.command(name = "test-fw")
def find_fw() -> None:
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.reset_first_set()
    cfg.show_follow_set_testing()

@app.command(name = "test-pt")
def find_pt() -> None:
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.reset_first_set()
    cfg.reset_follow_set()

    # initialise parsetable
    cfg.setup_parsetable()

    # calculate parsetable
    code = cfg.calculate_parsetable()
    cfg.parsetable.print_parse_table_testing()

# TODO ADD more tests here
@app.command(name = "test-ll1")
def find_ll1(  
    inp: str = typer.Option(
            ...,
            "--input",
            "-i",
            prompt="Please an input to be parsed",
            )) -> None:
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.reset_first_set()
    cfg.reset_follow_set()

    if not cfg.parsetable_calculated:
        cli_helper._set_parsetable(cfg)

    # set up the cfg parser 
    code = cli_helper._set_cfg_parser_ll1(inp, cfg)

    # parse the input
    if code == SUCCESS:
        cfg.parser_ll1.parse_ll1(cfg.start_symbol, inp, testing=True)
    else:
        typer.echo("problem setting up parser")
    return SUCCESS


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

