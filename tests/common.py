from typing import Union, List, Callable, Any
import pytest
import pathlib
from numbers import Number
import random
import os
import requests_mock
from ansys.granta.bomanalytics import (
    models,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsResponse,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsResponse,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesResponse,
    GrantaBomAnalyticsServicesInterfaceCommonMaterialReference,
    GrantaBomAnalyticsServicesInterfaceCommonPartReference,
    GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount,
    GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition,
)

from ansys.granta.bom_analytics import (
    queries,
    indicators,
    Connection,
)
from ansys.granta.bom_analytics._allowed_types import allowed_types, check_type
from ansys.granta.bom_analytics.indicators import _Indicator
from ansys.granta.bom_analytics._bom_item_definitions import (
    BoM1711Definition,
    MaterialDefinition,
    SpecificationDefinition,
    PartDefinition,
    SubstanceDefinition,
    ReferenceType,
)

from .examples import examples_as_strings


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


LEGISLATIONS = ["The SIN List 2.1 (Substitute It Now!)", "Canadian Chemical Challenge"]


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
