import pytest
import os
from types import ModuleType
from ansys.granta.auth_common import AuthenticatedApiClient
from ansys.granta.bom_analytics import (
    Connection,
    WatchListIndicator,
    RoHSIndicator,
)


@pytest.fixture(scope="session")
def connection():
    client = AuthenticatedApiClient.with_credentials(
        servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"),
        username=os.getenv("TEST_USER"),
        password=os.getenv("TEST_PASS"),
    )
    connection = Connection(client=client, db_key=os.getenv("TEST_RS_DB_KEY", "MI_Restricted_Substances"))
    return connection


class ClientMock:
    def __init__(self):
        self.response = None

    def select_header_accept(self, *args, **kwargs):
        pass

    def select_header_content_type(self, *args, **kwargs):
        pass

    def setup_client(self, package: ModuleType):
        pass

    def call_api(self, *args, **kwargs):
        return self.response


@pytest.fixture(scope="session")
def mock_connection():
    client = ClientMock()
    connection = Connection(client=client, db_key=os.getenv("TEST_RS_DB_KEY", "MI_Restricted_Substances"))
    return connection
