from ansys.granta.bom_analytics import queries


def test_compliance(connection, indicator_definitions):
    response = (
        queries.SubstanceCompliance()
        .add_cas_numbers(["50-00-0", "57-24-9"])
        .add_cas_numbers_with_amounts([("1333-86-4", 25), ("75-74-1", 50)])
        .add_indicators(indicator_definitions)
        .execute(connection)
    )

    assert len(response.compliance_by_substance_and_indicator) == 4
    for sub_results in response.compliance_by_substance_and_indicator:
        assert len(sub_results.indicators) == len(indicator_definitions)
        for ind in indicator_definitions:
            indicator_result = sub_results.indicators[ind.name]
            assert indicator_result.name == ind.name
            assert indicator_result.flag

    assert len(response.compliance_by_indicator) == 2
    for indicator in indicator_definitions:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.flag
