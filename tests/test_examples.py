from pathlib import Path
import subprocess
import sys

import pytest

pytestmark = pytest.mark.integration
IPYTHONDIR = str(Path(__file__).parent.parent) + "/.ipython"


def test_examples(example_script: Path):
    p = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "IPython",
            "--ipython-dir",
            str(IPYTHONDIR),  # str() needed in py <= 3.7
            str(example_script),  # str() needed in py <= 3.7
        ],
        cwd=example_script.parent,
    )
    p.wait()
    assert p.returncode == 0
