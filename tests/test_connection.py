import pytest


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
def test_custom_table_config(property_name, table_name, connection):
    connection.__setattr__(property_name, table_name)

    query_config = connection.query_config.to_dict()
    query_config["in_house_materials_table_name"] = query_config.pop(
        "inhouse_materials_table_name"
    )
    for k, v in query_config.items():
        if k != property_name:
            assert not v
        else:
            assert v == table_name

    connection.__setattr__(property_name, None)


def test_yaml(connection):
    assert connection.get_yaml()
