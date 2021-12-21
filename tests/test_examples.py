import pytest
import sys
import subprocess
import pathlib
import backoff

pytestmark = pytest.mark.integration


@backoff.on_exception(backoff.constant,
                      AssertionError,
                      max_tries=5)
def test_examples(example_script: pathlib.Path):
    p = subprocess.Popen([sys.executable, str(example_script)], cwd=example_script.parent)  # str() needed in py <= 3.7
    p.wait()
    assert p.returncode == 0
