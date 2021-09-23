from typing import List, Callable
from ansys.granta.bom_analytics import (
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    PartImpactedSubstanceQuery,
    PartComplianceQuery,
    SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
    BomImpactedSubstanceQuery,
    BomComplianceQuery,
    WatchListIndicator,
    RoHSIndicator,
)
from .examples import example_dict

RECORD_QUERY_TYPES: List = [
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    PartImpactedSubstanceQuery,
    PartComplianceQuery,
    SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
]

COMPLIANCE_QUERY_TYPES: List = [
    MaterialComplianceQuery,
    PartComplianceQuery,
    SpecificationComplianceQuery,
    SubstanceComplianceQuery,
    BomComplianceQuery,
]
SUBSTANCE_QUERY_TYPES: List = [
    MaterialImpactedSubstanceQuery,
    PartImpactedSubstanceQuery,
    SpecificationImpactedSubstanceQuery,
    BomImpactedSubstanceQuery,
]
ALL_QUERY_TYPES = COMPLIANCE_QUERY_TYPES + SUBSTANCE_QUERY_TYPES


TEST_GUIDS = [
    [],
    ["00000000-0000-0000-0000-000000000000"],
    [
        "00000000-0123-4567-89AB-000000000000",
        "00000000-0000-0000-0000-CDEF01234567",
    ],
]


TEST_HISTORY_IDS = [
    [],
    [123],
    [
        456,
        789,
    ],
]

STK_OBJECT = [
    {
        "db_key": "MI_Restricted_Substances",
        "record_guid": "00000000-0000-0000-0000-000000000000",
    },
    {
        "db_key": "MI_Restricted_Substances",
        "record_guid": "00000000-0000-0000-0000-000000000123",
    },
]


LEGISLATIONS = ["The SIN List 2.1 (Substitute It Now!)", "Canadian Chemical Challenge"]


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


INDICATORS = [two_legislation_indicator, one_legislation_indicator]


def check_query_manager_attributes(query_manager, none_attributes, populated_attributes, populated_values):
    assert len(query_manager._items) == len(populated_values)
    for idx, value in enumerate(populated_values):
        if query_manager._items[idx].__getattribute__(populated_attributes) != value:
            return False
        for none_attr in none_attributes:
            if query_manager._items[idx].__getattribute__(none_attr):
                return False
    return True


class ConnectionMock:
    def __init__(self, api_name: str, api_call_method_name: str, response_type: Callable, client):
        self.db_key = "Mock_db_key"
        self.query_config = None
        api_object = self.__class__.API(api_call_method_name, response_type, client)
        setattr(self, api_name, api_object)

    class API:
        def __init__(self, call_method_name: str, response_type: Callable, client):
            response = example_dict[response_type.__name__]
            self.response = client._ApiClient__deserialize(response, response_type)
            setattr(self, call_method_name, self.api_call)

        def api_call(self, **kwargs):
            return self.response
