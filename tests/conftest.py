from .common import (
    pytest,
    os,
    requests_mock,
    Connection,
)


@pytest.fixture(scope="function")
def connection_mock():
    sl_url = os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")
    with requests_mock.Mocker() as m:
        m.get(sl_url, text="")  # Ensures that AuthenticatedApiClient gets a 200 response when validating the auth
        connection = (
            Connection(servicelayer_url=sl_url)
            .with_credentials(username=os.getenv("TEST_USER"), password=os.getenv("TEST_PASS"))
            .build()
        )
    return connection


@pytest.fixture(scope="session")
def connection():
    connection = (
        Connection(servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"))
        .with_credentials(username=os.getenv("TEST_USER"), password=os.getenv("TEST_PASS"))
        .build()
    )
    return connection
