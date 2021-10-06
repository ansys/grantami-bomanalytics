from .common import (
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesResponse,
    queries,
    indicators,
    check_indicator,
    get_mocked_response,
    check_substance_attributes,
)


class TestCompliance:
    query = (
        queries.SubstanceCompliance()
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
        assert substance_0.cas_number == "50-00-0"
        assert not substance_0.ec_number
        assert not substance_0.chemical_name
        assert not substance_0.record_guid
        assert not substance_0.record_history_guid
        assert not substance_0.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in substance_0.indicators.items())

        substance_1 = response.compliance_by_substance_and_indicator[1]
        assert substance_1.chemical_name == "1,3-Butadiene"
        assert not substance_1.ec_number
        assert not substance_1.cas_number
        assert not substance_1.record_guid
        assert not substance_1.record_history_guid
        assert not substance_1.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in substance_1.indicators.items())

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind) for name, ind in response.compliance_by_indicator.items())

    def test_compliance_result_objects(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        assert all(
            [check_substance_attributes(sub) for sub in response.compliance_by_substance_and_indicator]
        )
