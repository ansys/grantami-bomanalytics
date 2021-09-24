from .common import (
    pytest,
    GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response,
    GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response,
    BomComplianceQuery,
    BomImpactedSubstanceQuery,
    WatchListIndicator,
    RoHSIndicator,
    check_substance,
    check_indicator,
)


@pytest.mark.parametrize(
    "connection_mock",
    [
        [
            "impacted_substances_api",
            "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_bom1711",
            GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response,
        ]
    ],
    indirect=True,
)
class TestImpactedSubstances:
    query = BomImpactedSubstanceQuery().add_legislations(["Fake legislation"]).set_bom("<Bom />")

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
            "post_miservicelayer_bom_analytics_v1svc_compliance_bom1711",
            GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response,
        ]
    ],
    indirect=True,
)
class TestCompliance:
    query = (
        BomComplianceQuery()
        .add_indicators(
            [
                WatchListIndicator(name="Indicator 1", legislation_names=["Mock"]),
                RoHSIndicator(name="Indicator 2", legislation_names=["Mock"]),
            ]
        )
        .set_bom("<Bom />")
    )

    def test_compliance_by_part_and_indicator(self, connection_mock):
        response = self.query.execute(connection_mock)
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

    def test_compliance_by_indicator(self, connection_mock):
        response = self.query.execute(connection_mock)
        assert len(response.compliance_by_indicator) == 2
        assert all(check_indicator(name, ind, False) for name, ind in response.compliance_by_indicator.items())
