# tests/test_follow.py
""" DO NOT EDIT """
import difflib
from typer.testing import CliRunner
import os
import pytest
from pathlib import Path
from kitchen import __app_name__, __version__, app

runner = CliRunner()

@pytest.fixture
def sample_path():
    return ".\\samples\\example_cfgs\\"

@pytest.fixture
def ll1_out_path():
    return ".\\samples\\expected_ll1\\"

""" Test calculation of first sets on existing CFG files """
@pytest.mark.parametrize("sample_cfg, input_str", [
    ("cfg.txt", "c"),
    # ("cfg_1.txt"), # need memo
    # ("cfg_2.txt"), # issue here with follow(B) and done
    # ("cfg_3.txt"),
    # ("cfg_4.txt"),
    # ("cfg_5.txt"),
    # ("cfg_6.txt"),
    # ("cfg_7.txt"), 
    # ("cfg_8.txt"),
    # ("cfg_9.txt"), 
    # ("cfg_10.txt"), # issue here
    ("cfg_bla_simple_0.txt", "+ identifier"),
    ("cfg_bla_simple_1.txt", "identifier +"),
    ("cfg_bla_simple_2.txt", "identifier a identifier"),
    ("cfg_id_language.txt", "identifier = value identifier = value")
])

def test_pt(sample_path, ll1_out_path, sample_cfg, input_str):
    """Tests the first set of a given input

    Args:
        sample_path (str): Path to samples directory
        sample_cfg (str): Name of CFG file
        fs_out_path (str): Path to expected outputs directory
    """    
    runner.invoke(app.app, ["init-tests",  "-cfg", sample_path + sample_cfg])
    result = runner.invoke(app.app, ["test-ll1", "-i", input_str])
    out_fs = get_contents(sample_cfg, ll1_out_path)
    show_differences(out_fs, result.stdout)
    assert out_fs in result.stdout

def get_contents(sample_cfg, ll1_out_path):
    """Gets the contents of the sample file to be compared to

    Args:
        sample_fs (str): Path to the file for the first set to be tested
        fs_out_path (str): Path to the expected outputs file

    Returns:
        str: contents of the expected output file corresponding to the first set to be tested
    """    
    filename = os.getcwd() + ll1_out_path + sample_cfg
    file = open(filename, 'r')
    return file.read()

def show_differences(out, result):
    print("Expected:")
    print(out)
    print("but got:")
    print(result)
    print("__")

    for i,s in enumerate(difflib.ndiff(result, out)):
        if s[0]==' ': continue
        elif s[0]=='-':
            print(u'Delete "{}" from position {}'.format(s[-1],i))
        elif s[0]=='+':
            print(u'Add "{}" to position {}'.format(s[-1],i))    
