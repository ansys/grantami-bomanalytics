from ..common import (
    pytest,
    queries,
)


@pytest.mark.parametrize("query_type", [queries.BomComplianceQuery, queries.BomImpactedSubstancesQuery])
def test_add_bom(query_type):
    query = query_type().with_bom("TEST BOM")
    assert isinstance(query, query_type)
    assert query._item_argument_manager.bom == "TEST BOM"


@pytest.mark.parametrize("query_type", [queries.BomComplianceQuery, queries.BomImpactedSubstancesQuery])
def test_add_bom_wrong_type(query_type):
    with pytest.raises(TypeError):
        query_type().with_bom(12345)
        query_type().with_bom(bom=12345)
