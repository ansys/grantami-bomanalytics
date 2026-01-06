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

from ansys.openapi.common import Unset
import pytest

from ansys.grantami.bomanalytics._typing import _convert_unset_to_none, _raise_if_empty


class TestRaiseIfEmpty:
    def test_does_not_raise_if_not_empty(self):
        _raise_if_empty("value")

    @pytest.mark.parametrize(
        "value, message", [(Unset, "Provided value cannot be 'Unset'"), (None, "Provided value cannot be 'None'")]
    )
    def test_raises_if_empty(self, value, message):
        with pytest.raises(ValueError, match=message):
            _raise_if_empty(value)


class TestConvertUnsetToNone:
    @pytest.mark.parametrize("value", [None, "value"])
    def test_value_is_unchanged(self, value):
        converted = _convert_unset_to_none(value)
        assert converted == value

    def test_unset_is_converted_to_none(self):
        converted = _convert_unset_to_none(Unset)
        assert converted is None
