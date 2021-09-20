import pytest
from ansys.granta.bom_analytics import BomComplianceQuery, BomImpactedSubstancesQuery


@pytest.mark.parametrize("query_type", [BomComplianceQuery, BomImpactedSubstancesQuery])
def test_add_bom(query_type):
    query = query_type().set_bom("TEST BOM")
    assert isinstance(query, query_type)
    assert len(query._items) == 1
    assert query._items[0]._bom == "TEST BOM"


@pytest.mark.parametrize("query_type", [BomComplianceQuery, BomImpactedSubstancesQuery])
def test_add_bom_wrong_type(query_type, connection):
    with pytest.raises(TypeError) as e:
        query_type().set_bom(12345)
    assert "Incorrect type for value" in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type().set_bom(bom=12345)
    assert "Incorrect type for value" in str(e.value)
