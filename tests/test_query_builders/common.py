from ..common import (
    pytest,
    List,
    LEGISLATIONS,
    INDICATORS,
    check_query_manager_attributes,
    queries,
)


RECORD_QUERY_TYPES: List = [
    queries.MaterialImpactedSubstances,
    queries.MaterialCompliance,
    queries.PartImpactedSubstances,
    queries.PartCompliance,
    queries.SpecificationImpactedSubstances,
    queries.SpecificationCompliance,
    queries.SubstanceCompliance,
]

COMPLIANCE_QUERY_TYPES: List = [
    queries.MaterialCompliance,
    queries.PartCompliance,
    queries.SpecificationCompliance,
    queries.SubstanceCompliance,
    queries.BomCompliance,
]
SUBSTANCE_QUERY_TYPES: List = [
    queries.MaterialImpactedSubstances,
    queries.PartImpactedSubstances,
    queries.SpecificationImpactedSubstances,
    queries.BomImpactedSubstances,
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
