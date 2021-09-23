import pytest
import os
from ansys.granta.auth_common import AuthenticatedApiClient
from ansys.granta.bomanalytics import models
from ansys.granta.bom_analytics import Connection
from .common import ConnectionMock


@pytest.fixture(scope="session")
def client():
    client = AuthenticatedApiClient.with_credentials(
        servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"),
        username=os.getenv("TEST_USER"),
        password=os.getenv("TEST_PASS"),
    )
    client.setup_client(models)
    return client


@pytest.fixture(scope="session")
def connection(client):
    return Connection(client, db_key=os.getenv("TEST_RS_DB_KEY", "MI_Restricted_Substances"))


@pytest.fixture(scope="function")
def connection_mock(client, request):
    api_name = request.param[0]
    api_call_method = request.param[1]
    response_type = request.param[2]

    return ConnectionMock(api_name, api_call_method, response_type, client)
