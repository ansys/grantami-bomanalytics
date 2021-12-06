import pytest
import os
import requests_mock
from ansys.grantami.bomanalytics import Connection


@pytest.fixture(scope="session")
def connection():
    connection = (
        Connection(servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer/"))
        .with_credentials(username=os.getenv("TEST_USER"), password=os.getenv("TEST_PASS"))
        .build()
    )
    return connection


@pytest.fixture
def mock_connection():
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, text="")
        connection = (
            Connection(servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer/"))
            .with_anonymous()
            .build()
        )
    return connection
