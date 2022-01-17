import pytest
from dataclasses import dataclass
from ansys.grantami.bomanalytics_openapi import models
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


impacted_substance_1_high = models.CommonImpactedSubstance(
    substance_name="Substance1",
    cas_number="123-456",
    ec_number="654-321",
    max_percentage_amount_in_material=50,
    legislation_threshold=50,
)
impacted_substance_1_low = models.CommonImpactedSubstance(
    substance_name="Substance1",
    cas_number="123-456",
    ec_number="654-321",
    max_percentage_amount_in_material=25,
    legislation_threshold=25,
)
impacted_substance_1_none = models.CommonImpactedSubstance(
    substance_name="Substance1",
    cas_number="123-456",
    ec_number="654-321",
    max_percentage_amount_in_material=None,
    legislation_threshold=None,
)

impacted_substance_2 = models.CommonImpactedSubstance(
    substance_name="Substance2",
    cas_number="456-789",
    ec_number="987-654",
)

leg_result_1_substance_high = models.CommonLegislationWithImpactedSubstances(
    legislation_name="Legislation_1", impacted_substances=[impacted_substance_1_high]
)
leg_result_2_substances = models.CommonLegislationWithImpactedSubstances(
    legislation_name="Legislation_2", impacted_substances=[impacted_substance_1_high, impacted_substance_2]
)
leg_result_1_substance_low = models.CommonLegislationWithImpactedSubstances(
    legislation_name="Legislation_3", impacted_substances=[impacted_substance_1_low]
)
leg_result_1_substance_none = models.CommonLegislationWithImpactedSubstances(
    legislation_name="Legislation_4", impacted_substances=[impacted_substance_1_none]
)

leg_results = [leg_result_1_substance_high, leg_result_2_substances]
leg_results_high_and_low = [leg_result_1_substance_high, leg_result_1_substance_low]
leg_results_sparse = [leg_result_1_substance_high, leg_result_1_substance_none]


def test_impacted_substance_repr():
    impacted_substance = ImpactedSubstance(
        reference_type=ReferenceType.CasNumber,
        reference_value="123-456-789",
        max_percentage_amount_in_material=50,
        legislation_threshold=12,
    )
    assert repr(impacted_substance) == f'<ImpactedSubstance: {{"cas_number": "123-456-789", "percent_amount": 50}}>'


@pytest.mark.parametrize(
    "result_type",
    ["MaterialWithImpactedSubstances", "PartWithImpactedSubstances", "SpecificationWithImpactedSubstances"],
)
@pytest.mark.parametrize("reverse_order", [True, False])
class TestItemWithImpactedSubstancesSubstances:
    def test_substances_highest_amount_wins(self, result_type, reverse_order):
        query_result = RecordSubstanceResultMock(
            reference_type="MiRecordGuid",
            reference_value="TEST_GUID",
            legislations=reversed(leg_results_high_and_low) if reverse_order else leg_results_high_and_low,
        )
        result = ItemResultFactory.create_impacted_substances_result(result_type, query_result)
        merged_substance = [s for s in result.substances if s.cas_number == "123-456"]
        assert len(merged_substance) == 1
        assert merged_substance.pop().max_percentage_amount_in_material == 50

    def test_substances_threshold_is_None(self, result_type, reverse_order):
        query_result = RecordSubstanceResultMock(
            reference_type="MiRecordGuid",
            reference_value="TEST_GUID",
            legislations=reversed(leg_results_high_and_low) if reverse_order else leg_results_high_and_low,
        )
        result = ItemResultFactory.create_impacted_substances_result(result_type, query_result)
        merged_substance = [s for s in result.substances if s.cas_number == "123-456"]
        assert len(merged_substance) == 1
        assert merged_substance.pop().legislation_threshold is None

    def test_substances_populated_amount_wins(self, result_type, reverse_order):
        query_result = RecordSubstanceResultMock(
            reference_type="MiRecordGuid",
            reference_value="TEST_GUID",
            legislations=reversed(leg_results_sparse) if reverse_order else leg_results_sparse,
        )
        result = ItemResultFactory.create_impacted_substances_result(result_type, query_result)
        merged_substance = [s for s in result.substances if s.cas_number == "123-456"]
        assert len(merged_substance) == 1
        assert merged_substance.pop().max_percentage_amount_in_material == 50


@pytest.mark.parametrize(
    "result_type",
    ["MaterialWithImpactedSubstances", "PartWithImpactedSubstances", "SpecificationWithImpactedSubstances"],
)
class TestItemWithImpactedSubstancesReprs:
    query_result = RecordSubstanceResultMock(
        reference_type="MiRecordGuid", reference_value="TEST_GUID", legislations=leg_results
    )

    def test_item_result_repr(self, result_type):
        result = ItemResultFactory.create_impacted_substances_result(result_type, type(self).query_result)
        assert (
            repr(result) == f"<{result_type}Result({{'reference_type': 'MiRecordGuid', "
            f"'reference_value': 'TEST_GUID'}}), {len(leg_results)} legislations>"
        )

    def test_substances_list_repr(self, result_type):
        result = ItemResultFactory.create_impacted_substances_result(result_type, type(self).query_result)
        assert (
            repr(result.substances) == '[<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
            '<ImpactedSubstance: {"cas_number": "456-789", "percent_amount": None}>]'
        )

    def test_substances_by_legislation_repr(self, result_type):
        result = ItemResultFactory.create_impacted_substances_result(result_type, type(self).query_result)
        for legislation in leg_results:
            assert legislation.legislation_name in repr(result.substances_by_legislation)
        assert "ImpactedSubstance" in repr(result.substances_by_legislation)


class TestBomWithImpactedSubstancesReprs:
    query_result = BomSubstanceResultMock(legislations=leg_results)

    def test_substances_list_repr(self):
        result = ItemResultFactory.create_impacted_substances_result(
            "BomWithImpactedSubstances", type(self).query_result
        )
        assert repr(result) == f"<BoM1711WithImpactedSubstancesResult(), {len(leg_results)} legislations>"
        assert (
            repr(result.substances) == '[<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
            '<ImpactedSubstance: {"cas_number": "456-789", "percent_amount": None}>]'
        )

    def test_substances_by_legislation_repr(self):
        result = ItemResultFactory.create_impacted_substances_result(
            "BomWithImpactedSubstances", type(self).query_result
        )
        for legislation in leg_results:
            assert legislation.legislation_name in repr(result.substances_by_legislation)
        assert "ImpactedSubstance" in repr(result.substances_by_legislation)


one_legislation_result = models.CommonIndicatorResult(name="One legislation", flag="RohsNotImpacted")
two_legislation_result = models.CommonIndicatorResult(name="Two legislations", flag="WatchListNotImpacted")


@pytest.mark.parametrize(
    "result_type",
    [
        "PartWithCompliance",
        "MaterialWithCompliance",
        "SpecificationWithCompliance",
        "SubstanceWithCompliance",
        "CoatingWithCompliance",
    ],
)
def test_compliance_item_repr(result_type):
    indicator_results = [two_legislation_result, one_legislation_result]
    query_result = ComplianceResultMock(
        reference_type="MiRecordGuid", reference_value="TEST_GUID", indicators=indicator_results
    )
    result = ItemResultFactory.create_compliance_result(result_type, query_result, INDICATORS)
    assert (
        repr(result) == f"<{result_type}Result({{'reference_type': 'MiRecordGuid', "
        f"'reference_value': 'TEST_GUID'}}), {len(indicator_results)} indicators>"
    )
