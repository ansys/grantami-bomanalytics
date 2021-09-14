from query_managers import MaterialImpactedSubstanceQuery, MaterialComplianceQuery


def test_impacted_substances(connection):
    stk_object = [{'dbkey': 'MI_Restricted_Substances',
                   'record_guid': 'eef13c81-9b04-4af3-8d68-3524ffce7035'}]

    response = MaterialImpactedSubstanceQuery(connection).add_material_ids(['plastic-abs-pvc-flame']) \
        .add_stk_records(stk_object) \
        .add_legislations(['The SIN List 2.1 (Substitute It Now!)']) \
        .execute()

    assert len(response.impacted_substances) == 2
    for mat_results in response.impacted_substances:
        assert len(mat_results.legislations) == 1
        assert 'The SIN List 2.1 (Substitute It Now!)' in mat_results.legislations
        legislation = mat_results.legislations['The SIN List 2.1 (Substitute It Now!)']
        assert legislation.name == 'The SIN List 2.1 (Substitute It Now!)'
        assert legislation.substances

    assert len(response.all_impacted_substances) == 53
    assert len(response.impacted_substances_by_legislation) == 1
    for name, legislation in response.impacted_substances_by_legislation.items():
        assert len(legislation) == 53


def test_compliance(connection, indicators):
    stk_object = [{'dbkey': 'MI_Restricted_Substances',
                   'record_guid': 'eef13c81-9b04-4af3-8d68-3524ffce7035'}]

    response = MaterialComplianceQuery(connection).add_material_ids(['plastic-abs-pvc-flame']) \
        .add_stk_records(stk_object) \
        .add_indicators(indicators) \
        .execute()

    assert len(response.compliance) == 2
    for mat_results in response.compliance:
        assert len(mat_results.indicators) == len(indicators)
        for indicator in indicators:
            indicator_result = mat_results.indicators[indicator.name]
            assert indicator_result.name == indicator.name
            assert indicator_result.result
        assert mat_results.substances

    assert len(response.compliance_by_indicator) == 2
    for indicator in indicators:
        indicator_result = response.compliance_by_indicator[indicator.name]
        assert indicator_result.name == indicator.name
        assert indicator_result.result
