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

import jupytext
import pytest
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat.v4 import new_code_cell

pytestmark = pytest.mark.integration
IPYTHONDIR = str(Path(__file__).parent.parent) + "/.ipython"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

env = os.environ.copy()
env["PLOTLY_RENDERER"] = "json"


def example_0_basic_usage():
    assert len(result.impacted_substances) == 12
    assert len(result.messages) == 0
    # Expected cells with outputs
    assert set(Out.keys()) == set([2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

def example_4_1_sustainability():
    assert len(records) == 50


@pytest.mark.parametrize(
    ["example_script_", "test_method"],
    [
        pytest.param("0_Basic_usage.py", example_0_basic_usage),
        pytest.param("4_Sustainability/4-1_Sustainability.py", example_4_1_sustainability, marks=pytest.mark.onlyabove(mi_version=(27, 2))),
    ],
)
def test_examples(example_script_: str, test_method):
    os.environ["IPYTHONDIR"] = IPYTHONDIR
    ep = ExecutePreprocessor()
    example_script_path = EXAMPLES_DIR / example_script_
    notebook = jupytext.read(example_script_path)
    test_method_source = inspect.getsource(test_method)
    notebook.cells.append(
        new_code_cell(
            source=f"{test_method_source}\n\n{test_method.__name__}()"
        )
    )
    ep.preprocess(notebook, {"metadata": {"path": str(example_script_path.parent)}})

