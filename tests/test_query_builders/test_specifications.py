from ..common import (
    pytest,
    queries,
    check_query_manager_attributes,
)


@pytest.mark.parametrize("query_type", [queries.SpecificationComplianceQuery, queries.SpecificationImpactedSubstancesQuery])
@pytest.mark.parametrize("spec_ids", [[], ["One spec id"], ["Two", "Spec IDs"]])
def test_add_spec_ids(query_type, spec_ids):
    query = query_type().with_specification_ids(spec_ids)
    assert isinstance(query, query_type)
    assert check_query_manager_attributes(
        query,
        ["record_guid", "record_history_guid", "record_history_identity"],
        "specification_id",
        spec_ids,
    )


@pytest.mark.parametrize("query_type", [queries.SpecificationComplianceQuery, queries.SpecificationImpactedSubstancesQuery])
def test_add_spec_ids_wrong_type(query_type):
    with pytest.raises(TypeError) as e:
        query_type().with_specification_ids("Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type().with_specification_ids(specification_ids="Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
