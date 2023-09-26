from ansys.grantami.bomanalytics_openapi.models import GetAvailableLicensesResponse
import requests_mock

from ..inputs import examples_as_strings


def test_response(mock_connection):
    with requests_mock.Mocker() as mocker:
        mocker.get(requests_mock.ANY, text=examples_as_strings[GetAvailableLicensesResponse.__name__])
        response = mock_connection._get_licensing_information()
    assert response.sustainability is False
    assert response.restricted_substances is True
