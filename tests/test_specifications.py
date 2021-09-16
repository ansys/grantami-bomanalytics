from query_managers import (
    SpecificationComplianceQuery,
    SpecificationImpactedSubstanceQuery,
)


def test_impacted_substances(connection):
    response = (
        SpecificationImpactedSubstanceQuery(connection)
        .add_record_history_guids(["516b2b9b-c4cf-419f-8caa-238ba1e7b7e5"])
        .add_specification_ids(["MIL-C-20218,TypeII"])
        .add_legislations(["The SIN List 2.1 (Substitute It Now!)"])
        .execute()
    )

    assert len(response.impacted_substances_by_specification_and_legislation) == 2
    for spec_results in response.impacted_substances_by_specification_and_legislation:
        assert len(spec_results.legislations) == 1
        assert "The SIN List 2.1 (Substitute It Now!)" in spec_results.legislations
        leg = spec_results.legislations["The SIN List 2.1 (Substitute It Now!)"]
        assert leg.name == "The SIN List 2.1 (Substitute It Now!)"
        assert leg.substances

    assert len(response.impacted_substances_by_legislation) == 1
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) == 4

    assert len(response.impacted_substances) == 4


def test_compliance(connection, indicators):
    response = (
        SpecificationComplianceQuery(connection)
        .add_record_history_guids(["516b2b9b-c4cf-419f-8caa-238ba1e7b7e5"])
        .add_specification_ids(["MIL-C-20218,TypeII"])
        .add_indicators(indicators)
        .execute()
    )

    assert len(response.compliance_by_specification_and_indicator) == 2
    for spec_results in response.compliance_by_specification_and_indicator:
        assert len(spec_results.indicators) == len(indicators)
        for ind in indicators:
            ind_res = spec_results.indicators[ind.name]
            assert ind_res.name == ind.name
            assert ind_res.result

    assert len(response.compliance_by_indicator) == 2
    for indicator in indicators:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.result
