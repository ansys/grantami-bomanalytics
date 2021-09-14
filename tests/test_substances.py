from query_managers import SubstanceComplianceQuery


def test_compliance(connection, indicators):
    response = SubstanceComplianceQuery(connection)\
        .add_cas_numbers(['50-00-0', '57-24-9'])\
        .add_indicators(indicators)\
        .execute()

    assert len(response.compliance) == 2
    for sub_results in response.compliance:
        assert len(sub_results.indicators) == len(indicators)
        for ind in indicators:
            indicator_result = sub_results.indicators[ind.name]
            assert indicator_result.name == ind.name
            assert indicator_result.result

    assert len(response.compliance_by_indicator) == 2
    for indicator in indicators:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.result
