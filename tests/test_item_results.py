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
    legislation_id="SINList", impacted_substances=[impacted_substance_1]
)
ccc_result = models.CommonLegislationWithImpactedSubstances(
    legislation_id="CCC", impacted_substances=[impacted_substance_1, impacted_substance_2]
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


class TestImpactedSubstancesResultsRepr:
    def _check_properties_repr(self, result):
        assert (
            repr(result.substances) == '[<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
            '<ImpactedSubstance: {"cas_number": "123-456", "percent_amount": 50}>, '
            '<ImpactedSubstance: {"cas_number": "456-789", "percent_amount": None}>]'
        )

        for legislation in legislation_results:
            assert legislation.legislation_id in repr(result.substances_by_legislation)
        assert "ImpactedSubstance" in repr(result.substances_by_legislation)

    def test_specification_impacted_substances_item_repr(self):
        query_result = models.GetImpactedSubstancesForSpecificationsSpecification(
            reference_type="MiRecordGuid", reference_value="TEST_GUID", legislations=legislation_results
        )
        result = ItemResultFactory.create_specification_impacted_substances_result(query_result)
        assert (
            repr(result) == f"<SpecificationWithImpactedSubstancesResult({{'reference_type': 'MiRecordGuid', "
            f"'reference_value': 'TEST_GUID'}}), {len(legislation_results)} legislations>"
        )
        self._check_properties_repr(result)

    def test_material_impacted_substances_item_repr(self):
        query_result = models.GetImpactedSubstancesForMaterialsMaterial(
            reference_type="MiRecordGuid", reference_value="TEST_GUID", legislations=legislation_results
        )
        result = ItemResultFactory.create_material_impacted_substances_result(query_result)
        assert (
            repr(result) == f"<MaterialWithImpactedSubstancesResult({{'reference_type': 'MiRecordGuid', "
            f"'reference_value': 'TEST_GUID'}}), {len(legislation_results)} legislations>"
        )
        self._check_properties_repr(result)

    def test_part_impacted_substances_item_repr(
        self,
    ):
        query_result = models.GetImpactedSubstancesForPartsPart(
            reference_type="MiRecordGuid", reference_value="TEST_GUID", legislations=legislation_results
        )
        result = ItemResultFactory.create_part_impacted_substances_result(query_result)
        assert (
            repr(result) == f"<PartWithImpactedSubstancesResult({{'reference_type': 'MiRecordGuid', "
            f"'reference_value': 'TEST_GUID'}}), {len(legislation_results)} legislations>"
        )
        self._check_properties_repr(result)

    def test_impacted_substances_bom_repr(self):
        query_result = models.GetImpactedSubstancesForBom1711Response(
            legislations=legislation_results,
            log_messages=[],
        )
        result = ItemResultFactory.create_bom_impacted_substances_result(query_result)

        assert repr(result) == f"<BoM1711WithImpactedSubstancesResult(), {len(legislation_results)} legislations>"
        self._check_properties_repr(result)


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
        "embodied_energy": models.CommonValueWithUnit(
            value=1.0,
            unit="KJ",
        ),
        "climate_change": models.CommonValueWithUnit(
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
            distance=models.CommonValueWithUnit(value=45, unit="km"),
            record_reference=models.CommonTransportReference(**self._rec_ref_kwargs),
        )
        transport_result = ItemResultFactory.create_transport_summary(model)
        expected = "<TransportSummaryResult('Train A->B', EE%=60.0, CC%=40.0)>"
        assert repr(transport_result) == expected

    def test_material_phase_summary_repr(self):
        model = models.CommonSustainabilityMaterialSummaryEntry(
            **self._eco_metrics,
            identity="Steel",
            record_reference=models.CommonMaterialReference(**self._rec_ref_kwargs),
            largest_contributors=[],
            mass_after_processing=models.CommonValueWithUnit(value=50, unit="kg"),
            mass_before_processing=models.CommonValueWithUnit(value=45, unit="kg"),
        )
        result = ItemResultFactory.create_material_summary(model)
        expected = "<MaterialSummaryResult('Steel', EE%=60.0, CC%=40.0)>"
        assert repr(result) == expected

    def test_process_phase_summary_repr(self):
        model = models.CommonSustainabilityProcessSummaryEntry(
            **self._eco_metrics,
            material_identity="Steel",
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
            material_mass_before_processing=models.CommonValueWithUnit(value=50, unit="kg"),
            record_reference=models.CommonPartReference(**self._rec_ref_kwargs),
        )
        result = ItemResultFactory.create_contributing_component(model)
        expected = "<ContributingComponentResult('Engine', mass=50kg)>"
        assert repr(result) == expected


class TestSustainabilityResultsRepr:
    _rec_ref_kwargs = {"reference_type": "MiRecordGuid", "reference_value": "TEST_GUID"}
    _eco_metrics = {
        "embodied_energy": models.CommonValueWithUnit(value=2.3, unit="KJ"),
        "climate_change": models.CommonValueWithUnit(value=5.1, unit="KJ"),
    }
    _id = {"id": "TEST_ID"}
    _identifiers = {
        "id": "TEST_ID",
        "external_identity": "TEST_EXT_ID",
        "name": "TEST_NAME",
    }

    def test_transport_result_repr(self):
        model = models.CommonSustainabilityTransportWithSustainability(
            **self._eco_metrics,
            **self._rec_ref_kwargs,
            **self._id,
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
            **self._identifiers,
            input_part_number="TEST_PN",
            materials=[],
            substances=[],
            specifications=[],
            processes=[],
            parts=[],
            reported_mass=models.CommonValueWithUnit(value=45, unit="kg"),
        )
        result = ItemResultFactory.create_part_with_sustainability(model)
        expected = "<PartWithSustainabilityResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        assert repr(result) == expected

    def test_material_result_repr(self):
        model = models.CommonSustainabilityMaterialWithSustainability(
            **self._eco_metrics,
            **self._rec_ref_kwargs,
            **self._identifiers,
            biodegradable=True,
            functional_recycle=True,
            recyclable=True,
            processes=[],
            substances=[],
            reported_mass=models.CommonValueWithUnit(value=45, unit="kg"),
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
            **self._identifiers,
        )
        result = ItemResultFactory.create_process_with_sustainability(model)
        expected = (
            "<ProcessWithSustainabilityResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        )
        assert repr(result) == expected

    def test_coating_result_repr(self):
        model = models.CommonCoatingReference(
            **self._rec_ref_kwargs,
            **self._id,
        )
        result = ItemResultFactory.create_coating_result(model)
        expected = "<CoatingResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        assert repr(result) == expected

    def test_substance_result_repr(self):
        model = models.CommonSubstanceReference(
            **self._rec_ref_kwargs,
            **self._identifiers,
        )
        result = ItemResultFactory.create_substance_result(model)
        expected = "<SubstanceResult({'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        assert repr(result) == expected

    def test_specification_result_repr(self):
        model = models.CommonSustainabilitySpecificationWithSustainability(
            **self._rec_ref_kwargs,
            **self._eco_metrics,
            **self._identifiers,
            reported_mass=models.CommonValueWithUnit(value=45, unit="kg"),
            specifications=[],
            materials=[],
            substances=[],
            coatings=[],
        )
        result = ItemResultFactory.create_specification_with_sustainability(model)
        expected = (
            "<SpecificationWithSustainabilityResult("
            "{'reference_type': 'MiRecordGuid', 'reference_value': 'TEST_GUID'})>"
        )
        assert repr(result) == expected


class TestLicensing:
    @pytest.mark.parametrize("restricted_substances", [True, False])
    @pytest.mark.parametrize("sustainability", [True, False])
    def test_factory(self, restricted_substances, sustainability):
        response = models.GetAvailableLicensesResponse(
            restricted_substances=restricted_substances,
            sustainability=sustainability,
        )
        result = ItemResultFactory.create_licensing_result(response)
        assert result.restricted_substances is restricted_substances
        assert result.sustainability is sustainability


def test_unitted_value_repr():
    model = models.CommonValueWithUnit(unit="kg", value=255.2)
    result = ItemResultFactory.create_unitted_value(model)
    expected = '<ValueWithUnit(value=255.2, unit="kg")>'
    assert repr(result) == expected
