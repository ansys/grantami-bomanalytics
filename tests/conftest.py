import pytest

from ansys.granta.bom_analytics import (
    Connection,
    WatchListIndicator,
    RoHSIndicator,
)


@pytest.fixture(scope="session")
def connection():
    connection = Connection(
        url="http://localhost/mi_servicelayer",
        dbkey="MI_Restricted_Substances",
        username="***REMOVED***",
        password="***REMOVED***",
    )
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
