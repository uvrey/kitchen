""" Driver functions for the CLI application. """
# kitchen/backend/cli_helper.py

from pathlib import Path
import typer
import manim as m

from kitchen import (
    __app_name__,
    AMBIGUOUS_ERROR,
    ERRORS, 
    SUCCESS
)

from kitchen.helpers import (
    display,
    error, 
    config,
    lang_spec
)

from kitchen.backend import (
    parse_table as pt,
    parser as p,
    semantic as tc,
    context_free_grammar as cofg
)

from kitchen.manim import (
    m_first, 
    m_follow, 
    m_parse_table, 
    m_parser,
    m_semantic
)

from dslmodule.dsltool import (
     dsltool as dsl
)

def init_app(cfg_path: str, spec_path = None) -> int:
    """Initialises the application by creating its configuration file and
       CFG path.

    Args:
        cfg_path (str): CFG path.

    Returns:
        int: Status code.
    """    

    config_code = config.init_config_file()
    if config_code != SUCCESS:
        return config_code

    # create cfg path
    cfg_code = config.create_paths(cfg_path, spec_path)

    if cfg_code != SUCCESS:
        return cfg_code

    return SUCCESS

def load_app(cfg_path, spec_path = None, testing = False) -> None:
    """Loads the application's paths.

    Args:
        cfg_path (str): Path to the CFG file.
        spec_path (str, optional): Path to the spec file. Defaults to None.
        testing (bool, optional): Testing state. Defaults to False.

    Raises:
        typer.Exit: When CFG loading is unsuccesful. 
    """    

    app_init_error = init_app(cfg_path, spec_path)
    if app_init_error:
        if not testing:
            typer.secho(
                f'Loading files failed with "{ERRORS[app_init_error]}"',
                fg=typer.colors.RED,
            )
        raise typer.Exit(1)
    else:
        if not testing:
            # does preliminary checks on the loaded grammars.
            cfg = cofg.ContextFreeGrammar(Path(cfg_path))
            spec = lang_spec.get_spec(cfg)

            typer.secho(f"Initialisation successful!\n\t The cfg path is " + 
            cfg_path, fg=typer.colors.GREEN)
            if spec_path != None:
                typer.secho(f"\t The language specification path is " + 
                spec_path, fg=typer.colors.GREEN)

def _set_parsetable(cfg) -> int:
    """Sets the up and calculates the parsetable structures.

    Args:
        cfg (ContextFreeGrammar): Loaded CFG.

    Returns:
        int: Status code.
    """    

    if not cfg.parsetable_calculated:
    # reset cfg structures before we begin if needed
        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        if not cfg.follow_set_calculated:
            cfg.reset_follow_set()

        if not cfg.is_ambiguous:
            # initialise parsetable
            cfg.setup_parsetable()

            # calculate parsetable
            code = cfg.calculate_parsetable()
        else:
            code = AMBIGUOUS_ERROR
        return code
    return SUCCESS
    
def _show_parsetable(cfg) -> None:
    """Displays the calculated parse table. 

    Args:
        cfg (ContextFreeGrammar): CFG for which the parse table is to be 
        calculated.
    """    
    code = _set_parsetable(cfg)
    if code == SUCCESS:
        cfg.parsetable.print_parse_table()
    return code

def handle_input(inp, cfg, spec) -> None:
    """Handles user input by performing commands or otherwise parsing using 
    the default method, LL(1)

    Args:
      inp (String): User input. 
      cfg (ContextFreeGrammar): ContextFreeGrammar Object based on loaded CFG.     
    """    
    if inp.strip()[0] == "\\":
        _process_command(inp, cfg, spec)
    else:
        code = _init_parsing_ll1(inp.strip(), cfg, spec)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()

def _init_parsing_ll1_via_cmd(inp, cfg, spec) -> int:
    """Initialises LL(1) parsing via the command \ll1 <input>

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object

    Returns:
        int: _description_
    """    
    config = inp.strip()[4:7].strip()
    # parse \ll1 \v <input>
    if config == "\\v":
        to_parse = inp.strip()[7:].strip()
        if to_parse == "":
            error.ERR_no_input_given()
        else:
            if to_parse == "":
                error.ERR_no_input_given()
            else:
                config.configure_output_file_name(config.LL1_PARSING, to_parse)
                with m.tempconfig(config.OUTPUT_CONFIG):
                    animation = m_parser.MParseTree()
                    animation.setup_manim(to_parse, cfg, spec)
                    animation.render()       
    else:
        # parse \ll1 <input>
        _init_parsing_ll1(inp[4:].strip(), cfg, spec)
    return SUCCESS

