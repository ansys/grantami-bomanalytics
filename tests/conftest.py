import pytest
import os
from ansys.granta.bom_analytics import Connection, indicators


@pytest.fixture(scope="session")
def connection():
    connection = (
        Connection(servicelayer_url=os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer"))
        .with_credentials(username=os.getenv("TEST_USER"), password=os.getenv("TEST_PASS"))
        .build()
    )
    return connection


@pytest.fixture(scope="session")
def indicator_definitions():
    two_legislation_indicator = indicators.WatchListIndicator(
        name="Two legislations",
        legislation_names=["GADSL", "California Proposition 65 List"],
        default_threshold_percentage=2,
    )
    one_legislation_indicator = indicators.RoHSIndicator(
        name="One legislation",
        legislation_names=["EU Directive 2011/65/EU (RoHS 2)"],
        default_threshold_percentage=0.01,
    )
    return [two_legislation_indicator, one_legislation_indicator]


@pytest.fixture(scope="session")
def legislations():
    return ["The SIN List 2.1 (Substitute It Now!)", "Canadian Chemical Challenge"]
