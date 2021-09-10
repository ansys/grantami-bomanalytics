from query_managers import ReferenceTypes


def test_impacted_substances(connection):
    material_query = connection.create_material_query()
    material_query.add_record(ReferenceTypes.material_id, 'plastic-abs-pvc-flame')
    stk_object = [{'dbkey': 'MI_Restricted_Substances',
                   'record_guid': 'eef13c81-9b04-4af3-8d68-3524ffce7035'}]
    material_query.add_stk_records(stk_object)
    material_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
    assert len(material_query.impacted_substances) == 2
    for res in material_query.impacted_substances:
        assert len(res.legislations) == 1
        assert 'The SIN List 2.1 (Substitute It Now!)' in res.legislations
        leg = res.legislations['The SIN List 2.1 (Substitute It Now!)']
        assert leg.name == 'The SIN List 2.1 (Substitute It Now!)'
        assert leg.substances


def test_compliance(connection, indicators):
    material_query = connection.create_material_query()
    material_query.add_record(ReferenceTypes.material_id, 'plastic-abs-pvc-flame')
    stk_object = [{'dbkey': 'MI_Restricted_Substances',
                   'record_guid': 'eef13c81-9b04-4af3-8d68-3524ffce7035'}]
    material_query.add_stk_records(stk_object)

    for indicator in indicators:
        material_query.add_indicator(indicator)
    assert len(material_query.compliance) == 2
    for mat_res in material_query.compliance:
        assert len(mat_res.indicators) == len(indicators)
        for ind in indicators:
            ind_res = mat_res.indicators[ind.name]
            assert ind_res.definition == ind
            assert ind_res.result
        assert mat_res.substances
