import pytest
from ansys.granta.bom_analytics import (
    SpecificationImpactedSubstanceQuery,
    SpecificationComplianceQuery,
    WatchListIndicator,
    RoHSIndicator,
)

from ansys.granta.bomanalytics.models import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse,
)
from .common import check_substance, check_indicator


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "impacted_substances_api",
            "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications",
            GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse,
        ]
    ],
    indirect=True,
)
class TestImpactedSubstances:
    query = (
        SpecificationImpactedSubstanceQuery()
        .add_legislations(["Fake legislation"])
        .add_specification_ids(["Fake ID"])
    )

    def test_full_response(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.impacted_substances_by_specification_and_legislation) == 2

        spec_result_0 = response.impacted_substances_by_specification_and_legislation[0]
        assert spec_result_0.record_history_identity == "14321"
        assert len(spec_result_0.legislations) == 1
        substances_0 = spec_result_0.legislations["The SIN List 2.1 (Substitute It Now!)"].substances
        assert len(substances_0) == 2
        assert all([check_substance(s) for s in substances_0])

        spec_result_1 = response.impacted_substances_by_specification_and_legislation[1]
        assert spec_result_1.specification_id == "MSP89,TypeI"
        assert len(spec_result_1.legislations) == 1
        substances_1 = spec_result_1.legislations["The SIN List 2.1 (Substitute It Now!)"].substances
        assert len(substances_1) == 2
        assert all([check_substance(s) for s in substances_1])

    def test_legislation_pivot(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        assert all([check_substance(s) for s in legislation])

    def test_substance_pivot(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.impacted_substances) == 4
        assert all([check_substance(s) for s in response.impacted_substances])


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "compliance_api",
            "post_miservicelayer_bom_analytics_v1svc_compliance_specifications",
            GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse,
        ]
    ],
    indirect=True,
)
class TestCompliance:
    query = (
        SpecificationComplianceQuery()
            .add_indicators(
            [
                WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .add_specification_ids(["Fake ID"])
    )

    def test_full_response_specs(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.compliance_by_specification_and_indicator) == 2

        spec_0 = response.compliance_by_specification_and_indicator[0]
        assert spec_0.specification_id == "MSP89,TypeI"
        assert not spec_0.record_guid
        assert not spec_0.record_history_guid
        assert not spec_0.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in spec_0.indicators.items())

        spec_1 = response.compliance_by_specification_and_indicator[1]
        assert not spec_1.specification_id
        assert spec_1.record_guid == '3df206df-9fc8-4859-90d4-3519764f8b55'
        assert not spec_1.record_history_guid
        assert not spec_1.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in spec_1.indicators.items())

    def test_full_response_substances(self, connection_mock):
        response = self.query.execute(connection_mock)

        substance_1_0 = response.compliance_by_specification_and_indicator[1].substances[0]
        assert substance_1_0.record_history_identity == '12345'
        assert all(check_indicator(name, ind) for name, ind in substance_1_0.indicators.items())

        substance_1_1 = response.compliance_by_specification_and_indicator[1].substances[1]
        assert substance_1_1.record_history_identity == '34567'
        assert all(check_indicator(name, ind) for name, ind in substance_1_1.indicators.items())

    def test_indicator_pivot(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind) for name, ind in response.compliance_by_indicator.items())
