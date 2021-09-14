import pytest

from connection import Connection
from item_definitions import WatchlistIndicator, RoHSIndicator


@pytest.fixture(scope="session")
def connection():
    connection = Connection(url='http://localhost/mi_servicelayer',
                            dbkey='MI_Restricted_Substances',
                            username='***REMOVED***',
                            password='***REMOVED***')
    return connection


@pytest.fixture(scope="session")
def indicators():
    andys_noxious_substance_indicator = WatchlistIndicator(name="Andy's disliked substances",
                                                           legislation_names=['GADSL',
                                                                              'California Proposition 65 List'],
                                                           default_threshold_percentage=2)
    rohs_indicator = RoHSIndicator(name="RoHS 2",
                                   legislation_names=['EU Directive 2011/65/EU (RoHS 2)'],
                                   default_threshold_percentage=0.01)
    return [andys_noxious_substance_indicator, rohs_indicator]


@pytest.fixture(scope="session")
def legislations():
    return ['The SIN List 2.1 (Substitute It Now!)', 'Canadian Chemical Challenge']
