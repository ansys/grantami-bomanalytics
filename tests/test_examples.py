import pytest
import sys
import subprocess
import pathlib

pytestmark = pytest.mark.integration


def test_examples(example_script: pathlib.Path):
    p = subprocess.Popen([sys.executable, example_script], cwd=example_script.parent)
    p.wait()
    assert p.returncode == 0
