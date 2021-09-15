from query_managers import PartComplianceQuery, PartImpactedSubstanceQuery


def test_impacted_substances(connection):
    legislations = ['The SIN List 2.1 (Substitute It Now!)', 'EU Directive 2011/65/EU (RoHS 2)']
    response = PartImpactedSubstanceQuery(connection) \
                   .add_part_numbers(['DRILL', 'main_frame']) \
                   .add_legislations(legislations) \
                   .execute()

    assert len(response.impacted_substances) == 2
    for part_results in response.impacted_substances:
        assert len(part_results.legislations) in [1, 2]
        for name, legislation in part_results.legislations.items():
            assert len(legislation.substances) in [1, 19, 79]

    assert len(response.all_impacted_substances) == 99
    assert len(response.impacted_substances_by_legislation) == 2
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) in [80, 19]


def test_compliance(connection, indicators):
    response = PartComplianceQuery(connection) \
        .add_part_numbers(['DRILL', 'main_frame']) \
        .add_indicators(indicators) \
        .execute()

    assert len(response.compliance) == 2
    for part_results in response.compliance:
        assert len(part_results.indicators) == len(indicators)
        for indicator in indicators:
            indicator_result = part_results.indicators[indicator.name]
            assert indicator_result.name == indicator.name
            assert indicator_result.result
        assert not part_results.substances  # Empty list, no substances

    assert len(response.compliance_by_indicator) == 2
    for indicator in indicators:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.result
