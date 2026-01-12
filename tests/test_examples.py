# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import inspect
import os
from pathlib import Path
from typing import Callable

import jupytext
import pytest
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat.v4 import new_code_cell

pytestmark = pytest.mark.integration
IPYTHONDIR = str(Path(__file__).parent.parent) + "/.ipython"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

env = os.environ.copy()
env["PLOTLY_RENDERER"] = "json"


def test_examples(example_script: tuple[Path, Callable]):
    example_path, test_method = example_script
    os.environ["IPYTHONDIR"] = IPYTHONDIR
    ep = ExecutePreprocessor()

    notebook = jupytext.read(example_path)
    if test_method is not None:
        test_method_source = inspect.getsource(test_method)
        notebook.cells.append(
            new_code_cell(
                source=f"{test_method_source}\n\n{test_method.__name__}()"
            )
        )
    ep.preprocess(notebook, {"metadata": {"path": str(example_path.parent)}})

