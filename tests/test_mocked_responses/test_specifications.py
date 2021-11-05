from .common import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse,
    queries,
    indicators,
    get_mocked_response,
    SpecificationValidator,
    CoatingValidator,
    MaterialValidator,
    SubstanceValidator,
)


class TestImpactedSubstances:
    query = (
        queries.SpecificationImpactedSubstancesQuery()
        .with_legislations(["Fake legislation"])
        .with_specification_ids(["Fake ID"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse.__name__

    def test_impacted_substances_by_specification_and_legislation(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances_by_specification_and_legislation) == 2

        spec_result_0 = response.impacted_substances_by_specification_and_legislation[0]
        specv_0 = SpecificationValidator(spec_result_0)
        assert specv_0.check_reference(record_history_identity="14321")
        assert len(spec_result_0.legislations) == 1
        substances_0 = spec_result_0.legislations["The SIN List 2.1 (Substitute It Now!)"].substances
        assert len(substances_0) == 2
        for substance in substances_0:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()

        spec_result_1 = response.impacted_substances_by_specification_and_legislation[1]
        specv_1 = SpecificationValidator(spec_result_1)
        assert specv_1.check_reference(specification_id="MSP89,TypeI")
        assert len(spec_result_1.legislations) == 1
        substances_1 = spec_result_1.legislations["The SIN List 2.1 (Substitute It Now!)"].substances
        assert len(substances_1) == 2
        for substance in substances_1:
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
        assert len(response.impacted_substances) == 4
        for substance in response.impacted_substances:
            sv = SubstanceValidator(substance)
            sv.check_substance_details()


class TestCompliance:
    """Check that each mocked result has the correct record references, indicator results, child objects, and bom
    relationships.

    A mocked query is used, populated by the examples included in the API definition.

    Spec, coating, material and substance details are verified in separate methods.
    """

    query = (
        queries.SpecificationComplianceQuery()
        .with_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .with_specification_ids(["Fake ID"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse.__name__

    def test_compliance_by_specification_and_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_specification_and_indicator) == 2

        spec_0 = response.compliance_by_specification_and_indicator[0]
        specv_0 = SpecificationValidator(spec_0)
        assert specv_0.check_reference(specification_id="MSP89,TypeI")
        spec_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert specv_0.check_indicators(spec_0_result)
        assert specv_0.check_bom_structure()
        assert specv_0.check_empty_children(materials=True, substances=True)

        spec_0_0 = spec_0.specifications[0]
        specv_0_0 = SpecificationValidator(spec_0_0)
        assert specv_0_0.check_reference(record_history_identity="987654")
        specv_0_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert specv_0_0.check_indicators(specv_0_0_result)
        assert specv_0_0.check_bom_structure()
        assert specv_0_0.check_empty_children(materials=True, specifications=True, coatings=True)

        spec_1 = response.compliance_by_specification_and_indicator[1]
        specv_1 = SpecificationValidator(spec_1)
        assert specv_1.check_reference(record_guid="3df206df-9fc8-4859-90d4-3519764f8b55")
        spec_1_result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert specv_1.check_indicators(spec_1_result)
        assert specv_1.check_bom_structure()
        assert specv_1.check_empty_children(specifications=True, coatings=True)

    def test_compliance_by_specification_and_indicator_materials(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        coating_0_0 = response.compliance_by_specification_and_indicator[0].coatings[0]
        cv_0_0 = CoatingValidator(coating_0_0)
        assert cv_0_0.check_reference(record_history_identity="987654")
        coating_0_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert cv_0_0.check_indicators(coating_0_0_result)
        assert cv_0_0.check_bom_structure()
        assert cv_0_0.check_empty_children()

    def test_compliance_by_specification_and_indicator_coatings(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        material_1_0 = response.compliance_by_specification_and_indicator[1].materials[0]
        mv_1_0 = MaterialValidator(material_1_0)
        assert mv_1_0.check_reference(record_history_identity="111111")
        material_1_0_result = [
            indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold,
            indicators.RoHSFlag.RohsCompliant,
        ]
        assert mv_1_0.check_indicators(material_1_0_result)
        assert mv_1_0.check_bom_structure()
        assert mv_1_0.check_empty_children()

    def test_compliance_by_specification_and_indicator_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        substance_0_coating_0_0 = response.compliance_by_specification_and_indicator[0].coatings[0].substances[0]
        sv_0_0_0 = SubstanceValidator(substance_0_coating_0_0)
        assert sv_0_0_0.check_reference(record_history_identity="62345")
        substance_0_0_result = [
            indicators.WatchListFlag.WatchListNotImpacted,
            indicators.RoHSFlag.RohsNotImpacted,
        ]
        assert sv_0_0_0.check_indicators(substance_0_0_result)
        assert sv_0_0_0.check_bom_structure()

        substance_1_0 = response.compliance_by_specification_and_indicator[1].substances[0]
        sv_1_0 = SubstanceValidator(substance_1_0)
        assert sv_1_0.check_reference(record_history_identity="12345")
        substance_1_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_0.check_indicators(substance_1_0_result)
        assert sv_1_0.check_bom_structure()

        substance_1_1 = response.compliance_by_specification_and_indicator[1].substances[1]
        sv_1_1 = SubstanceValidator(substance_1_1)
        assert sv_1_1.check_reference(record_history_identity="34567")
        substance_1_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert sv_1_1.check_indicators(substance_1_1_result)
        assert sv_1_1.check_bom_structure()

        substance_1_material_0_0 = response.compliance_by_specification_and_indicator[1].materials[0].substances[0]
        sv_1_0_0 = SubstanceValidator(substance_1_material_0_0)
        assert sv_1_0_0.check_reference(record_history_identity="12345")
        substance_1_0_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_0_0.check_indicators(substance_1_0_0_result)
        assert sv_1_0_0.check_bom_structure()

        substance_1_material_1_0 = response.compliance_by_specification_and_indicator[1].materials[1].substances[0]
        sv_1_1_0 = SubstanceValidator(substance_1_material_1_0)
        assert sv_1_1_0.check_reference(record_history_identity="12345")
        substance_1_1_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_1_1_0.check_indicators(substance_1_1_0_result)
        assert sv_1_1_0.check_bom_structure()

        substance_1_material_1_1 = response.compliance_by_specification_and_indicator[1].materials[1].substances[1]
        sv_1_1_1 = SubstanceValidator(substance_1_material_1_1)
        assert sv_1_1_1.check_reference(record_history_identity="34567")
        substance_1_1_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert sv_1_1_1.check_indicators(substance_1_1_1_result)
        assert sv_1_1_1.check_bom_structure()

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        result = [
            indicators.WatchListFlag.WatchListHasSubstanceAboveThreshold,
            indicators.RoHSFlag.RohsNonCompliant,
        ]
        assert all(
            [actual.flag == expected for actual, expected in zip(response.compliance_by_indicator.values(), result)]
        )

    def test_indicator_results_are_separate_objects(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        for result in response.compliance_by_specification_and_indicator:
            for k, v in result.indicators.items():
                assert k in self.query._indicators  # The indicator name should be the same (string equality)
                assert v is not self.query._indicators[k]  # The indicator object should be a copy (non-identity)
