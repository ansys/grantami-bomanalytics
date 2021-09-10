from query_managers import ReferenceTypes


def test_impacted_substances(connection):
    part_query = connection.create_part_query()
    part_query.add_record(ReferenceTypes.part_number, 'DRILL')
    part_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
    assert len(part_query.impacted_substances) == 1
    assert not part_query.compliance
    for res in part_query.impacted_substances:
        assert len(res.legislations) == 1
        assert 'The SIN List 2.1 (Substitute It Now!)' in res.legislations
        leg = res.legislations['The SIN List 2.1 (Substitute It Now!)']
        assert leg.name == 'The SIN List 2.1 (Substitute It Now!)'
        assert leg.substances


def test_compliance(connection, indicators):
    part_query = connection.create_part_query()
    part_query.add_record(ReferenceTypes.part_number, 'DRILL')
    for indicator in indicators:
        part_query.add_indicator(indicator)
    part_query.get_impacted_substances()
    assert len(part_query.compliance) == 1
    assert not part_query.impacted_substances
    for res in part_query.compliance:
        assert len(res.indicators) == len(indicators)
        for ind in indicators:
            ind_res = res.indicators[ind.name]
            assert ind_res.definition == ind
            assert ind_res.result
