import pytest
from ansys.grantami.bomanalytics import queries
from .common import check_query_manager_attributes


@pytest.mark.parametrize("query_type", [queries.MaterialImpactedSubstancesQuery, queries.MaterialComplianceQuery])
@pytest.mark.parametrize("material_ids", [[], ["One Material ID"], ["Two", "Material IDs"]])
def test_add_material_ids(query_type, material_ids):
    query = query_type().with_material_ids(material_ids)
    assert isinstance(query, query_type)
    assert check_query_manager_attributes(
        query,
        ["record_guid", "record_history_guid", "record_history_identity"],
        "material_id",
        material_ids,
    )


@pytest.mark.parametrize("query_type", [queries.MaterialImpactedSubstancesQuery, queries.MaterialComplianceQuery])
def test_add_material_ids_wrong_type(query_type):
    with pytest.raises(TypeError) as e:
        query_type().with_material_ids("Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type().with_material_ids(material_ids="Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