def _init_parsing_ll1(inp, cfg, spec, semantic = False) -> int:
    """Initialises parsing using LL(1) by associating the CFG with its 
       own LL(1) Parser object.

    Args:
        inp (str): Input string to be parsed
        cfg (ContextFreeGrammar): ContextFreeGrammar object
    
    Returns:
        int: Status code
    """    
    # calculates the parse table if this has not yet been done 
    code = SUCCESS
    if not cfg.parsetable_calculated:
        code = _set_parsetable(cfg)

    if code == SUCCESS:
        # sets up the cfg parser 
        code = _set_cfg_parser_ll1(inp, cfg, spec)

        # parses the input
        if code == SUCCESS:
            if inp == cfg.parser_ll1.inp:
                inp = ""
            code = cfg.parser_ll1.parse_ll1(cfg.start_symbol, inp, semantic)
            return code
    return code
            
def _set_cfg_parser_ll1(inp, cfg, spec) -> int:
    """Initialises a new ParserLL1 object if it has not been initialised 
       in this app session yet.

    Args:
        inp (str): Input string to be parsed.
        cfg (ContextFreeGrammar): ContextFreeGrammar object.
        spec (Specification): Specification object.

    Returns:
        int: Status code
    """    
    code = SUCCESS
    if not cfg.is_parser_ll1_set_up:
        code = cfg.set_parser_ll1(p.ParserLL1(inp, cfg, spec))
    return code

def _prepare_to_parse(cfg):
    """Sets up the LL(1) parsing structures.

    Args:
        cfg (ContextFreeGrammar): Loaded CFG.

    Returns:
        int: Status code.
    """    
    if not cfg.first_set_calculated:
        cfg.reset_first_set()

    if not cfg.follow_set_calculated:
        cfg.reset_follow_set()

    if not cfg.is_ambiguous:
        if not cfg.parsetable_calculated:
            cfg.setup_parsetable()
            cfg.calculate_parsetable()
        return SUCCESS
    else:
        return AMBIGUOUS_ERROR

def _init_parsing_vis_shortcut(inp, cfg, spec) -> int:
    """Initialises the visualisation of LL(1) parsing on some input, 
       via the app shortcut '\\v <input>'.

    Args:
        inp (str): Input string

    Returns:
        int: Status code
    """    
    to_parse = inp.strip()[2:].strip()
    
    if to_parse == "":
        error.ERR_no_input_given()
    else:
        config.configure_output_file_name(config.LL1_PARSING, to_parse)
        with m.tempconfig(config.OUTPUT_CONFIG):
            animation = m_parser.MParseTree()
            animation.setup_manim(to_parse, cfg, spec)
            animation.render()       
    return SUCCESS

