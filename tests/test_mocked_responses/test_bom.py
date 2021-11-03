from .common import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response,
    queries,
    indicators,
    get_mocked_response,
    PartValidator,
    SubstanceValidator,
)


class TestImpactedSubstances:
    query = queries.BomImpactedSubstancesQuery().with_legislations(["Fake legislation"]).with_bom("<Bom />")
    mock_key = GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response.__name__

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
    query = (
        queries.BomComplianceQuery()
        .with_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .with_bom("<Bom />")
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response.__name__

    def test_compliance_by_part_and_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_part_and_indicator) == 1

        # Top level item
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

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        result = [indicators.WatchListFlag.WatchListAllSubstancesBelowThreshold, indicators.RoHSFlag.RohsCompliant]
        assert all(
            [actual.flag == expected for actual, expected in zip(response.compliance_by_indicator.values(), result)]
        )

    def test_indicator_results_are_separate_objects(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        for result in response.compliance_by_part_and_indicator:
            for k, v in result.indicators.items():
                assert k in self.query._indicators  # The indicator name should be the same (string equality)
                assert v is not self.query._indicators[k]  # The indicator object should be a copy (non-identity)
