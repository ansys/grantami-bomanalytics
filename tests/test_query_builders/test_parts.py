import pytest

from ansys.grantami.bomanalytics import queries

from .common import check_query_manager_attributes


@pytest.mark.parametrize("query_type", [queries.PartComplianceQuery, queries.PartImpactedSubstancesQuery])
@pytest.mark.parametrize("part_numbers", [[], ["One part number"], ["Two", "Part numbers"]])
def test_add_part_numbers(query_type, part_numbers):
    query = query_type().with_part_numbers(part_numbers)
    assert isinstance(query, query_type)
    assert check_query_manager_attributes(
        query,
        ["record_guid", "record_history_guid", "record_history_identity"],
        "part_number",
        part_numbers,
    )


@pytest.mark.parametrize("query_type", [queries.PartComplianceQuery, queries.PartImpactedSubstancesQuery])
def test_add_part_numbers_wrong_type(query_type):
    with pytest.raises(TypeError) as e:
        query_type().with_part_numbers("Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type().with_part_numbers(part_numbers="Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
