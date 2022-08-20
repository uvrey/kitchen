# tests/test_kitchen.py
""" DO NOT EDIT """
from typer.testing import CliRunner
import os
import pytest
from pathlib import Path
from kitchen import __app_name__, __version__, app

runner = CliRunner()

def test_version():
    result = runner.invoke(app.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def sample_path():
    return ".\\samples\\example_cfgs\\"


""" Test initialisation and loading of CFGs """
@pytest.mark.parametrize("sample, out", [
    ("cfg.txt", ""),
    ("cfg_101010.txt", "Loading the CFG file failed with \"file does not exist\""),
    ("cfg_2.txt", ""),
    ("cfgXT.txt", "Loading the CFG file failed with \"file does not exist\""),
    ("cfg_4.txt", ""),
])

def test_init(sample, out, sample_path):
    result = runner.invoke(app.app, ["init",  "-cfg", sample_path + sample])
    assert out in result.stdout

