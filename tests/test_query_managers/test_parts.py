import pytest
from ansys.granta.bom_analytics import PartImpactedSubstanceQuery, PartComplianceQuery

from tests.test_query_managers.common import check_query_manager_attributes

# TODO: For all tests, test all different pivots on the results with known values


@pytest.mark.parametrize(
    "query_type", [PartComplianceQuery, PartImpactedSubstanceQuery]
)
@pytest.mark.parametrize(
    "part_numbers", [[], ["One part number"], ["Two", "Part numbers"]]
)
def test_add_part_numbers(query_type, part_numbers, connection):
    query = query_type(connection).add_part_numbers(part_numbers)
    assert isinstance(query, query_type)
    assert check_query_manager_attributes(
        query,
        ["record_guid", "record_history_guid", "record_history_identity"],
        "part_number",
        part_numbers,
    )


@pytest.mark.parametrize(
    "query_type", [PartComplianceQuery, PartImpactedSubstanceQuery]
)
def test_add_part_numbers_wrong_type(query_type, connection):
    with pytest.raises(TypeError) as e:
        query_type(connection).add_part_numbers("Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
    with pytest.raises(TypeError) as e:
        query_type(connection).add_part_numbers(part_numbers="Strings are not allowed")
    assert 'Incorrect type for value "Strings are not allowed"' in str(e.value)
