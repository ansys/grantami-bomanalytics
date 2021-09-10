from builders import ReferenceTypes


def test_impacted_substances(connection):
    spec_query = connection.create_specification_query()
    spec_query.add_record(ReferenceTypes.record_history_guid, '516b2b9b-c4cf-419f-8caa-238ba1e7b7e5')
    spec_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
    assert len(spec_query.impacted_substances) == 1
    for res in spec_query.impacted_substances:
        assert len(res.legislations) == 1
        assert 'The SIN List 2.1 (Substitute It Now!)' in res.legislations
        leg = res.legislations['The SIN List 2.1 (Substitute It Now!)']
        assert leg.name == 'The SIN List 2.1 (Substitute It Now!)'
        assert leg.substances


def test_compliance(connection, indicators):
    spec_query = connection.create_specification_query()
    spec_query.add_record(ReferenceTypes.record_history_guid, '516b2b9b-c4cf-419f-8caa-238ba1e7b7e5')
    for indicator in indicators:
        spec_query.add_indicator(indicator)
    assert len(spec_query.compliance) == 1
    for res in spec_query.compliance:
        assert len(res.indicators) == len(indicators)
        for ind in indicators:
            ind_res = res.indicators[ind.name]
            assert ind_res.definition == ind
            assert ind_res.result