def _process_command(inp, cfg, spec) -> None:
    """Processes a command from the user.

    Args:
        inp (String): User input.
        cfg (ContextFreeGrammar): ContextFreeGrammar Object based on 
                                  loaded CFG.

    Raises:
        typer.Exit: Exits the application when the user requests this. 
    """   

    if inp == "\\m" or inp == "\\menu":
        display.print_menu()

    elif inp == "\\q" or inp == "\\quit":
        raise typer.Exit()

    elif inp == "\\tutorial" or inp == "\\tut":
        display.display_tutorial()

    elif inp == "\\dsl" or inp == "\\dsl tool":
        spec = lang_spec.get_spec_path(config.CONFIG_FILE_PATH, True)
        if spec == None:
            display.fail_secho("No Language Specification provided.\n"+
            "Please re-initialise Kitchen with this file to use the DSL Tool.")
        else:
            dsl.main (spec)

    elif inp == "\\show first" or inp == "\\fs":
        cfg.show_first_set()
    
    elif inp == "\\vis first" or inp == "\\vfs":
        if cfg.first_set_calculated:
            cfg.reset_first_set(calculate_again = False)
            cfg.first_set_calculated = False

        config.configure_output_file_name(config.FIRST_SET)
        with m.tempconfig(config.OUTPUT_CONFIG):
            animation = m_first.MFirstSet()
            animation.setup_manim(cfg)
            animation.render()
      
    elif inp == "\\show follow" or inp == "\\fw":
        if not cfg.first_set_calculated:
            cfg.reset_first_set()
            cfg.first_set_calculated = True

        cfg.show_follow_set()
        
    elif inp == "\\vis follow" or inp == "\\vfw":
        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        # reset the follow set to be visualised again
        if cfg.follow_set_calculated:
            cfg.reset_follow_set(calculate_again = False)
            cfg.follow_set_calculated = False

        config.configure_output_file_name(config.FOLLOW_SET)
        with m.tempconfig(config.OUTPUT_CONFIG):
            animation = m_follow.MFollowSet()
            animation.setup_manim(cfg)
            animation.render()

    elif inp == "\\show parsetable" or inp == "\\pt":
        code = _show_parsetable(cfg)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()

    elif inp == "\\vis parsetable" or inp == "\\vpt":
        if not cfg.first_set_calculated:
            cfg.reset_first_set()

        if not cfg.follow_set_calculated:
            cfg.reset_follow_set()

        if not cfg.is_ambiguous:
            if cfg.parsetable_calculated:
                # re-initialise parsetable
                cfg.setup_parsetable()
            
            config.OUTPUT_CONFIG["output_file"] = "Parsetable"
            config.configure_output_file_name(config.PARSETABLE)
            with m.tempconfig(config.OUTPUT_CONFIG):
                animation = m_parse_table.MParsingTable()
                animation.setup_manim(cfg)
                animation.render()
        else:
            error.ERR_ambiguous_grammar()

    elif inp == "\\semantic" or inp[0:4] == "\\sem":
        stripped = inp.strip()
        to_sem = stripped[4:]
        if to_sem == "":
            display.fail_secho("No input provided.")
        else:
            code = _prepare_to_parse(cfg)
            if code == AMBIGUOUS_ERROR:
                error.ERR_ambiguous_grammar()
            else:
                code = _init_parsing_ll1(to_sem, cfg, spec, semantic = True)
                if code == SUCCESS:
                    sem_analyser = tc.SemanticAnalyser(cfg, 
                    cfg.parser_ll1.root, to_sem)
                    sem_analyser.init_analysis()
                else:
                    display.fail_secho("Parsing failed. Cannot generate "+
                    "semantic analysis.\n(Have you provided a language spec?")

    elif inp[0:5] == "\\tree":
            stripped = inp.strip()
            to_sem = stripped[5:]
            if to_sem == "":
                display.fail_secho("No input provided.")
            else:
                code = _prepare_to_parse(cfg)
                if code == AMBIGUOUS_ERROR:
                    error.ERR_ambiguous_grammar()
                else:
                    code = _init_parsing_ll1(to_sem, cfg, spec, semantic = True)
                    if code == SUCCESS:
                        cfg.parser_ll1.export_tree()
                    else:
                        display.fail_secho("Parsing failed with code " + 
                        str(code)+ ".Cannot export tree as PNG.")

    elif inp[0:5] == "\\vsem":
        stripped = inp.strip()
        to_sem = stripped[5:]
        if to_sem == "":
            display.fail_secho("No input provided.")
        else:
            code = _prepare_to_parse(cfg)
            if code == AMBIGUOUS_ERROR:
                error.ERR_ambiguous_grammar()
            else:
                code = _init_parsing_ll1(to_sem, cfg, spec, semantic = True)
                if code == SUCCESS:
                    config.OUTPUT_CONFIG["output_file"] = "TypeCheck"
                    config.configure_output_file_name(config.TYPE_CHECK)
                    with m.tempconfig(config.OUTPUT_CONFIG):
                        sem_analyser = m_semantic.MSemanticAnalyser()
                        sem_analyser.setup_manim(cfg, 
                        cfg.parser_ll1.root, to_sem, spec)
                        sem_analyser.render()
                else:
                    display.fail_secho("Parsing failed. Cannot generate "+
                    "semantic analysis.\n(Have you provided a language spec?")
       
    elif inp == "\\show cfg" or inp == "\\cfg":
        cfg.show_contents()

    elif inp == "\\show spec" or inp == "\\spec":
        if spec != None:
            spec.show_contents()
        else:
            display.fail_secho("No specification provided.")

    elif inp.strip()[0:2] == "\\c" or inp == "\\config":
        if inp == "\\c":
            config.edit_config(inp.strip()[2:].strip())
        else:
            config.edit_config(inp.strip()[7:].strip())

    elif inp[0:4] == "\\ll1":
        code = _prepare_to_parse(cfg)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()
        else:
            _init_parsing_ll1_via_cmd(inp, cfg, spec)

    elif inp[0:2] == "\\v":
        code = _prepare_to_parse(cfg)
        if code == AMBIGUOUS_ERROR:
            error.ERR_ambiguous_grammar()
        else:
            _init_parsing_vis_shortcut(inp, cfg, spec)
    
    else:
        display.fail_secho('Invalid command')



