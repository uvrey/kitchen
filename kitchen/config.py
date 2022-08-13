from kitchen import (display_helper, sounds)

OUTPUT_CONFIG = None

def init_config():
    global OUTPUT_CONFIG
    OUTPUT_CONFIG = {"quality": "medium_quality", "preview": True, "output_file": ""}

def _set_quality(inp) -> bool:
    global OUTPUT_CONFIG
    qs = ["low_quality", "medium_quality", "high_quality"]
    opts = ['low', 'med', 'high']
    try:
        q_index = inp.index("-q")
        if inp[q_index + 1] not in opts:
            display_helper.fail_secho("\t Options: -q <high | med | low>")
        else:
            OUTPUT_CONFIG["quality"] = qs[opts.index(inp[q_index + 1])]
            display_helper.success_secho("Success: set 'quality' to '" + OUTPUT_CONFIG["quality"] + "'\n")
            return True
    except:
        return False

def _set_preview(inp):
    global OUTPUT_CONFIG
    ps = ['True', 'False']
    opts = ['y', 'n']
    try:
        p_index = inp.index("-p")
        if inp[p_index + 1] not in opts:
            display_helper.fail_secho("\t Options: -p <y | n>")
        else:
            OUTPUT_CONFIG["preview"] = ps[opts.index(inp[p_index + 1])]
            display_helper.success_secho("Success: set 'preview' to '" + OUTPUT_CONFIG["preview"] + "'\n")
            return True
    except:
        return False   

def _set_narration(inp):
    global OUTPUT_CONFIG
    opts = ["y", "n"]
    ns = [True, False]
    try:
        n_index = inp.index("-n")
        if inp[n_index + 1] in opts:
            narr = ns[opts.index(inp[n_index + 1])]
            if narr:
                sounds.set_config(sounds.NARR)
            else:
                sounds.set_config(sounds.NO_NARR)
            display_helper.success_secho("Success: set 'narration' to '" + str(narr) + "'\n")
            return True
    except:
        return False   

def _adjust_settings(inp):
    qcode = _set_quality(inp)
    pcode = _set_preview(inp)
    ncode = _set_narration(inp)
    if not (qcode or pcode or ncode):
        display_helper.fail_secho("Invalid configuration.\n")
    return


def _show_config():
    global OUTPUT_CONFIG
    display_helper.info_secho("Current configuration settings:")
    display_helper.pretty_print_config_settings(OUTPUT_CONFIG, sounds.get_config())
    display_helper.show_config_opts()

def edit_config(inp):
    code = False
    if inp != "":
        split_inp = inp.split(" ")
        for i in split_inp:
            i = i.strip() 
        code = _adjust_settings(split_inp)
    else:
        _show_config()
    return code