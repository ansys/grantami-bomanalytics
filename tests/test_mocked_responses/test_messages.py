# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import logging

import pytest

from ansys.grantami.bomanalytics import GrantaMIException, queries
from ansys.grantami.bomanalytics._query_results import LogMessage

from ..inputs import example_boms, example_payloads
from .common import BaseMockTester


class TestMessages(BaseMockTester):
    bom = example_boms["bom-1711"].content
    query = queries.BomImpactedSubstancesQuery().with_bom(bom)

    def test_critical_error_raises_exception(self, mock_connection, caplog):
        error_message = "This is a critical message"
        response = {"LogMessages": [{"Severity": "critical-error", "Message": error_message}]}
        with pytest.raises(GrantaMIException) as e, pytest.warns(RuntimeWarning, match="No legislations"):
            self.get_mocked_response(mock_connection, response=json.dumps(response))
        assert str(e.value) == error_message
        assert self.check_log(caplog, "CRITICAL", error_message)

    @pytest.mark.parametrize("severity", ["error", "warning"])
    def test_non_critical_error_printed_to_stdout(self, mock_connection, severity, caplog):
        self.query = (
            queries.MaterialImpactedSubstancesQuery()
            .with_legislation_ids(["Fake legislation"])
            .with_material_ids(["Fake ID"])
        )
        mock_key = "GetImpactedSubstancesForMaterials.Response"
        mock_response = example_payloads[mock_key].data

        error_message = f"This is a non-critical {severity} message"
        messages = [{"Severity": severity, "Message": error_message}]
        mock_response["LogMessages"] = messages

        query_result = self.get_mocked_response(mock_connection, response=json.dumps(mock_response))

        assert len(messages) == len(query_result.messages)
        assert LogMessage(severity=severity, message=error_message) in query_result.messages
        assert self.check_log(caplog, severity.upper(), error_message)

    def test_info(self, mock_connection, caplog):
        self.query = (
            queries.MaterialImpactedSubstancesQuery()
            .with_legislation_ids(["Fake legislation"])
            .with_material_ids(["Fake ID"])
        )
        mock_key = "GetImpactedSubstancesForMaterials.Response"
        mock_response = example_payloads[mock_key].data

        error_message = "This is a non-critical info message"
        messages = [{"Severity": "information", "Message": error_message}]
        mock_response["LogMessages"] = messages

        with caplog.at_level(logging.INFO):
            query_result = self.get_mocked_response(mock_connection, response=json.dumps(mock_response))

        assert len(messages) == len(query_result.messages)
        assert LogMessage(severity="information", message=error_message) in query_result.messages
        assert self.check_log(caplog, "INFO", error_message)

    @staticmethod
    def check_log(caplog: pytest.LogCaptureFixture, level: str, message: str) -> bool:
        for rec in caplog.records:
            if rec.levelname == level and rec.message == message:
                return True
        return False
