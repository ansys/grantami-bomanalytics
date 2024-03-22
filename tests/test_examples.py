import os
from pathlib import Path
import subprocess
import sys

import pytest

pytestmark = pytest.mark.integration
IPYTHONDIR = str(Path(__file__).parent.parent) + "/.ipython"

env = os.environ.copy()
env["PLOTLY_RENDERER"] = "json"


def test_examples(example_script: Path):
    p = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "IPython",
            "--ipython-dir",
            IPYTHONDIR,
            example_script,
        ],
        cwd=example_script.parent,
        env=env,
    )
    p.wait()
    assert p.returncode == 0
