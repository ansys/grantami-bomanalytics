import pytest
import os
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


@pytest.fixture(scope="session")
def indicators():
    two_legislation_indicator = WatchListIndicator(
        name="Two legislations",
        legislation_names=["GADSL", "California Proposition 65 List"],
        default_threshold_percentage=2,
    )
    one_legislation_indicator = RoHSIndicator(
        name="One legislation",
        legislation_names=["EU Directive 2011/65/EU (RoHS 2)"],
        default_threshold_percentage=0.01,
    )
    return [two_legislation_indicator, one_legislation_indicator]


@pytest.fixture(scope="session")
def legislations():
    return ["The SIN List 2.1 (Substitute It Now!)", "Canadian Chemical Challenge"]
