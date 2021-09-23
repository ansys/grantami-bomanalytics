import pytest
from ansys.granta.bom_analytics import (
    PartImpactedSubstanceQuery,
    PartComplianceQuery,
    WatchListIndicator,
    RoHSIndicator,
)

from ansys.granta.bomanalytics.models import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsResponse,
)


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "impacted_substances_api",
            "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts",
            GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsResponse,
        ]
    ],
    indirect=True,
)
def test_impacted_substances(connection_mock):
    response = (
        PartImpactedSubstanceQuery()
        .add_legislations(["Fake legislation"])
        .add_part_numbers(["Fake part number"])
        .execute(connection_mock)
    )

    # Check full response
    assert len(response.impacted_substances_by_part_and_legislation) == 2
    part_0 = response.impacted_substances_by_part_and_legislation[0]
    assert part_0.record_history_identity == "14321"
    assert len(part_0.legislations) == 1
    part_0_legislation = part_0.legislations["The SIN List 2.1 (Substitute It Now!)"]
    assert part_0_legislation.name == "The SIN List 2.1 (Substitute It Now!)"
    assert len(part_0_legislation.substances) == 2
    validate_substance(part_0_legislation.substances[0], ("106-99-0", "203-450-8", "1,3-Butadiene", None, 0.1))
    validate_substance(
        part_0_legislation.substances[1], ("128-37-0", "204-881-4", "Butylated hydroxytoluene [BAN:NF]", None, 0.1)
    )

    part_1 = response.impacted_substances_by_part_and_legislation[1]
    assert part_1.part_number == "AF-1235"
    assert len(part_1.legislations) == 1
    part_1_legislation = part_1.legislations["The SIN List 2.1 (Substitute It Now!)"]
    assert part_1_legislation.name == "The SIN List 2.1 (Substitute It Now!)"
    assert len(part_1_legislation.substances) == 2
    validate_substance(part_1_legislation.substances[0], ("119-61-9", "204-337-6", "Benzophenone", 1.0, 0.1))
    validate_substance(
        part_1_legislation.substances[1], ("131-56-6", "205-029-4", "2,4-Dihydroxybenzophenon", 1.0, 0.1)
    )

    # Check pivot rolled up to legislations
    assert len(response.impacted_substances_by_legislation) == 1
    legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
    validate_substance(legislation[0], ("106-99-0", "203-450-8", "1,3-Butadiene", None, 0.1))
    validate_substance(legislation[1], ("128-37-0", "204-881-4", "Butylated hydroxytoluene [BAN:NF]", None, 0.1))
    validate_substance(legislation[2], ("119-61-9", "204-337-6", "Benzophenone", 1.0, 0.1))
    validate_substance(legislation[3], ("131-56-6", "205-029-4", "2,4-Dihydroxybenzophenon", 1.0, 0.1))

    # Check pivot rolled-up to substances
    assert len(response.impacted_substances) == 4
    validate_substance(response.impacted_substances[0], ("106-99-0", "203-450-8", "1,3-Butadiene", None, 0.1))
    validate_substance(
        response.impacted_substances[1], ("128-37-0", "204-881-4", "Butylated hydroxytoluene [BAN:NF]", None, 0.1)
    )
    validate_substance(response.impacted_substances[2], ("119-61-9", "204-337-6", "Benzophenone", 1.0, 0.1))
    validate_substance(response.impacted_substances[3], ("131-56-6", "205-029-4", "2,4-Dihydroxybenzophenon", 1.0, 0.1))


