import os
import pathlib
from typing import List

import pytest
import requests_mock

from ansys.grantami.bomanalytics import Connection

from .common import CUSTOM_TABLES, LICENSE_RESPONSE

sl_url = os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")
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
