# tests/test_kitchen.py

# tests/test_rptodo.py

from typer.testing import CliRunner
import os
import pytest
from pathlib import Path
from kitchen import __app_name__, __version__, cli, ERROR
import difflib

runner = CliRunner()

def test_always_passes():
    assert True

def is_palindrome(p):
    return True

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def sample_path():
    return ".\\samples\\cfgs\\"

@pytest.fixture
def fs_out_path():
    return ".\\samples\\fs\\"

""" Test initialisation and loading of CFGs """
@pytest.mark.parametrize("sample, out", [
    ("cfg.txt", ""),
    ("cfg_101010.txt", "Loading files failed with \"file does not exist\""),
    ("cfg_2.txt", ""),
    ("cfgXT.txt", "Loading files failed with \"file does not exist\""),
    ("cfg_4.txt", ""),
])

def test_init(sample, out, sample_path):
    result = runner.invoke(cli.app, ["init",  "-cfg", sample_path + sample])
    assert out in result.stdout

""" Test calculation of first sets on existing CFG files """
@pytest.mark.parametrize("sample_fs", [
    ("cfg.txt"),
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

def test_fs(sample_path, fs_out_path, sample_fs):
    """Tests the first set of a given input

    Args:
        sample_path (str): Path to samples directory
        sample_fs (str): Name of CFG file
        fs_out_path (str): Path to expected outputs directory
    """    
    runner.invoke(cli.app, ["init-tests",  "-cfg", sample_path + sample_fs])
    result = runner.invoke(cli.app, ["test-fs"])
    out_fs = get_contents(sample_fs, fs_out_path)
    show_differences(out_fs, result.stdout)
    assert out_fs in result.stdout

def get_contents(sample_fs, fs_out_path):
    """Gets the contents of the sample file to be compared to

    Args:
        sample_fs (str): Path to the file for the first set to be tested
        fs_out_path (str): Path to the expected outputs file

    Returns:
        str: contents of the expected output file corresponding to the first set to be tested
    """    
    filename = os.getcwd() + fs_out_path + sample_fs
    file = open(filename, 'r')
    return file.read()

def show_differences(out, result):
    print("Comparing:")
    print(out)
    print("and")
    print(result)
    print("__")
    for i,s in enumerate(difflib.ndiff(result, out)):
        if s[0]==' ': continue
        elif s[0]=='-':
            print(u'Delete "{}" from position {}'.format(s[-1],i))
        elif s[0]=='+':
            print(u'Add "{}" to position {}'.format(s[-1],i))    


# TODO follow set, parsing, pt tests