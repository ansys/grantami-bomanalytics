import pytest
import requests_mock
import os
from ansys.grantami.bomanalytics import _connection, Connection


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
    query_config = mock_connection._query_arguments["config"].to_dict()
    query_config["in_house_materials_table_name"] = query_config.pop("inhouse_materials_table_name")
    for k, v in query_config.items():
        if k != property_name:
            assert not v
        else:
            assert v == table_name


def test_custom_dbkey(mock_connection):
    mock_connection.set_database_details(database_key="RS_DB")
    assert mock_connection._query_arguments["database_key"] == "RS_DB"


def test_default_dbkey(mock_connection):
    assert mock_connection._query_arguments["database_key"] == "MI_Restricted_Substances"


def test_repr_default_dbkey(mock_connection):
    assert repr(mock_connection) == '<BomServicesClient: url="http://localhost/mi_servicelayer", ' \
                                    'dbkey="MI_Restricted_Substances">'


def test_repr_custom_dbkey(mock_connection):
    mock_connection.set_database_details(database_key="RS_DB")
    assert repr(mock_connection) == '<BomServicesClient: url="http://localhost/mi_servicelayer", dbkey="RS_DB">'


def test_repr_default_dbkey_custom_table(mock_connection):
    mock_connection.set_database_details(specifications_table_name="My Specs")
    assert repr(mock_connection) == '<BomServicesClient: url="http://localhost/mi_servicelayer", ' \
                                    'dbkey="MI_Restricted_Substances", specifications_table_name="My Specs">'


def test_repr_custom_dbkey_custom_table(mock_connection):
    mock_connection.set_database_details(database_key="RS_DB", specifications_table_name="My Specs")
    assert repr(mock_connection) == '<BomServicesClient: url="http://localhost/mi_servicelayer", ' \
                                    'dbkey="RS_DB", specifications_table_name="My Specs">'


class TestConnectToSL:
    @pytest.mark.parametrize("sl_url", ["http://host/path/",
                                        "http://host/path",
                                        "https://host/path/",
                                        "https://host/path"])
    def test_mocked(self, sl_url):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, text="")
            connection = Connection(servicelayer_url=sl_url).with_anonymous().connect()
        sl_url_stripped = sl_url.strip("/")
        assert connection.api_url == sl_url_stripped + _connection.SERVICE_PATH

    @pytest.mark.integration
    @pytest.mark.parametrize("trailing_slash", [True, False])
    def test_real(self, trailing_slash):
        url = os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer") + ("/" if trailing_slash else "")
        _ = (
            Connection(servicelayer_url=url)
            .with_autologon()
            .connect()
        )