def validate_substance(substance, params):
    assert substance.cas_number == params[0]
    assert substance.ec_number == params[1]
    assert substance.chemical_name == params[2]
    assert substance.max_percentage_amount_in_material == params[3]
    assert substance.legislation_threshold == params[4]


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "compliance_api",
            "post_miservicelayer_bom_analytics_v1svc_compliance_parts",
            GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsResponse,
        ]
    ],
    indirect=True,
)
def test_compliance(connection_mock):
    response = (
        PartComplianceQuery()
        .add_indicators(
            [
                WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .add_part_numbers(["Fake part number"])
        .execute(connection_mock)
    )

    # Check full response
    assert len(response.compliance_by_part_and_indicator) == 2
    part_0 = response.compliance_by_part_and_indicator[0]
    assert part_0.part_number == "AF-1235"
    assert not part_0.record_guid
    assert not part_0.record_history_guid
    assert not part_0.record_history_identity

    assert part_0.indicators["Indicator 1"].name == "Indicator 1"
    assert part_0.indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_0.indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_0.indicators["Indicator 2"].name == "Indicator 2"
    assert part_0.indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_0.indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert part_0.parts[0].record_history_identity == "987654"
    assert part_0.parts[0].indicators["Indicator 1"].name == "Indicator 1"
    assert part_0.parts[0].indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_0.parts[0].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_0.parts[0].indicators["Indicator 2"].name == "Indicator 2"
    assert part_0.parts[0].indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_0.parts[0].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert part_0.parts[0].substances[0].record_history_identity == "62345"
    assert part_0.parts[0].substances[0].indicators["Indicator 1"].name == "Indicator 1"
    assert part_0.parts[0].substances[0].indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_0.parts[0].substances[0].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_0.parts[0].substances[0].indicators["Indicator 2"].name == "Indicator 2"
    assert part_0.parts[0].substances[0].indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_0.parts[0].substances[0].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    part_1 = response.compliance_by_part_and_indicator[1]
    assert part_1.record_guid == "3df206df-9fc8-4859-90d4-3519764f8b55"
    assert not part_1.part_number
    assert not part_1.record_history_guid
    assert not part_1.record_history_identity

    assert part_1.indicators["Indicator 1"].name == "Indicator 1"
    assert part_1.indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_1.indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_1.indicators["Indicator 2"].name == "Indicator 2"
    assert part_1.indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_1.indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert part_1.materials[0].record_history_identity == "111111"
    assert part_1.materials[0].indicators["Indicator 1"].name == "Indicator 1"
    assert part_1.materials[0].indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_1.materials[0].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_1.materials[0].indicators["Indicator 2"].name == "Indicator 2"
    assert part_1.materials[0].indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_1.materials[0].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert part_1.materials[0].substances[0].record_history_identity == "12345"
    assert part_1.materials[0].substances[0].indicators["Indicator 1"].name == "Indicator 1"
    assert part_1.materials[0].substances[0].indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_1.materials[0].substances[0].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_1.materials[0].substances[0].indicators["Indicator 2"].name == "Indicator 2"
    assert part_1.materials[0].substances[0].indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_1.materials[0].substances[0].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert part_1.materials[1].record_history_identity == "222222"
    assert part_1.materials[1].indicators["Indicator 1"].name == "Indicator 1"
    assert part_1.materials[1].indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_1.materials[1].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_1.materials[1].indicators["Indicator 2"].name == "Indicator 2"
    assert part_1.materials[1].indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_1.materials[1].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert part_1.materials[1].substances[0].record_history_identity == "12345"
    assert part_1.materials[1].substances[0].indicators["Indicator 1"].name == "Indicator 1"
    assert part_1.materials[1].substances[0].indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_1.materials[1].substances[0].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_1.materials[1].substances[0].indicators["Indicator 2"].name == "Indicator 2"
    assert part_1.materials[1].substances[0].indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_1.materials[1].substances[0].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

    assert part_1.materials[1].substances[1].record_history_identity == "34567"
    assert part_1.materials[1].substances[1].indicators["Indicator 1"].name == "Indicator 1"
    assert part_1.materials[1].substances[1].indicators["Indicator 1"].legislation_names == ["Mock"]
    assert part_1.materials[1].substances[1].indicators["Indicator 1"].flag.name == "WatchListAboveThreshold"
    assert part_1.materials[1].substances[1].indicators["Indicator 2"].name == "Indicator 2"
    assert part_1.materials[1].substances[1].indicators["Indicator 2"].legislation_names == ["Mock"]
    assert part_1.materials[1].substances[1].indicators["Indicator 2"].flag.name == "RohsAboveThreshold"

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
