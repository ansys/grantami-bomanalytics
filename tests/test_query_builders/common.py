from typing import List
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
)

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


def check_query_manager_attributes(
    query_manager, none_attributes, populated_attributes, populated_values
):
    assert len(query_manager._items) == len(populated_values)
    for idx, value in enumerate(populated_values):
        if query_manager._items[idx].__getattribute__(populated_attributes) != value:
            return False
        for none_attr in none_attributes:
            if query_manager._items[idx].__getattribute__(none_attr):
                return False
    return True
