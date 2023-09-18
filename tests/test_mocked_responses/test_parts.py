from ansys.grantami.bomanalytics import queries, indicators
from ansys.grantami.bomanalytics_openapi.models import (
    GetImpactedSubstancesForPartsResponse,
    GetComplianceForPartsResponse,
)
from .common import (
    BaseMockTester,
    PartValidator,
    SpecificationValidator,
    MaterialValidator,
    SubstanceValidator,
)


class TestImpactedSubstances(BaseMockTester):
    query = (
        queries.PartImpactedSubstancesQuery()
        .with_legislations(["Fake legislation"])
        .with_part_numbers(["Fake part number"])
    )
    mock_key = GetImpactedSubstancesForPartsResponse.__name__

    def test_impacted_substances_by_part(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        assert len(response.impacted_substances_by_part) == 2
        part_0 = response.impacted_substances_by_part[0]
        pv_0 = PartValidator(part_0)
        pv_0.check_reference(record_history_identity="14321")

        # Test flattened list of substances
        assert len(part_0.substances) == 2
        for substance in part_0.substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

        # Test list of substances grouped by legislations
        assert len(part_0.substances_by_legislation) == 1
        part_0_substances = part_0.substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        assert len(part_0_substances) == 2
        for substance in part_0_substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

        part_1 = response.impacted_substances_by_part[1]
        pv_1 = PartValidator(part_1)
        pv_1.check_reference(part_number="AF-1235")

        # Test flattened list of substances
        assert len(part_1.substances) == 2
        for substance in part_1.substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

        # Test list of substances grouped by legislations
        assert len(part_1.substances_by_legislation) == 1
        part_1_substances = part_1.substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        assert len(part_1_substances) == 2
        for substance in part_1_substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_impacted_substances_by_legislation(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        for substance in legislation:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_impacted_substances(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.impacted_substances) == 4
        for substance in response.impacted_substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

    def test_query_result_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert repr(response) == "<PartImpactedSubstancesQueryResult: 2 PartWithImpactedSubstances results>"

    def test_impacted_substances_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "ImpactedSubstance" in repr(response.impacted_substances)

    def test_impacted_substances_by_part_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "PartWithImpactedSubstancesResult" in repr(response.impacted_substances_by_part)

    def test_impacted_substances_by_legislation_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        for legislation in response.impacted_substances_by_legislation.keys():
            assert legislation in repr(response.impacted_substances_by_legislation)
        assert "ImpactedSubstance" in repr(response.impacted_substances_by_legislation)


class TestCompliance(BaseMockTester):
    """Check that each mocked result has the correct record references, indicator results, child objects, and bom
    relationships.

    A mocked query is used, populated by the examples included in the API definition.

    Part, spec, material and substance details are verified in separate methods.
    """

    query = (
        queries.PartComplianceQuery()
        .with_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_ids=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_ids=["Mock"]),
            ]
        )
        .with_part_numbers(["Fake part number"])
    )
    mock_key = GetComplianceForPartsResponse.__name__

    def test_compliance_by_part_and_indicator(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.compliance_by_part_and_indicator) == 2

        # Part 0
        part_0 = response.compliance_by_part_and_indicator[0]
        pv_0 = PartValidator(part_0)
        assert pv_0.check_reference(part_number="FLRY33")
        part_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert pv_0.check_indicators(part_0_result)
        assert pv_0.check_empty_children(substances=True, materials=True)
        assert pv_0.check_bom_structure()

        # Part 0, child part 0
        part_0_0 = part_0.parts[0]
        pv_0_0 = PartValidator(part_0_0)
        assert pv_0_0.check_reference(record_history_identity="987654")
        part_0_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert pv_0_0.check_indicators(part_0_0_result)
        assert pv_0_0.check_empty_children(parts=True, specifications=True, materials=True)
        assert pv_0_0.check_bom_structure()

        # Part 1
        part_1 = response.compliance_by_part_and_indicator[1]
        pv_1 = PartValidator(part_1)
        assert pv_1.check_reference(record_guid="f622cc99-158d-43eb-881e-209a08af1108")
        part_1_result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert pv_1.check_indicators(part_1_result)
        assert pv_1.check_empty_children(parts=True, specifications=True)
        assert pv_1.check_bom_structure()

    def test_compliance_by_part_and_indicator_specs(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        spec = response.compliance_by_part_and_indicator[0].specifications[0]
        sv = SpecificationValidator(spec)
        assert sv.check_reference(record_history_identity="987654")
        spec_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert sv.check_indicators(spec_result)
        assert sv.check_empty_children(coatings=True, materials=True, specifications=True)
        assert sv.check_bom_structure()

    def test_compliance_by_part_and_indicator_materials(self, mock_connection):
        response = self.get_mocked_response(mock_connection)

        material_1_0 = response.compliance_by_part_and_indicator[1].materials[0]
        mv_1_0 = MaterialValidator(material_1_0)
        assert mv_1_0.check_reference(record_history_identity="111111")
        material_1_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert mv_1_0.check_indicators(material_1_0_result)
        assert mv_1_0.check_bom_structure()

        material_1_1 = response.compliance_by_part_and_indicator[1].materials[1]
        mv_1_1 = MaterialValidator(material_1_1)
        assert mv_1_1.check_reference(record_history_identity="222222")
        material_1_1_result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert mv_1_1.check_indicators(material_1_1_result)
        assert mv_1_1.check_bom_structure()

    def test_compliance_by_part_and_indicator_substances(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        part_0_0_substance_0 = response.compliance_by_part_and_indicator[0].parts[0].substances[0]
        part_0_0_sv_0 = SubstanceValidator(part_0_0_substance_0)
        assert part_0_0_sv_0.check_reference(record_history_identity="62345")
        part_0_0_substance_0_result = [
            indicators.WatchListFlag.WatchListNotImpacted,
            indicators.RoHSFlag.RohsNotImpacted,
        ]
        assert part_0_0_sv_0.check_indicators(part_0_0_substance_0_result)
        assert part_0_0_sv_0.check_bom_structure()

        spec_substance_0 = response.compliance_by_part_and_indicator[0].specifications[0].substances[0]
        spec_sv_0 = SubstanceValidator(spec_substance_0)
        assert spec_sv_0.check_reference(record_history_identity="12345")
        spec_substance_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert spec_sv_0.check_indicators(spec_substance_0_result)
        assert spec_sv_0.check_bom_structure()

        part_1_material_0_substance_0 = response.compliance_by_part_and_indicator[1].materials[0].substances[0]
        part_1_material_0_sv_0 = SubstanceValidator(part_1_material_0_substance_0)
        assert part_1_material_0_sv_0.check_reference(record_history_identity="12345")
        part_1_material_0_substance_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert part_1_material_0_sv_0.check_indicators(part_1_material_0_substance_0_result)
        assert part_1_material_0_sv_0.check_bom_structure()

        part_1_material_1_substance_0 = response.compliance_by_part_and_indicator[1].materials[1].substances[0]
        part_1_material_1_sv_0 = SubstanceValidator(part_1_material_1_substance_0)
        assert part_1_material_1_sv_0.check_reference(record_history_identity="12345")
        part_1_material_1_substance_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert part_1_material_1_sv_0.check_indicators(part_1_material_1_substance_0_result)
        assert part_1_material_1_sv_0.check_bom_structure()

        part_1_material_1_substance_1 = response.compliance_by_part_and_indicator[1].materials[1].substances[1]
        part_1_material_1_sv_1 = SubstanceValidator(part_1_material_1_substance_1)
        assert part_1_material_1_sv_1.check_reference(record_history_identity="34567")
        part_1_material_1_substance_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert part_1_material_1_sv_1.check_indicators(part_1_material_1_substance_1_result)
        assert part_1_material_1_sv_1.check_bom_structure()

        part_1_substance_0 = response.compliance_by_part_and_indicator[1].substances[0]
        part_1_sv_0 = SubstanceValidator(part_1_substance_0)
        assert part_1_sv_0.check_reference(record_history_identity="12345")
        part_1_substance_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert part_1_sv_0.check_indicators(part_1_substance_0_result)
        assert part_1_sv_0.check_bom_structure()

        part_1_substance_1 = response.compliance_by_part_and_indicator[1].substances[1]
        part_1_sv_1 = SubstanceValidator(part_1_substance_1)
        assert part_1_sv_1.check_reference(record_history_identity="34567")
        part_1_substance_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert part_1_sv_1.check_indicators(part_1_substance_1_result)
        assert part_1_sv_1.check_bom_structure()

    def test_compliance_by_indicator(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert len(response.compliance_by_indicator) == 2
        result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
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
        assert repr(response) == "<PartComplianceQueryResult: 2 PartWithCompliance results>"

    def test_compliance_by_indicator_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        for indicator in response.compliance_by_indicator.keys():
            assert indicator in repr(response.compliance_by_indicator)

    def test_compliance_by_part_and_indicator_repr(self, mock_connection):
        response = self.get_mocked_response(mock_connection)
        assert "PartWithComplianceResult" in repr(response.compliance_by_part_and_indicator)
