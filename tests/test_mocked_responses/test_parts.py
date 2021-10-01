from .common import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsResponse,
    queries,
    indicators,
    check_substance,
    check_indicator,
    get_mocked_response,
)


class TestImpactedSubstances:
    query = queries.PartImpactedSubstances().add_legislations(["Fake legislation"]).add_part_numbers(["Fake part number"])
    mock_key = GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsResponse.__name__

    def test_impacted_substances_by_part_and_legislation(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        assert len(response.impacted_substances_by_part_and_legislation) == 2
        part_0 = response.impacted_substances_by_part_and_legislation[0]
        assert part_0.record_history_identity == "14321"
        assert len(part_0.legislations) == 1
        part_0_legislation = part_0.legislations["The SIN List 2.1 (Substitute It Now!)"]
        assert part_0_legislation.name == "The SIN List 2.1 (Substitute It Now!)"
        assert len(part_0_legislation.substances) == 2
        assert all([check_substance(s) for s in part_0_legislation.substances])

        part_1 = response.impacted_substances_by_part_and_legislation[1]
        assert part_1.part_number == "AF-1235"
        assert len(part_1.legislations) == 1
        part_1_legislation = part_1.legislations["The SIN List 2.1 (Substitute It Now!)"]
        assert part_1_legislation.name == "The SIN List 2.1 (Substitute It Now!)"
        assert len(part_1_legislation.substances) == 2
        assert all([check_substance(s) for s in part_1_legislation.substances])

    def test_impacted_substances_by_legislation(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        assert all([check_substance(s) for s in legislation])

    def test_impacted_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances) == 4
        assert all([check_substance(s) for s in response.impacted_substances])


class TestCompliance:
    query = (
        queries.PartCompliance()
        .add_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .add_part_numbers(["Fake part number"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsResponse.__name__

    def test_compliance_by_part_and_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_part_and_indicator) == 2
        part_0 = response.compliance_by_part_and_indicator[0]
        assert part_0.part_number == "AF-1235"
        assert not part_0.record_guid
        assert not part_0.record_history_guid
        assert not part_0.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in part_0.indicators.items())

        part_0_0 = part_0.parts[0]
        assert part_0_0.record_history_identity == "987654"
        assert all(check_indicator(name, ind) for name, ind in part_0_0.indicators.items())

        part_1 = response.compliance_by_part_and_indicator[1]
        assert part_1.record_guid == "3df206df-9fc8-4859-90d4-3519764f8b55"
        assert not part_1.part_number
        assert not part_1.record_history_guid
        assert not part_1.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in part_1.indicators.items())

        material_1_0 = part_1.materials[0]
        assert material_1_0.record_history_identity == "111111"
        assert all(check_indicator(name, ind) for name, ind in material_1_0.indicators.items())
        material_1_1 = part_1.materials[1]
        assert material_1_1.record_history_identity == "222222"
        assert all(check_indicator(name, ind) for name, ind in material_1_1.indicators.items())

    def test_compliance_by_part_and_indicator_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        substance_0_0_0 = response.compliance_by_part_and_indicator[0].parts[0].substances[0]
        assert substance_0_0_0.record_history_identity == "62345"
        assert all(check_indicator(name, ind) for name, ind in substance_0_0_0.indicators.items())

        substance_1_0_0 = response.compliance_by_part_and_indicator[1].materials[0].substances[0]
        assert substance_1_0_0.record_history_identity == "12345"
        assert all(check_indicator(name, ind) for name, ind in substance_1_0_0.indicators.items())

        substance_1_1_0 = response.compliance_by_part_and_indicator[1].materials[1].substances[0]
        assert substance_1_1_0.record_history_identity == "12345"
        assert all(check_indicator(name, ind) for name, ind in substance_1_1_0.indicators.items())

        substance_1_1_1 = response.compliance_by_part_and_indicator[1].materials[1].substances[1]
        assert substance_1_1_1.record_history_identity == "34567"
        assert all(check_indicator(name, ind) for name, ind in substance_1_1_1.indicators.items())

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind) for name, ind in response.compliance_by_indicator.items())
