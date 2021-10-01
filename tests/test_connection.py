from .common import (
    pytest,
    ALL_QUERY_TYPES,
)


@pytest.mark.parametrize(
    "property_name, table_name",
    [
        ("material_universe_table_name", "My Material Universe"),
        ("in_house_materials_table_name", "My Materials"),
        ("specifications_table_name", "specs"),
        ("products_and_parts_table_name", "Parts 'n' Products"),
        ("substances_table_name", "Chemicals"),
        ("coatings_table_name", "Coverings"),
    ],
)
@pytest.mark.parametrize("query_type", ALL_QUERY_TYPES)
def test_custom_table_config(property_name, table_name, query_type, mock_connection):
    mock_connection.set_database_details(**{property_name: table_name})
    query_config = mock_connection._query_config.to_dict()
    query_config["in_house_materials_table_name"] = query_config.pop("inhouse_materials_table_name")
    for k, v in query_config.items():
        if k != property_name:
            assert not v
        else:
            assert v == table_name
