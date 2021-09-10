from pytest import raises
from query_managers import ReferenceTypes, SubstanceQueryManager


def test_impacted_substances(connection):
    substance_query = connection.create_substance_query()
    substance_query.add_record(ReferenceTypes.cas_number, '50-00-0')
    with raises(AttributeError) as e:
        substance_query.add_legislation('The SIN List 2.1 (Substitute It Now!)')
    with raises(AttributeError) as e:
        assert len(substance_query.impacted_substances) == 1


def test_compliance(connection, indicators):
    substance_query: SubstanceQueryManager = connection.create_substance_query()
    substance_query.add_substance_with_amount(ReferenceTypes.cas_number, '50-00-0', 1.0)
    for indicator in indicators:
        substance_query.add_indicator(indicator)
    assert len(substance_query.compliance) == 1
    for res in substance_query.compliance:
        assert len(res.indicators) == len(indicators)
        for ind in indicators:
            ind_res = res.indicators[ind.name]
            assert ind_res.definition == ind
            assert ind_res.result
