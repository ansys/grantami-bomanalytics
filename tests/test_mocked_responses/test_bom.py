from .common import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response,
    queries,
    indicators,
    check_substance,
    check_indicator,
    get_mocked_response,
    check_part_attributes,
    check_material_attributes,
    check_substance_attributes,
)


class TestImpactedSubstances:
    query = queries.BomImpactedSubstances().with_legislations(["Fake legislation"]).with_bom("<Bom />")
    mock_key = GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response.__name__

    def test_impacted_substances_by_legislation(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances_by_legislation) == 1
        legislation = response.impacted_substances_by_legislation["The SIN List 2.1 (Substitute It Now!)"]
        assert all([check_substance(s) for s in legislation])

    def test_impacted_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.impacted_substances) == 2
        assert all([check_substance(s) for s in response.impacted_substances])


class TestCompliance:
    query = (
        queries.BomCompliance()
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
        assert not part_0.part_number
        assert not part_0.record_guid
        assert not part_0.record_history_guid
        assert not part_0.record_history_identity
        assert not part_0.materials
        assert not part_0.specifications
        assert not part_0.substances
        assert all(check_indicator(name, ind, False) for name, ind in part_0.indicators.items())

        # Level 1: Child part
        part_0_0 = part_0.parts[0]
        assert not part_0_0.part_number
        assert not part_0_0.record_guid
        assert not part_0_0.record_history_guid
        assert not part_0_0.record_history_identity
        assert not part_0_0.materials
        assert not part_0_0.specifications
        assert not part_0_0.parts
        assert all(check_indicator(name, ind, False) for name, ind in part_0_0.indicators.items())

        # Level 2: Child substance
        substance_0_0_0 = part_0_0.substances[0]
        assert substance_0_0_0.record_history_identity == "62345"
        assert not substance_0_0_0.cas_number
        assert not substance_0_0_0.ec_number
        assert not substance_0_0_0.chemical_name
        assert not substance_0_0_0.record_history_guid
        assert not substance_0_0_0.record_guid
        assert all(check_indicator(name, ind, False) for name, ind in substance_0_0_0.indicators.items())

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind, False) for name, ind in response.compliance_by_indicator.items())

    def test_compliance_result_objects_parts(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        parts = response.compliance_by_part_and_indicator + \
            response.compliance_by_part_and_indicator[0].parts
        assert all(
            [check_part_attributes(part) for part in parts]
        )

    def test_compliance_result_objects_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        subs = response.compliance_by_part_and_indicator[0].parts[0].substances
        assert all(
            [check_substance_attributes(sub) for sub in subs]
        )
