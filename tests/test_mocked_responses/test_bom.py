from ansys.grantami.bomanalytics import queries, indicators
from ansys.grantami.bomanalytics_openapi.models import (
    GetImpactedSubstancesForBom1711Response,
    GetComplianceForBom1711Response,
)
from .common import (
    BaseMockTester,
    PartValidator,
    SubstanceValidator,
    MaterialValidator,
)


class TestImpactedSubstances(BaseMockTester):
    query = queries.BomImpactedSubstancesQuery()
    mock_key = GetImpactedSubstancesForBom1711Response.__name__

    def test_impacted_substances_by_legislation(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        for substance in legislation:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_impacted_substances(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.impacted_substances) == 2
        for substance in response.impacted_substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_query_result_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert repr(response) == "<BomImpactedSubstancesQueryResult: 1 BomWithImpactedSubstances results>"

    def test_impacted_substances_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "ImpactedSubstance" in repr(response.impacted_substances)

    def test_impacted_substances_by_legislation_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        for legislation in response.impacted_substances_by_legislation.keys():
            assert legislation in repr(response.impacted_substances_by_legislation)
        assert "ImpactedSubstance" in repr(response.impacted_substances_by_legislation)


class TestCompliance(BaseMockTester):
    """Check that each mocked result has the correct record references, indicator results, child objects, and bom
    relationships.

    A mocked query is used, populated by the examples included in the API definition.
    """

    query = queries.BomComplianceQuery().with_indicators(
        [
            indicators.WatchListIndicator(name="Indicator 1", legislation_ids=["Mock"]),
            indicators.RoHSIndicator(name="Indicator 2", legislation_ids=["Mock"]),
        ]
    )
    mock_key = GetComplianceForBom1711Response.__name__

    def test_compliance_by_part_and_indicator(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.compliance_by_part_and_indicator) == 2

        # Top level part 0
        part_0 = response.compliance_by_part_and_indicator[0]
        pv_0 = PartValidator(part_0)
        assert pv_0.check_reference()
        part_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert pv_0.check_indicators(part_0_result)
        assert pv_0.check_empty_children(materials=True, specifications=True, substances=True)
        assert pv_0.check_bom_structure()

        # Level 1: Child part
        part_0_0 = part_0.parts[0]
        pv_0_0 = PartValidator(part_0_0)
        assert pv_0_0.check_reference()
        part_0_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert pv_0_0.check_indicators(part_0_0_result)
        assert pv_0_0.check_empty_children(materials=True, specifications=True, parts=True)
        assert pv_0_0.check_bom_structure()

        # Level 2: Child substance
        substance_0_0_0 = part_0_0.substances[0]
        sv_0_0_0 = SubstanceValidator(substance_0_0_0)
        assert sv_0_0_0.check_reference(record_history_identity="62345")
        substance_0_0_0_result = [indicators.WatchListFlag.WatchListNotImpacted, indicators.RoHSFlag.RohsNotImpacted]
        assert sv_0_0_0.check_indicators(substance_0_0_0_result)
        assert sv_0_0_0.check_bom_structure()

        # Top level part 1
        part_1 = response.compliance_by_part_and_indicator[1]
        pv_1 = PartValidator(part_1)
        assert pv_0.check_reference()
        part_1_result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert pv_1.check_indicators(part_1_result)
        assert pv_1.check_empty_children(specifications=True, substances=True)
        assert pv_1.check_bom_structure()

        # Level 1: Child material
        material_1_0 = response.compliance_by_part_and_indicator[1].materials[0]
        mv_1_0 = MaterialValidator(material_1_0)
        assert mv_1_0.check_reference(record_history_identity="111111")
        material_1_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert mv_1_0.check_indicators(material_1_0_result)
        assert mv_1_0.check_empty_children()
        assert mv_1_0.check_bom_structure()

        # Level 2: Child substance
        substance_1_0_0 = response.compliance_by_part_and_indicator[1].materials[0].substances[0]
        sv_1_0_0 = SubstanceValidator(substance_1_0_0)
        assert sv_1_0_0.check_reference(record_history_identity="12345")
        substance_1_0_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_0_0.check_indicators(substance_1_0_0_result)
        assert sv_1_0_0.check_bom_structure()

    def test_compliance_by_indicator(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.compliance_by_indicator) == 2
        result = [indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold, indicators.RoHSFlag.RohsNonCompliant]
        assert all(
            [actual.flag == expected for actual, expected in zip(response.compliance_by_indicator.values(), result)]
        )

    def test_indicator_results_are_separate_objects(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        for result in response.compliance_by_part_and_indicator:
            for k, v in result.indicators.items():
                assert k in self.query._indicators  # The indicator name should be the same (string equality)
                assert v is not self.query._indicators[k]  # The indicator object should be a copy (non-identity)

    def test_query_result_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert repr(response) == "<BomComplianceQueryResult: 2 PartWithCompliance results>"

    def test_compliance_by_indicator_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        for indicator in response.compliance_by_indicator.keys():
            assert indicator in repr(response.compliance_by_indicator)

    def test_compliance_by_substance_and_indicator_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "PartWithComplianceResult" in repr(response.compliance_by_part_and_indicator)
