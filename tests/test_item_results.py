from dataclasses import dataclass

from ansys.grantami.bomanalytics_openapi import models
import pytest

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


impacted_substance_1 = models.CommonImpactedSubstance(
    substance_name="Substance1",
    cas_number="123-456",
    ec_number="654-321",
    max_percentage_amount_in_material=50,
    legislation_threshold=25,
)
impacted_substance_2 = models.CommonImpactedSubstance(
    substance_name="Substance2", cas_number="456-789", ec_number="987-654"
)
sin_list_result = models.CommonLegislationWithImpactedSubstances(
    legislation_name="The SIN List 2.1 (Substitute It Now!)", impacted_substances=[impacted_substance_1]
)
ccc_result = models.CommonLegislationWithImpactedSubstances(
    legislation_name="Canadian Chemical Challenge", impacted_substances=[impacted_substance_1, impacted_substance_2]
)
legislation_results = [sin_list_result, ccc_result]

one_legislation_result = models.CommonIndicatorResult(name="One legislation", flag="RohsNotImpacted")

two_legislation_result = models.CommonIndicatorResult(name="Two legislations", flag="WatchListNotImpacted")


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
def test_impacted_substances_item_repr(result_type):
    query_result = RecordSubstanceResultMock(
        reference_type="MiRecordGuid", reference_value="TEST_GUID", legislations=legislation_results
    )
    result = ItemResultFactory.create_impacted_substances_result(result_type, query_result)
    assert (
        repr(result) == f"<{result_type}Result({{'reference_type': 'MiRecordGuid', "
        f"'reference_value': 'TEST_GUID'}}), {len(legislation_results)} legislations>"
    )
    assert (
        repr(result.substances) == '[<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
        '<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
        '<ImpactedSubstance: {"cas_number": "456-789", "percent_amount": None}>]'
    )

    for legislation in legislation_results:
        assert legislation.legislation_name in repr(result.substances_by_legislation)
    assert "ImpactedSubstance" in repr(result.substances_by_legislation)


def test_impacted_substances_bom_repr():
    query_result = BomSubstanceResultMock(legislations=legislation_results)
    result = ItemResultFactory.create_impacted_substances_result("BomWithImpactedSubstances", query_result)
    assert repr(result) == f"<BoM1711WithImpactedSubstancesResult(), {len(legislation_results)} legislations>"
    assert (
        repr(result.substances) == '[<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
        '<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
        '<ImpactedSubstance: {"cas_number": "456-789", "percent_amount": None}>]'
    )

    for legislation in legislation_results:
        assert legislation.legislation_name in repr(result.substances_by_legislation)
    assert "ImpactedSubstance" in repr(result.substances_by_legislation)


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


class TestSustainabilitySummaryResultsRepr:
    _rec_ref_kwargs = {"reference_type": "MiRecordGuid", "reference_value": "TEST_GUID"}
    _eco_metrics = {
        "embodied_energy": models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(
            value=1.0,
            unit="KJ",
        ),
        "climate_change": models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(
            value=1.0,
            unit="KJ",
        ),
        "embodied_energy_percentage": 60.0,
        "climate_change_percentage": 40.0,
    }

    def test_phase_summary_repr(self):
        phase_summary = models.CommonSustainabilityPhaseSummary(
            phase="Material",
            **self._eco_metrics,
        )
        phase_summary_result = ItemResultFactory.create_phase_summary(phase_summary)
        assert repr(phase_summary_result) == "<SustainabilityPhaseSummaryResult('Material', EE%=60.0, CC%=40.0)>"

    def test_transport_phase_summary_repr(self):
        model = models.CommonSustainabilityTransportSummaryEntry(
            **self._eco_metrics,
            stage_name="Train A->B",
            distance=models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(value=45, unit="km"),
            record_reference=models.CommonTransportReference(**self._rec_ref_kwargs),
        )
        transport_result = ItemResultFactory.create_transport_summary(model)
        expected = "<TransportSummaryResult('Train A->B', EE%=60.0, CC%=40.0)>"
        assert repr(transport_result) == expected

    def test_material_phase_summary_repr(self):
        model = models.CommonSustainabilityMaterialSummaryEntry(
            **self._eco_metrics,
            name="Steel",
            record_reference=models.CommonMaterialReference(**self._rec_ref_kwargs),
            largest_contributors=[],
            mass_after_processing=models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(
                value=50, unit="kg"
            ),
            mass_before_processing=models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(
                value=45, unit="kg"
            ),
        )
        result = ItemResultFactory.create_material_summary(model)
        expected = "<MaterialSummaryResult('Steel', EE%=60.0, CC%=40.0)>"
        assert repr(result) == expected

    def test_process_phase_summary_repr(self):
        model = models.CommonSustainabilityProcessSummaryEntry(
            **self._eco_metrics,
            material_name="Steel",
            material_record_reference=models.CommonMaterialReference(**self._rec_ref_kwargs),
            process_name="Forging",
            process_record_reference=models.CommonProcessReference(**self._rec_ref_kwargs),
        )
        result = ItemResultFactory.create_process_summary(model)
        expected = "<ProcessSummaryResult(process='Forging', material='Steel', EE%=60.0, CC%=40.0)>"
        assert repr(result) == expected

    def test_contributing_part_repr(self):
        model = models.CommonSustainabilityMaterialContributingComponent(
            component_name="Engine",
            material_mass_before_processing=models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(
                value=50, unit="kg"
            ),
            record_reference=models.CommonPartReference(**self._rec_ref_kwargs),
        )
        result = ItemResultFactory.create_contributing_component(model)
        expected = "<ContributingComponentResult('Engine', mass=50kg)>"
        assert repr(result) == expected


