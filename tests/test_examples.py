import pytest
import subprocess
import pathlib
import os

pytestmark = pytest.mark.integration

env = os.environ.copy()
env["IPYTHONDIR"] = str(pathlib.Path("../.ipython").absolute())


def test_examples(example_script: pathlib.Path):
    p = subprocess.Popen(
        ["ipython", str(example_script)], cwd=example_script.parent, env=env  # str() needed in py <= 3.7
    )
    p.wait()
    assert p.returncode == 0
