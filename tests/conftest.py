from .common import (
    pytest,
    os,
    Connection,
)


@pytest.fixture(scope="session")
def connection():
    connection = (
        Connection(servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"))
        .with_credentials(username=os.getenv("TEST_USER"), password=os.getenv("TEST_PASS"))
        .build()
    )
    return connection
