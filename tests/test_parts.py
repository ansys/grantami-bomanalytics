from query_managers import PartComplianceQuery, PartImpactedSubstanceQuery


def test_impacted_substances(connection):
    response = PartImpactedSubstanceQuery(connection) \
                   .add_part_numbers(['DRILL', 'main_frame']) \
                   .add_legislations(['The SIN List 2.1 (Substitute It Now!)']) \
                   .execute()

    assert len(response.impacted_substances) == 2
    for part_results in response.impacted_substances:
        assert len(part_results.legislations) == 1
        assert 'The SIN List 2.1 (Substitute It Now!)' in part_results.legislations
        legislation = part_results.legislations['The SIN List 2.1 (Substitute It Now!)']
        assert legislation.name == 'The SIN List 2.1 (Substitute It Now!)'
        assert legislation.substances

    assert len(response.all_impacted_substances) == 80
    assert len(response.impacted_substances_by_legislation) == 1
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) == 80


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
