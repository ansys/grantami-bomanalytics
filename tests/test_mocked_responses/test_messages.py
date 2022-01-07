import json
import pytest
from ansys.grantami.bomanalytics import queries, GrantaMIException
from ansys.grantami.bomanalytics._query_results import LogMessage
from .common import BaseMockTester
from ..inputs import examples_as_dicts
from ansys.grantami.bomanalytics_openapi.models import GetImpactedSubstancesForMaterialsResponse


class TestMessages(BaseMockTester):
    query = queries.BomImpactedSubstancesQuery()

    def test_critical_error_raises_exception(self, mock_connection):
        response = {"LogMessages": [{"Severity": "critical", "Message": "shit's on fire, yo"}]}
        with pytest.raises(GrantaMIException) as e:
            self.get_mocked_response(mock_connection, response=json.dumps(response))
        assert str(e.value) == response["LogMessages"][0]["Message"]

    def test_non_critical_error(self, mock_connection):
        self.query = (
            queries.MaterialImpactedSubstancesQuery()
            .with_legislations(["Fake legislation"])
            .with_material_ids(["Fake ID"])
        )
        mock_key = GetImpactedSubstancesForMaterialsResponse.__name__
        mock_response = examples_as_dicts[mock_key]

        severity_list = ["error", "warning", "info"]
        messages = [
            {"Severity": severity, "Message": f"This is a non-critical {severity} message"}
            for severity in severity_list
        ]
        mock_response["LogMessages"] = messages

        query_result = self.get_mocked_response(mock_connection, response=json.dumps(mock_response))

        assert len(messages) == len(query_result.messages)
        for severity in severity_list:
            assert (
                LogMessage(severity=severity, message=f"This is a non-critical {severity} message")
                in query_result.messages
            )
