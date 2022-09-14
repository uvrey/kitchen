""" Creates the Kitchen CLI"""
# kitchen/cli.py

import typer
from typing import Optional

from kitchen import (
    __app_name__,
     __version__, 
     SUCCESS, 
     ERROR,
     ERRORS
)

from kitchen.backend import (
  context_free_grammar as cfg, 
  cli_helper
  )

from kitchen.helpers import (
    display,
    sounds,
    lang_spec,
    config,
    error
)

from dslmodule.dsltool import (
     dsltool as dsl
)

app = typer.Typer()

def _version_callback(value: bool) -> None:
    """Callback to display the version of the application

    Args:
        value (bool): Version setting.

    Raises:
        typer.Exit: Exits the app once version has been displayed.
    """    
    if value:
        display.general_secho(f"{__app_name__} v{__version__}")
        raise typer.Exit()

def get_cfg() -> cfg.ContextFreeGrammar:
    """Helper function to obtain the created cfg from the config path

    Raises:
        typer.Exit: Closes the app session if the configuration file is 
        not found.
        typer.Exit: Closes the app session if the CFG file path is not found. 

    Returns:
        cfg.ContextFreeGrammar: ContextFreeGrammar object associated with 
        the given CFG.
    """    
    if config.CONFIG_FILE_PATH.exists():
        cfg_path = cfg.get_cfg_path(config.CONFIG_FILE_PATH)
    else:
        display.fail_secho(
            'Config file not found. Please run "kitchen init"',
        )
        raise typer.Exit(1)

    if cfg_path.exists():
        return cfg.ContextFreeGrammar(cfg_path)
    else:
        display.fail_secho('CFG not found. Please run "kitchen init" first')
        raise typer.Exit(1)

def _check_cfg(cfg) -> None:
    """Helper function to report issues with the CFG contents.

    Args:
        cfg (ContextFreeGrammar): CFG Object.

    Raises:
        typer.Abort: Aborts when CFG is invalid.
    """  
    try:
        if cfg.prods in ERRORS:
            display.fail_secho('"CFG file invalid with "{ERRORS[cfg.prods]}"')
            raise typer.Abort()
    except:
        pass

@app.command()
def init(
     cfg_path: str = typer.Option(
            ...,
            "--cfg-path",
            "-cfg",
            prompt="Please provide the path to your CFG",
            ),
     spec_path: Optional[str] = typer.Argument(None)
) -> None:
    """Initializes the configuration files.
    Args:
        cfg_path (str): Path to the CFG file.
    """
    cli_helper.load_app(cfg_path, spec_path)

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
    config.init_tree_png_dir()
    config.init_config()

    cfg = get_cfg()
    spec = lang_spec.get_spec(cfg)

    if spec == None:
        display.info_secho("Note:\tNo language specification has been " +
            "provided, so the given \n\tinput will be interpreted as " +
                "tokens directly.")

    display.success_secho("CFG loaded successfully.\n")

    display.print_welcome()
    while (True):
        input = typer.prompt("Input")
        cli_helper.handle_input(input, cfg, spec)

@app.command(name="dsl-tool")
def init_dsl() -> None:
    """This starts the tool using `python3 -m kitchen dsl-tool`
    """    
    spec = lang_spec.get_spec_path(config.CONFIG_FILE_PATH, True)
    if spec == None:
        display.fail_secho("No Language Specification provided.\n"+
        "Please re-initialise Kitchen with this file to use the DSL Tool.")
    else:
        dsl.main (spec)

@app.command(name="show-cfg")
def show_cfg() -> None:
    """Displays the contents of the given CFG file.
    """    
    cfg = get_cfg()
    _check_cfg(cfg)
    display.general_secho(cfg.cfg_contents)

""" Helper functions for testing """
@app.command(name = "test-fs")
def find_fs() -> None:
    """Tests the First Set.
    """    
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.show_first_set_testing()

@app.command(name = "test-fw")
def find_fw() -> None:
    """Tests the Follow Set.
    """    
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.reset_first_set()
    cfg.show_follow_set_testing()

@app.command(name = "test-pt")
def find_pt() -> None:
    """Tests the Parsing Table.
    """    
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.reset_first_set()
    cfg.reset_follow_set()
    if not cfg.is_ambiguous:
        # initialise parsetable
        code = cfg.setup_parsetable()
        # calculate parsetable
        code = cfg.calculate_parsetable()
        if code != ERROR:
            cfg.parsetable.print_parse_table_testing()
    else:
        error.ERR_ambiguous_grammar(testing = True)

@app.command(name = "test-ll1")
def find_ll1(  
    inp: str = typer.Option(
            ...,
            "--input",
            "-i",
            prompt="Please an input to be parsed",
            )) -> None:
    """Tests LL(1) Parsing

    Args:
        inp (str, optional): Input String. Defaults to typer.
        Option( ..., "--input", "-i", prompt="Please an input to be parsed", ).

    Returns:
        int: Status Code
    """            
    cfg = get_cfg()
    _check_cfg(cfg)
    cfg.reset_first_set()
    cfg.reset_follow_set()

    if not cfg.parsetable_calculated:
        cli_helper._set_parsetable(cfg)

    # sets up the cfg parser with no spec (testing token streams)
    code = cli_helper._set_cfg_parser_ll1(inp, cfg, None)

    # parses the input
    if code == SUCCESS:
        cfg.parser_ll1.parse_ll1(cfg.start_symbol, inp, testing=True)
    else:
        typer.echo("Problem setting up parser.")
    return SUCCESS

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Shows the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    """Displays application options.

    Args:
        version (Optional[bool], optional): Version option. 
        Defaults to typer.Option( None, "--version", "-v",
         help="Show the application's version and exit.", 
         callback=_version_callback, is_eager=True, ).
    """
    return

