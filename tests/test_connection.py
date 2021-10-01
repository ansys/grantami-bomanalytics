from .common import (
    pytest,
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
def test_custom_table_config(property_name, table_name, mock_connection):
    mock_connection.set_database_details(**{property_name: table_name})
    query_config = mock_connection._query_arguments['config'].to_dict()
    query_config["in_house_materials_table_name"] = query_config.pop("inhouse_materials_table_name")
    for k, v in query_config.items():
        if k != property_name:
            assert not v
        else:
            assert v == table_name


def test_custom_dbkey(mock_connection):
    mock_connection.set_database_details(database_key="RS_DB")
    assert mock_connection._query_arguments['database_key'] == "RS_DB"


def test_default_dbkey(mock_connection):
    assert mock_connection._query_arguments['database_key'] == "MI_Restricted_Substances"
