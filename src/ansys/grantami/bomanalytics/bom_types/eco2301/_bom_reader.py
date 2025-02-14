# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

import inspect
from typing import TYPE_CHECKING, Dict, Type

from xmlschema import XMLSchema

from . import _bom_types as bom_types
from .. import gbt1205
from .._bom_reader import GenericBoMReader

if TYPE_CHECKING:
    from .._base_types import BaseType


class BoMReader(GenericBoMReader[bom_types.BillOfMaterials]):
    def __init__(self, schema: XMLSchema):
        """
        Reader to convert a JSON formatted BoM, created by xmlschema, into a populated 23/01 BillOfMaterials object.

        Parameters
        ----------
        schema: XMLSchema
            Parsed XMLSchema representing the 23/01 Eco BoM format
        """
        super().__init__()
        self._schema = schema
        self._class_members: Dict[str, Type[BaseType]] = {
            k: v for k, v in inspect.getmembers(bom_types, inspect.isclass)
        }
        self._class_members.update({k: v for k, v in inspect.getmembers(gbt1205, inspect.isclass)})
        self._bom_type = bom_types.BillOfMaterials
