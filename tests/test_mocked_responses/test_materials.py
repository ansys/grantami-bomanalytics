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
def test_impacted_substances(connection_mock):
    response = (
        MaterialImpactedSubstanceQuery()
        .add_legislations(["Fake legislation"])
        .add_material_ids(["Fake ID"])
        .execute(connection_mock)
    )

    # Check full response
    assert len(response.impacted_substances_by_material_and_legislation) == 1
    mat_results = response.impacted_substances_by_material_and_legislation[0]
    assert mat_results.material_id == "elastomer-butadienerubber"
    legislations = mat_results.legislations
    assert len(legislations) == 1
    legislation = legislations["The SIN List 2.1 (Substitute It Now!)"]
    assert legislation.name == "The SIN List 2.1 (Substitute It Now!)"
    assert len(legislation.substances) == 2
    validate_substances(legislation.substances)

    # Check pivot rolled up to legislations
    assert len(response.impacted_substances_by_legislation) == 1
    legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
    validate_substances(legislation)

    # Check pivot rolled-up to substances
    assert len(response.impacted_substances) == 2
    validate_substances(response.impacted_substances)


def validate_substances(substances):
    assert substances[0].cas_number == "106-99-0"
    assert substances[0].ec_number == "203-450-8"
    assert substances[0].chemical_name == "1,3-Butadiene"

    assert substances[1].cas_number == "128-37-0"
    assert substances[1].ec_number == "204-881-4"
    assert substances[1].chemical_name == "Butylated hydroxytoluene [BAN:NF]"
    assert substances[1].legislation_threshold == 0.1


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
def test_compliance(connection_mock):
    response = (
        MaterialComplianceQuery()
        .add_indicators(
            [
                WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .add_material_ids(["Fake ID"])
        .execute(connection_mock)
    )

    # Check full response
    assert len(response.compliance_by_material_and_indicator) == 2
    mat_0 = response.compliance_by_material_and_indicator[0]
    assert mat_0.material_id == "S200"
    assert not mat_0.record_guid
    assert not mat_0.record_history_guid
    assert not mat_0.record_history_identity

    assert mat_0.indicators["Indicator 1"].name == "Indicator 1"
    assert mat_0.indicators["Indicator 1"].legislation_names == ["Mock"]
    assert mat_0.indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert mat_0.indicators["Indicator 2"].name == "Indicator 2"
    assert mat_0.indicators["Indicator 2"].legislation_names == ["Mock"]
    assert mat_0.indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert mat_0.substances[0].record_history_identity == "12345"
    assert mat_0.substances[0].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert mat_0.substances[0].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    mat_1 = response.compliance_by_material_and_indicator[1]
    assert mat_1.record_guid == "3df206df-9fc8-4859-90d4-3519764f8b55"
    assert not mat_1.material_id
    assert not mat_1.record_history_guid
    assert not mat_1.record_history_identity

    assert mat_1.indicators["Indicator 1"].name == "Indicator 1"
    assert mat_1.indicators["Indicator 1"].legislation_names == ["Mock"]
    assert mat_1.indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert mat_1.indicators["Indicator 2"].name == "Indicator 2"
    assert mat_1.indicators["Indicator 2"].legislation_names == ["Mock"]
    assert mat_1.indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert mat_1.substances[0].record_history_identity == "12345"
    assert mat_1.substances[0].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert mat_1.substances[0].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert mat_1.substances[1].record_history_identity == "34567"
    assert mat_1.substances[1].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert mat_1.substances[1].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    # Check rollup by indicator
    assert len(response.compliance_by_indicator) == 2
    indicator_1 = response.compliance_by_indicator["Indicator 1"]
    assert indicator_1.name == "Indicator 1"
    assert indicator_1.flag.name == "WatchListAboveThreshold"
    assert indicator_1.legislation_names == ["Mock"]

    indicator_2 = response.compliance_by_indicator["Indicator 2"]
    assert indicator_2.name == "Indicator 2"
    assert indicator_2.flag.name == "RohsAboveThreshold"
    assert indicator_2.legislation_names == ["Mock"]