class TestSustainabilityResultsRepr:
    _rec_ref_kwargs = {"reference_type": "MiRecordGuid", "reference_value": "TEST_GUID"}
    _eco_metrics = {
        "embodied_energy": models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(
            value=2.3,
            unit="KJ",
        ),
        "climate_change": models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(
            value=5.1,
            unit="KJ",
        ),
    }

    def test_transport_result_repr(self):
        model = models.CommonSustainabilityTransportWithSustainability(
            **self._eco_metrics,
            **self._rec_ref_kwargs,
        )
        result = ItemResultFactory.create_transport_with_sustainability(model)
        expected = (
            "<TransportWithSustainabilityResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        )
        assert repr(result) == expected

    def test_part_result_repr(self):
        model = models.CommonSustainabilityPartWithSustainability(
            **self._eco_metrics,
            **self._rec_ref_kwargs,
            materials=[],
            substances=[],
            specifications=[],
            processes=[],
            parts=[],
            reported_mass=models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(value=45, unit="kg"),
        )
        result = ItemResultFactory.create_part_with_sustainability(model)
        expected = "<PartWithSustainabilityResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        assert repr(result) == expected

    def test_material_result_repr(self):
        model = models.CommonSustainabilityMaterialWithSustainability(
            **self._eco_metrics,
            **self._rec_ref_kwargs,
            biodegradable=True,
            downcycle=True,
            recyclable=True,
            processes=[],
            substances=[],
            reported_mass=models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(value=45, unit="kg"),
        )
        result = ItemResultFactory.create_material_with_sustainability(model)
        expected = (
            "<MaterialWithSustainabilityResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        )
        assert repr(result) == expected

    def test_process_result_repr(self):
        model = models.CommonSustainabilityProcessWithSustainability(
            **self._eco_metrics,
            **self._rec_ref_kwargs,
        )
        result = ItemResultFactory.create_process_with_sustainability(model)
        expected = (
            "<ProcessWithSustainabilityResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        )
        assert repr(result) == expected

    def test_coating_result_repr(self):
        model = models.CommonCoatingReference(
            **self._rec_ref_kwargs,
        )
        result = ItemResultFactory.create_coating_result(model)
        expected = "<CoatingResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        assert repr(result) == expected

    def test_substance_result_repr(self):
        model = models.CommonSubstanceReference(
            **self._rec_ref_kwargs,
        )
        result = ItemResultFactory.create_substance_result(model)
        expected = "<SubstanceResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        assert repr(result) == expected


def test_unitted_value_repr():
    model = models.GrantaBomAnalyticsServicesImplementationCommonValueWithUnit(unit="kg", value=255.2)
    result = ItemResultFactory.create_unitted_value(model)
    expected = '<ValueWithUnit(value=255.2, unit="kg")>'
    assert repr(result) == expected
