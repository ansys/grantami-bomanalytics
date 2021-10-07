from .common import (
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse,
    queries,
    indicators,
    check_substance,
    check_indicator,
    get_mocked_response,
    check_specification_attributes,
    check_material_attributes,
    check_coating_attributes,
    check_substance_attributes,
)


class TestImpactedSubstances:
    query = (
        queries.SpecificationImpactedSubstances()
        .with_legislations(["Fake legislation"])
        .with_specification_ids(["Fake ID"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsResponse.__name__

    def test_impacted_substances_by_specification_and_legislation(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
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
        queries.SpecificationCompliance()
        .with_indicators(
            [
                indicators.WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                indicators.RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .with_specification_ids(["Fake ID"])
    )
    mock_key = GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsResponse.__name__

    def test_compliance_by_specification_and_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_specification_and_indicator) == 2

        spec_0 = response.compliance_by_specification_and_indicator[0]
        assert spec_0.specification_id == "MSP89,TypeI"
        assert not spec_0.record_guid
        assert not spec_0.record_history_guid
        assert not spec_0.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in spec_0.indicators.items())

        spec_1 = response.compliance_by_specification_and_indicator[1]
        assert not spec_1.specification_id
        assert spec_1.record_guid == "3df206df-9fc8-4859-90d4-3519764f8b55"
        assert not spec_1.record_history_guid
        assert not spec_1.record_history_identity
        assert all(check_indicator(name, ind) for name, ind in spec_1.indicators.items())

    def test_compliance_by_specification_and_indicator_coatings(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        coating_0_0 = response.compliance_by_specification_and_indicator[0].coatings[0]
        assert coating_0_0.record_history_identity == "987654"
        assert all(check_indicator(name, ind) for name, ind in coating_0_0.indicators.items())

    def test_compliance_by_specification_and_indicator_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)

        substance_0_0 = response.compliance_by_specification_and_indicator[0].coatings[0].substances[0]
        assert substance_0_0.record_history_identity == "62345"
        assert all(check_indicator(name, ind) for name, ind in substance_0_0.indicators.items())

        substance_1_0 = response.compliance_by_specification_and_indicator[1].substances[0]
        assert substance_1_0.record_history_identity == "12345"
        assert all(check_indicator(name, ind) for name, ind in substance_1_0.indicators.items())

        substance_1_1 = response.compliance_by_specification_and_indicator[1].substances[1]
        assert substance_1_1.record_history_identity == "34567"
        assert all(check_indicator(name, ind) for name, ind in substance_1_1.indicators.items())

    def test_compliance_by_indicator(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind) for name, ind in response.compliance_by_indicator.items())

    def test_compliance_result_objects_specifications(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        specs = (
            response.compliance_by_specification_and_indicator
            + response.compliance_by_specification_and_indicator[0].specifications
        )
        assert all([check_specification_attributes(spec) for spec in specs])

    def test_compliance_result_objects_materials(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        mats = response.compliance_by_specification_and_indicator[1].materials
        assert all([check_material_attributes(mat) for mat in mats])

    def test_compliance_result_objects_coatings(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        coatings = response.compliance_by_specification_and_indicator[0].coatings
        assert all([check_coating_attributes(coating) for coating in coatings])

    def test_compliance_result_objects_substances(self, connection):
        response = get_mocked_response(self.query, self.mock_key, connection)
        subs = (
            response.compliance_by_specification_and_indicator[0].coatings[0].substances
            + response.compliance_by_specification_and_indicator[0].specifications[0].substances
            + response.compliance_by_specification_and_indicator[1].materials[0].substances
            + response.compliance_by_specification_and_indicator[1].materials[1].substances
            + response.compliance_by_specification_and_indicator[1].substances
        )
        assert all([check_substance_attributes(sub) for sub in subs])
