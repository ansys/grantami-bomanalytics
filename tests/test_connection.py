import pytest
from ansys.granta.bom_analytics import Connection


# TODO Test Auth methods


@pytest.mark.parametrize(
    "property_name, table_name",
    [
        ("material_universe_table_name", "My Material Universe"),
        ("inhouse_materials_table_name", "My Materials"),
        ("specifications_table_name", "specs"),
        ("products_and_parts_table_name", "Parts 'n' Products"),
        ("substances_table_name", "Chemicals"),
        ("coatings_table_name", "Coverings"),
    ],
)
def test_custom_table_config(property_name, table_name):
    conn = Connection(
        url="http://localhost/mi_servicelayer", autologon=True, dbkey="DBKEY"
    )

    conn.__setattr__(property_name, table_name)

    print(conn.query_config)
    for k, v in conn.query_config.to_dict().items():
        if k != property_name:
            assert not v
        else:
            assert v == table_name


def test_yaml(connection):
    assert connection.get_yaml()
