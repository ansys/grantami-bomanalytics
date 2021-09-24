from .common import (
    pytest,
    os,
    requests_mock,
    AuthenticatedApiClient,
    Connection,
    ConnectionMock,
    models,
)


@pytest.fixture(scope="session")
def mock_client():
    """A fixture to create a 'fake' client object. Useful for using some of the serialization / deserialization methods
    in the auth_common package without actually needing to talk to a server."""

    sl_url = os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")
    with requests_mock.Mocker() as m:
        m.get(sl_url, text="")  # Ensures that AuthenticatedApiClient gets a response when validating the auth
        client = AuthenticatedApiClient.with_anonymous(servicelayer_url=sl_url)
    client.setup_client(models)
    return client


@pytest.fixture(scope="function")
def connection_mock(mock_client, request):
    api_name = request.param[0]
    api_call_method = request.param[1]
    response_type = request.param[2]

    return ConnectionMock(api_name, api_call_method, response_type, mock_client)


@pytest.fixture(scope="session")
def authenticated_client():
    client = AuthenticatedApiClient.with_credentials(
        servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"),
        username=os.getenv("TEST_USER"),
        password=os.getenv("TEST_PASS"),
    )
    client.setup_client(models)
    return client


@pytest.fixture(scope="session")
def connection(authenticated_client):
    return Connection(authenticated_client, db_key=os.getenv("TEST_RS_DB_KEY", "MI_Restricted_Substances"))
