# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

from collections import defaultdict
import os
import pathlib
from typing import List

import pytest
import requests_mock

from ansys.grantami.bomanalytics import Connection

from .common import (
    CUSTOM_TABLES,
    LICENSE_RESPONSE,
    _get_connection,
    get_mi_version,
    read_password,
    read_username,
    sl_url,
    write_password,
    write_username,
)


@pytest.fixture
def connection():
    return _get_connection(sl_url, read_username, read_password)


def _configure_connection_for_custom_db(_cxn):
    _cxn.set_database_details(
        database_key="MI_Restricted_Substances_Custom_Tables",
        **{pn: tn for pn, tn in CUSTOM_TABLES},
    )


@pytest.fixture
def connection_custom_db(connection):
    _configure_connection_for_custom_db(connection)
    return connection


@pytest.fixture(params=["default_db", "custom_db"])
def connection_with_db_variants(request):
    """Parameterized fixture: tests using this fixture will run multiple times, according to parameter values provided
    in the fixture decorator."""
    connection = _get_connection(sl_url, read_username, read_password)
    if request.param == "custom_db":
        _configure_connection_for_custom_db(connection)
    return connection


@pytest.fixture
def connection_write_custom_db():
    cxn = _get_connection(sl_url, write_username, write_password)
    _configure_connection_for_custom_db(cxn)
    return cxn


@pytest.fixture
def mock_connection(monkeypatch):
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, json=LICENSE_RESPONSE)
        connection = Connection(api_url=sl_url).with_anonymous().connect()
    return connection


def pytest_generate_tests(metafunc):
    """Dynamically discover all example .py files and add to the set of parameters for a test if that test uses the
    'example_script' fixture.
    """

    mi_version = get_mi_version()

    # If we don't have an MI version, we cannot contact an MI server. Example tests cannot run, so we might as well
    # return early.
    if mi_version is None:
        return

    skip_examples_for_version = defaultdict(set)
    skip_examples_for_version[(25, 1)] = {
        "3-2_Creating_an_XML_BoM.py",
        "4-1_BoM_Sustainability.py",
        "4-2_BoM_Sustainability_summary_phase_summary.py",
        "4-3_BoM_Sustainability_summary_transport.py",
        "4-4_BoM_Sustainability_summary_material.py",
        "4-5_BoM_Sustainability_summary_processes.py",
        "4-6_BoM_Sustainability_summary_hierarchical_plots.py",
    }
    skip_examples_for_version[(24, 2)] = {
        "3-2_Creating_an_XML_BoM.py",
        "4-1_BoM_Sustainability.py",
        "4-2_BoM_Sustainability_summary_phase_summary.py",
        "4-3_BoM_Sustainability_summary_transport.py",
        "4-4_BoM_Sustainability_summary_material.py",
        "4-5_BoM_Sustainability_summary_processes.py",
        "4-6_BoM_Sustainability_summary_hierarchical_plots.py",
    }

    if "example_script" in metafunc.fixturenames:
        this_file = pathlib.Path(__file__).parent.resolve()
        example_path = this_file / pathlib.Path("../examples")
        parameters = []
        example_files = discover_python_scripts(example_path)
        for example_file in example_files:
            xfail_examples = skip_examples_for_version[mi_version]
            if example_file.name in xfail_examples:
                formatted_version = ".".join(str(x) for x in mi_version)
                mark = pytest.mark.skip(
                    f'Example "{example_file.name}" skipped for Granta MI release version "{formatted_version}"'
                )
                param = pytest.param(example_file, id=example_file.name, marks=mark)
            else:
                param = pytest.param(example_file, id=example_file.name)
            parameters.append(param)
        metafunc.parametrize("example_script", parameters)


def discover_python_scripts(example_dir: pathlib.Path) -> List[pathlib.Path]:
    """Find all .py files recursively, starting in the provided path"""

    output_files = []
    for root, dirs, files in os.walk(example_dir):
        root_path = pathlib.Path(root)
        if root_path.name == ".ipynb_checkpoints":
            continue
        for file in files:
            file_path = pathlib.Path(file)
            if file_path.suffix != ".py":
                continue
            absolute_path = (root_path / file_path).absolute()
            output_files.append(absolute_path)
    return output_files


@pytest.fixture(scope="session")
def mi_version() -> tuple[int, int] | None:
    return get_mi_version()


@pytest.fixture(autouse=True)
def process_integration_marks(request, mi_version):
    """Processes the arguments provided to the integration mark.

    If the mark is initialized with the kwarg ``mi_versions``, the value must be of type list[tuple[int, int]], where
    the tuples contain compatible major and minor release versions of Granta MI. If the version is specified for a test
    case and the Granta MI version being tested against is not in the provided list, the test case is skipped.

    Also handles test-specific behavior, for example if a certain Granta MI version and test are incompatible and need
    to be skipped or xfailed.
    """

    # Argument validation
    if not request.node.get_closest_marker("integration"):
        # No integration marker anywhere in the stack
        return
    if mi_version is None:
        # We didn't get an MI version
        # Unlikely to occur, since if we didn't get an MI version we don't have a URL, so we can't run integration
        # tests anyway
        return

    # Process integration mark arguments
    mark: pytest.Mark = request.node.get_closest_marker("integration")
    if not mark.kwargs:
        # Mark not initialized with any keyword arguments
        return
    allowed_versions = mark.kwargs.get("mi_versions")
    if allowed_versions is None:
        return
    if not isinstance(allowed_versions, list):
        raise TypeError("mi_versions argument type must be of type 'list'")
    if mi_version not in allowed_versions:
        formatted_version = ".".join(str(x) for x in mi_version)
        skip_message = f'Test skipped for Granta MI release version "{formatted_version}"'
        pytest.skip(skip_message)
