import pytest
import os
import requests_mock
import pathlib
from typing import List
from ansys.grantami.bomanalytics import Connection


@pytest.fixture(scope="session")
def connection():
    connection = (
        Connection(servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"))
        .with_autologon()
        .connect()
    )
    return connection


@pytest.fixture
def mock_connection():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, text="")
        connection = (
            Connection(servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"))
            .with_anonymous()
            .connect()
        )
    return connection


def pytest_generate_tests(metafunc):
    """ Dynamically discover all example .py files and add to the set of parameters for a test if that test uses the
    'example_script' fixture.
    """

    if 'example_script' in metafunc.fixturenames:
        this_file = pathlib.Path(__file__).parent.resolve()
        example_path = this_file / pathlib.Path("../examples")
        output_files = discover_python_scripts(example_path)
        file_names = [str(file) for file in output_files]
        metafunc.parametrize('example_script', output_files, ids=file_names)


def discover_python_scripts(example_dir: pathlib.Path) -> List[pathlib.Path]:
    """ Find all .py files recursively, starting in the provided path """

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
