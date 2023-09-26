import os
import re

import pytest
import requests_mock

from ansys.grantami.bomanalytics import Connection, LicensingException, _connection

from .common import CUSTOM_TABLES, LICENSE_RESPONSE

SL_URL = os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")


@pytest.mark.parametrize("property_name, table_name", CUSTOM_TABLES)
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
    assert (
        repr(mock_connection)
        == f'<BomServicesClient: url="{SL_URL}", maximum_spec_link_depth="unlimited", dbkey="MI_Restricted_Substances">'
    )


def test_repr_custom_dbkey(mock_connection):
    mock_connection.set_database_details(database_key="RS_DB")
    assert (
        repr(mock_connection)
        == f'<BomServicesClient: url="{SL_URL}", maximum_spec_link_depth="unlimited", dbkey="RS_DB">'
    )


def test_repr_default_dbkey_custom_table(mock_connection):
    mock_connection.set_database_details(specifications_table_name="My Specs")
    assert (
        repr(mock_connection) == f'<BomServicesClient: url="{SL_URL}", maximum_spec_link_depth="unlimited", '
        'dbkey="MI_Restricted_Substances", specifications_table_name="My Specs">'
    )


def test_repr_custom_dbkey_custom_table(mock_connection):
    mock_connection.set_database_details(database_key="RS_DB", specifications_table_name="My Specs")
    assert (
        repr(mock_connection) == f'<BomServicesClient: url="{SL_URL}", maximum_spec_link_depth="unlimited", '
        'dbkey="RS_DB", specifications_table_name="My Specs">'
    )


@pytest.mark.parametrize("value", [None, 0, 1, 3000])
def test_set_max_spec_link_depth_with_valid_inputs(mock_connection, value):
    mock_connection.maximum_spec_link_depth = value
    assert mock_connection.maximum_spec_link_depth == value


def test_set_max_spec_link_depth_with_invalid_input(mock_connection):
    with pytest.raises(ValueError, match="maximum_spec_link_depth must be a non-negative integer or None"):
        mock_connection.maximum_spec_link_depth = -1


class TestConnectToSL:
    @pytest.mark.parametrize(
        "sl_url", ["http://host/path/", "http://host/path", "https://host/path/", "https://host/path"]
    )
    def test_mocked(self, sl_url):
        with requests_mock.Mocker() as m:
            m.get(requests_mock.ANY, json=LICENSE_RESPONSE)
            connection = Connection(api_url=sl_url).with_anonymous().connect()
        sl_url_stripped = sl_url.strip("/")
        assert connection.api_url == sl_url_stripped + _connection.SERVICE_PATH

    def test_missing_bomanalytics_service_raises_informative_error(self):
        sl_url = "http://host/path"
        with requests_mock.Mocker() as m:
            m.get(sl_url)
            m.get(sl_url + _connection.MI_AUTH_PATH)
            service_matcher = re.compile(f"{sl_url}{_connection.SERVICE_PATH}.*")
            m.get(service_matcher, status_code=404)
            with pytest.raises(
                ConnectionError, match="Cannot find the BoM Analytics service in Granta MI Service Layer"
            ):
                Connection(api_url=sl_url).with_anonymous().connect()

    def test_unhandled_bomanalytics_service_response_raises_informative_error(self):
        sl_url = "http://host/path"
        with requests_mock.Mocker() as m:
            m.get(sl_url)
            m.get(sl_url + _connection.MI_AUTH_PATH)
            service_matcher = re.compile(f"{sl_url}{_connection.SERVICE_PATH}.*")
            m.get(service_matcher, status_code=500)
            with pytest.raises(
                ConnectionError, match="An unexpected error occurred when trying to connect to BoM Analytics service"
            ):
                Connection(api_url=sl_url).with_anonymous().connect()

    def test_no_licenses_raises_informative_error(self):
        sl_url = "http://host/path"
        with requests_mock.Mocker() as m:
            no_license_response = {"LogMessages": [], "RestrictedSubstances": False, "Sustainability": False}
            m.get(requests_mock.ANY, json=no_license_response)
            with pytest.raises(LicensingException, match="no valid licenses "):
                connection = Connection(api_url=sl_url).with_anonymous().connect()

    @pytest.mark.integration
    @pytest.mark.parametrize("trailing_slash", [True, False])
    def test_real(self, trailing_slash):
        url = SL_URL + ("/" if trailing_slash else "")
        _ = Connection(api_url=url).with_credentials(os.getenv("TEST_USER"), os.getenv("TEST_PASS")).connect()
