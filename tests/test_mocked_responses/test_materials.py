import pytest
from ansys.granta.bom_analytics import (
    MaterialImpactedSubstanceQuery,
    MaterialComplianceQuery,
    WatchListIndicator,
    RoHSIndicator,
)

from ansys.granta.bomanalytics.models import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsResponse,
)

from .common import check_substance, check_indicator


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "impacted_substances_api",
            "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials",
            GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsResponse,
        ]
    ],
    indirect=True,
)
class TestImpactedSubstances:
    query = MaterialImpactedSubstanceQuery().add_legislations(["Fake legislation"]).add_material_ids(["Fake ID"])

    def test_impacted_substances_by_material_and_legislation(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.impacted_substances_by_material_and_legislation) == 1
        mat_results = response.impacted_substances_by_material_and_legislation[0]
        assert mat_results.material_id == "elastomer-butadienerubber"
        legislations = mat_results.legislations
        assert len(legislations) == 1
        legislation = legislations["The SIN List 2.1 (Substitute It Now!)"]
        assert legislation.name == "The SIN List 2.1 (Substitute It Now!)"
        assert len(legislation.substances) == 2
        assert all([check_substance(s) for s in legislation.substances])

    def test_impacted_substances_by_legislation(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        assert all([check_substance(s) for s in legislation])

    def test_impacted_substances(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.impacted_substances) == 2
        assert all([check_substance(s) for s in response.impacted_substances])


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "compliance_api",
            "post_miservicelayer_bom_analytics_v1svc_compliance_materials",
            GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsResponse,
        ]
    ],
    indirect=True,
)
class TestCompliance:
    query = (
        MaterialComplianceQuery()
        .add_indicators(
            [
                WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .add_material_ids(["Fake ID"])
    )

    def test_compliance_by_material_and_indicator(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.compliance_by_material_and_indicator) == 2

        mat_0 = response.compliance_by_material_and_indicator[0]
        assert mat_0.material_id == "S200"
        assert not mat_0.record_guid
        assert not mat_0.record_history_guid
        assert not mat_0.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in mat_0.indicators.items())

        mat_1 = response.compliance_by_material_and_indicator[1]
        assert mat_1.record_guid == "3df206df-9fc8-4859-90d4-3519764f8b55"
        assert not mat_1.material_id
        assert not mat_1.record_history_guid
        assert not mat_1.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in mat_1.indicators.items())

    def test_compliance_by_material_and_indicator_substances(self, connection_mock):
        response = self.query.execute(connection_mock)

        substance_0_0 = response.compliance_by_material_and_indicator[0].substances[0]
        assert substance_0_0.record_history_identity == "12345"
        assert all(check_indicator(name, ind) for name, ind in substance_0_0.indicators.items())

        substance_1_0 = response.compliance_by_material_and_indicator[1].substances[0]
        assert substance_1_0.record_history_identity == "12345"
        assert all(check_indicator(name, ind) for name, ind in substance_1_0.indicators.items())

        substance_1_1 = response.compliance_by_material_and_indicator[1].substances[1]
        assert substance_1_1.record_history_identity == "34567"
        assert all(check_indicator(name, ind) for name, ind in substance_1_1.indicators.items())

    def test_compliance_by_indicator(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind) for name, ind in response.compliance_by_indicator.items())
