import pytest
from ansys.grantami.bomanalytics import queries

all_bom_queries = pytest.mark.parametrize(
    "query_type",
    [
        queries.BomComplianceQuery,
        queries.BomImpactedSubstancesQuery,
        queries.BomSustainabilityQuery,
        queries.BomSustainabilitySummaryQuery,
    ]
)


@all_bom_queries
def test_add_bom(query_type):
    query = query_type().with_bom("TEST BOM")
    assert isinstance(query, query_type)
    assert query._data.bom == "TEST BOM"


@all_bom_queries
def test_add_bom_wrong_type(query_type):
    with pytest.raises(TypeError) as e:
        query_type().with_bom(12345)
    assert "Incorrect type for value" in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type().with_bom(bom=12345)
    assert "Incorrect type for value" in str(e.value)
