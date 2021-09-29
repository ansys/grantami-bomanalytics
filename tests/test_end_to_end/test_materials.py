from ansys.granta.bom_analytics import queries


def test_impacted_substances(connection, legislations):
    response = (
        queries.MaterialImpactedSubstances()
        .add_material_ids(["plastic-abs-pvc-flame", "plastic-pmma-pc"])
        .add_legislations(legislations)
        .execute(connection)
    )

    assert len(response.impacted_substances_by_material_and_legislation) == 2
    for mat_results in response.impacted_substances_by_material_and_legislation:
        assert len(mat_results.legislations) == len(legislations)
        for legislation in legislations:
            assert legislation in mat_results.legislations
            this_legislation = mat_results.legislations[legislation]
            assert this_legislation.name == legislation
            assert this_legislation.substances

    assert len(response.impacted_substances_by_legislation) == len(legislations)
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) == 64 or len(legislation) == 5

    assert len(response.impacted_substances) == 69


def test_compliance(connection, indicator_definitions):
    response = (
        queries.MaterialCompliance()
        .add_material_ids(["plastic-abs-pvc-flame", "plastic-pmma-pc"])
        .add_indicators(indicator_definitions)
        .execute(connection)
    )

    assert len(response.compliance_by_material_and_indicator) == 2
    for mat_results in response.compliance_by_material_and_indicator:
        assert len(mat_results.indicators) == len(indicator_definitions)
        for indicator in indicator_definitions:
            indicator_result = mat_results.indicators[indicator.name]
            assert indicator_result.name == indicator.name
            assert indicator_result.flag
        assert len(mat_results.substances) in [51, 17]

    assert len(response.compliance_by_indicator) == 2
    for indicator in indicator_definitions:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.flag
