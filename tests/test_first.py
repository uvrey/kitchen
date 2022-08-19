# tests/test_first.py
""" DO NOT EDIT """
from typer.testing import CliRunner
import os
import pytest
from pathlib import Path
from kitchen import __app_name__, __version__, cli, ERROR

runner = CliRunner()

@pytest.fixture
def sample_path():
    return ".\\samples\\example_cfgs\\"

@pytest.fixture
def fs_out_path():
    return ".\\samples\\expected_fs\\"

""" Test calculation of first sets on existing CFG files """
@pytest.mark.parametrize("sample_cfg", [
    ("cfg.txt"),
    ("cfg_0.txt"),
    ("cfg_1.txt"),
    ("cfg_2.txt"),
    ("cfg_3.txt"),
    ("cfg_4.txt"),
    ("cfg_5.txt"),
    ("cfg_6.txt"),
    ("cfg_7.txt"),
    ("cfg_8.txt"),
    ("cfg_9.txt"),
    ("cfg_10.txt"),
])

def test_fs(sample_path, fs_out_path, sample_cfg):
    """Tests the first set of a given input

    Args:
        sample_path (str): Path to samples directory
        sample_cfg (str): Name of CFG file
        fs_out_path (str): Path to expected outputs directory
    """    
    runner.invoke(cli.app, ["init-tests",  "-cfg", sample_path + sample_cfg])
    result = runner.invoke(cli.app, ["test-fs"])
    out_fs = get_contents(sample_cfg, fs_out_path)
    show_differences(out_fs, result.stdout)
    assert out_fs in result.stdout

def get_contents(sample_cfg, fs_out_path):
    """Gets the contents of the sample file to be compared to

    Args:
        sample_fs (str): Path to the file for the first set to be tested
        fs_out_path (str): Path to the expected outputs file

    Returns:
        str: contents of the expected output file corresponding to the first set to be tested
    """    
    filename = os.getcwd() + fs_out_path + sample_cfg
    file = open(filename, 'r')
    return file.read()

def show_differences(out, result):
    print("Expected:")
    print(out)
    print("but got:")
    print(result)
    print("__")
