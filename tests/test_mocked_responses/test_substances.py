from .common import (
    pytest,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesResponse,
    queries,
    indicators,
    check_indicator,
)


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "compliance_api",
            "post_miservicelayer_bom_analytics_v1svc_compliance_substances",
            GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesResponse,
        ]
    ],
    indirect=True,
)
class TestCompliance:
    query = (
        queries.SubstanceCompliance()
        .add_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .add_cas_numbers(["Fake ID"])
    )

    def test_compliance_by_substance_and_indicator(self, connection_mock):
        response = self.query.execute(connection_mock)
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

    def test_compliance_by_indicator(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind) for name, ind in response.compliance_by_indicator.items())
