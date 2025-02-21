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

import os
import pathlib
from typing import List, cast
from xml.etree import ElementTree as ET

import pytest
import requests_mock

from ansys.grantami.bomanalytics import Connection

from .common import CUSTOM_TABLES, LICENSE_RESPONSE

CI = os.getenv("CI")
_test_sl_url_env = os.getenv("TEST_SL_URL")
sl_url = "http://localhost/mi_servicelayer" if (not CI and not _test_sl_url_env) else _test_sl_url_env
read_username = os.getenv("TEST_USER")
read_password = os.getenv("TEST_PASS")

write_username = os.getenv("TEST_WRITE_USER")
write_password = os.getenv("TEST_WRITE_PASS")


def _get_connection(url, username, password):
    if username is not None:
        connection = Connection(api_url=url).with_credentials(username, password).connect()
    else:
        connection = Connection(api_url=url).with_autologon().connect()
    return connection


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

    if "example_script" in metafunc.fixturenames:
        this_file = pathlib.Path(__file__).parent.resolve()
        example_path = this_file / pathlib.Path("../examples")
        output_files = discover_python_scripts(example_path)
        file_names = [str(file) for file in output_files]
        metafunc.parametrize("example_script", output_files, ids=file_names)


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
    """The version of MI referenced by the test url.

    Returns
    -------
    tuple[int, int] | None
        A 2-tuple containing the (MAJOR, MINOR) Granta MI release version, or None if a test URL is not available.

    Notes
    -----
    This fixture returns None if the ``sl_url`` variable is not available. This is typically because the tests are
    running in CI and the TEST_SL_URL environment variable was not populated.
    """
    if not sl_url:
        return None
    connection = _get_connection(sl_url, read_username, read_password)
    session = connection.rest_client
    response = session.get(connection._sl_url + "/SystemInfo/v4.svc/Versions/Mi")
    tree = ET.fromstring(response.text)
    version = next(c.text for c in tree if c.tag.rpartition("}")[2] == "MajorMinorVersion")
    parsed_version = [int(v) for v in version.split(".")]
    assert len(parsed_version) == 2
    return cast(tuple[int, int], tuple(parsed_version))


@pytest.fixture(autouse=True)
def skip_by_release_version(request, mi_version):
    """Checks if each test case should be executed based on the ``reports_release_versions`` marker.

    The marker should be initialized with an argument of type list[tuple[int, int]], where the tuples contain compatible
    major and minor release versions of Granta MI. If the marker is specified for a test case and the Granta MI
    version being tested against is not in the provided list, the test case is skipped.
    """

    if mi_version is None:
        return
    if request.node.get_closest_marker("reports_release_versions"):
        allowed_versions = request.node.get_closest_marker("reports_release_versions").args[0]
        if not isinstance(allowed_versions, list):
            raise TypeError("reports_release_versions argument type must be list")
        if mi_version not in allowed_versions:
            formatted_version = ".".join(str(x) for x in mi_version)
            skip_message = f'Test skipped for RS and Sustainability reports release version "{formatted_version}"'
            pytest.skip(skip_message)
