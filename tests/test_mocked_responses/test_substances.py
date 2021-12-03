from .common import (
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesResponse,
    queries,
    indicators,
    get_mocked_response,
    SubstanceValidator,
)


class TestCompliance:
    """Check that each mocked result has the correct record references, indicator results, child objects, and bom
    relationships.

    A mocked query is used, populated by the examples included in the API definition.
    """

    query = (
        queries.SubstanceComplianceQuery()
        .with_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .with_cas_numbers(["Fake ID"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesResponse.__name__

    def test_compliance_by_substance_and_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_substance_and_indicator) == 2

        substance_0 = response.compliance_by_substance_and_indicator[0]
        sv_0 = SubstanceValidator(substance_0)
        assert sv_0.check_reference(cas_number="50-00-0")
        substance_0_result = [
            indicators.WatchListFlag.WatchListBelowThreshold,
            indicators.RoHSFlag.RohsBelowThreshold,
        ]
        assert sv_0.check_indicators(substance_0_result)
        assert sv_0.check_bom_structure()

        substance_1 = response.compliance_by_substance_and_indicator[1]
        sv_1 = SubstanceValidator(substance_1)
        assert sv_1.check_reference(chemical_name="1,3-Butadiene")
        substance_1_result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert sv_1.check_indicators(substance_1_result)
        assert sv_1.check_bom_structure()

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        result = [
            indicators.WatchListFlag.WatchListAboveThreshold,
            indicators.RoHSFlag.RohsAboveThreshold,
        ]
        assert all(
            [actual.flag == expected for actual, expected in zip(response.compliance_by_indicator.values(), result)]
        )

    def test_indicator_results_are_separate_objects(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        for result in response.compliance_by_substance_and_indicator:
            for k, v in result.indicators.items():
                assert k in self.query._indicators  # The indicator name should be the same (string equality)
                assert v is not self.query._indicators[k]  # The indicator object should be a copy (non-identity)

    def test_query_result_repr(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert repr(response) == '<SubstanceComplianceQueryResult: 2 SubstanceWithCompliance results>'

    def test_compliance_by_indicator_repr(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        for indicator in response.compliance_by_indicator.keys():
            assert indicator in repr(response.compliance_by_indicator)

    def test_compliance_by_substance_and_indicator_repr(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert "SubstanceWithComplianceResult" in repr(response.compliance_by_substance_and_indicator)
