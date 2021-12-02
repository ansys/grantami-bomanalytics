from ansys.grantami.bomanalytics import queries, indicators
from ansys.grantami.bomanalytics_codegen.models import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsResponse,
)
from .common import (
    get_mocked_response,
    SubstanceValidator,
    MaterialValidator,
)


class TestImpactedSubstances:
    query = (
        queries.MaterialImpactedSubstancesQuery().with_legislations(["Fake legislation"]).with_material_ids(["Fake ID"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsResponse.__name__

    def test_impacted_substances_by_material_and_legislation(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances_by_material_and_legislation) == 1

        mat_results = response.impacted_substances_by_material_and_legislation[0]
        mv = MaterialValidator(mat_results)
        assert mv.check_reference(material_id="elastomer-butadienerubber")
        legislations = mat_results.legislations
        assert len(legislations) == 1
        legislation = legislations["The SIN List 2.1 (Substitute It Now!)"]
        assert legislation.name == "The SIN List 2.1 (Substitute It Now!)"
        assert len(legislation.substances) == 2
        for substance in legislation.substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_impacted_substances_by_legislation(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        for substance in legislation:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_impacted_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances) == 2
        for substance in response.impacted_substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()


class TestCompliance:
    """Check that each mocked result has the correct record references, indicator results, child objects, and bom
    relationships.

    A mocked query is used, populated by the examples included in the API definition.

    Material and substance details are verified in separate methods.
    """

    query = (
        queries.MaterialComplianceQuery()
        .with_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .with_material_ids(["Fake ID"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsResponse.__name__

    def test_compliance_by_material_and_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_material_and_indicator) == 2

        mat_0 = response.compliance_by_material_and_indicator[0]
        mv_0 = MaterialValidator(mat_0)
        assert mv_0.check_reference(material_id="S200")
        mat_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert mv_0.check_indicators(mat_0_result)
        assert mv_0.check_bom_structure()

        mat_1 = response.compliance_by_material_and_indicator[1]
        mv_1 = MaterialValidator(mat_1)
        assert mv_1.check_reference(record_guid="3df206df-9fc8-4859-90d4-3519764f8b55")
        mat_1_result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert mv_1.check_indicators(mat_1_result)
        assert mv_1.check_bom_structure()

    def test_compliance_by_material_and_indicator_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        substance_0_0 = response.compliance_by_material_and_indicator[0].substances[0]
        sv_0_0 = SubstanceValidator(substance_0_0)
        assert sv_0_0.check_reference(record_history_identity="12345")
        substance_0_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_0_0.check_indicators(substance_0_0_result)
        assert sv_0_0.check_bom_structure()

        substance_1_0 = response.compliance_by_material_and_indicator[1].substances[0]
        sv_1_0 = SubstanceValidator(substance_1_0)
        assert sv_1_0.check_reference(record_history_identity="12345")
        substance_1_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_0.check_indicators(substance_1_0_result)
        assert sv_1_0.check_bom_structure()

        substance_1_1 = response.compliance_by_material_and_indicator[1].substances[1]
        sv_1_1 = SubstanceValidator(substance_1_1)
        assert sv_1_1.check_reference(record_history_identity="34567")
        substance_1_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert sv_1_1.check_indicators(substance_1_1_result)
        assert sv_1_1.check_bom_structure()

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        result = [indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold, indicators.RoHSFlag.RohsNonCompliant]
        assert all(
            [actual.flag == expected for actual, expected in zip(response.compliance_by_indicator.values(), result)]
        )

    def test_indicator_results_are_separate_objects(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        for result in response.compliance_by_material_and_indicator:
            for k, v in result.indicators.items():
                assert k in self.query._indicators  # The indicator name should be the same (string equality)
                assert v is not self.query._indicators[k]  # The indicator object should be a copy (non-identity)
