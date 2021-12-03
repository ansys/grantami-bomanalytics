import pytest
from dataclasses import dataclass
from ansys.grantami.bomanalytics_codegen import models
from ansys.grantami.bomanalytics._item_definitions import ReferenceType
from ansys.grantami.bomanalytics._item_results import ImpactedSubstance, ItemResultFactory
from .common import INDICATORS


@dataclass
class RecordSubstanceResultMock:
    reference_type: str
    reference_value: str
    legislations: list


@dataclass
class BomSubstanceResultMock:
    legislations: list


@dataclass
class ComplianceResultMock:
    reference_type: str
    reference_value: str
    indicators: list


impacted_substance_1 = models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance(
    substance_name="Substance1",
    cas_number="123-456",
    ec_number="654-321",
    max_percentage_amount_in_material=50,
    legislation_threshold=25
)
impacted_substance_2 = models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance(
    substance_name="Substance2",
    cas_number="456-789",
    ec_number="987-654"
)
sin_list_result = models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances(
    legislation_name="The SIN List 2.1 (Substitute It Now!)",
    impacted_substances=[impacted_substance_1]
)
ccc_result = models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances(
    legislation_name="Canadian Chemical Challenge",
    impacted_substances=[impacted_substance_1, impacted_substance_2]
)
legislation_results = [sin_list_result, ccc_result]

one_legislation_result = models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult(name="One legislation",
                                                                                         flag="RohsNotImpacted")

two_legislation_result = models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult(name="Two legislations",
                                                                                         flag="WatchListNotImpacted")


def test_impacted_substance_repr():
    impacted_substance = ImpactedSubstance(reference_type=ReferenceType.CasNumber,
                                           reference_value="123-456-789",
                                           max_percentage_amount_in_material=50,
                                           legislation_threshold=12)
    assert repr(impacted_substance) == f'<ImpactedSubstance: {{"cas_number": "123-456-789", "percent_amount": 50}}>'


@pytest.mark.parametrize("result_type", ["MaterialWithImpactedSubstances",
                                         "PartWithImpactedSubstances",
                                         "SpecificationWithImpactedSubstances"])
def test_impacted_substances_item_repr(result_type):
    query_result = RecordSubstanceResultMock(reference_type="MiRecordGuid",
                                             reference_value="TEST_GUID",
                                             legislations=legislation_results)
    result = ItemResultFactory.create_impacted_substances_result(result_type, query_result)
    assert repr(result) == f"<{result_type}Result({{'reference_type': 'MiRecordGuid', " \
                           f"'reference_value': 'TEST_GUID'}}), {len(legislation_results)} legislations>"
    assert repr(result.substances) == '[<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, ' \
                                      '<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, ' \
                                      '<ImpactedSubstance: {"cas_number": "456-789", "percent_amount": None}>]'

    for legislation in legislation_results:
        assert legislation.legislation_name in repr(result.substances_by_legislation)
    assert "ImpactedSubstance" in repr(result.substances_by_legislation)


def test_impacted_substances_bom_repr():
    query_result = BomSubstanceResultMock(legislations=legislation_results)
    result = ItemResultFactory.create_impacted_substances_result("BomWithImpactedSubstances", query_result)
    assert repr(result) == f"<BoM1711WithImpactedSubstancesResult(), {len(legislation_results)} legislations>"
    assert repr(result.substances) == '[<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, ' \
                                      '<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, ' \
                                      '<ImpactedSubstance: {"cas_number": "456-789", "percent_amount": None}>]'

    for legislation in legislation_results:
        assert legislation.legislation_name in repr(result.substances_by_legislation)
    assert "ImpactedSubstance" in repr(result.substances_by_legislation)


@pytest.mark.parametrize("result_type", ["PartWithCompliance",
                                         "MaterialWithCompliance",
                                         "SpecificationWithCompliance",
                                         "SubstanceWithCompliance",
                                         "CoatingWithCompliance"])
def test_compliance_item_repr(result_type):
    indicator_results = [two_legislation_result, one_legislation_result]
    query_result = ComplianceResultMock(reference_type="MiRecordGuid",
                                        reference_value="TEST_GUID",
                                        indicators=indicator_results)
    result = ItemResultFactory.create_compliance_result(result_type, query_result, INDICATORS)
    assert repr(result) == f"<{result_type}Result({{'reference_type': 'MiRecordGuid', " \
                           f"'reference_value': 'TEST_GUID'}}), {len(indicator_results)} indicators>"
