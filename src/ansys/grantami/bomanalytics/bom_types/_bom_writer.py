# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

from typing import Dict, cast

from xmlschema import XMLSchema

from . import BaseType, BillOfMaterials, HasNamespace


class BoMWriter:
    _schema: XMLSchema

    def __init__(self, schema: XMLSchema):
        """
        Writer to convert BillOfMaterials objects into the format ready for XML serialization.

        Parameters
        ----------
        schema: XMLSchema
            Parsed XMLSchema representing the 2301 Eco BoM format
        """
        self._schema = schema

    def _get_qualified_name(self, obj: HasNamespace, field_name: str) -> str:
        namespace_prefixes = [k for k, v in self._schema.namespaces.items() if v == obj._namespace]
        if len(namespace_prefixes) == 1:
            namespace_prefix = namespace_prefixes[0]
        elif len(namespace_prefixes) == 0:
            raise KeyError(f"Namespace {obj._namespace} does not exist in schema for object {type(obj)}")
        elif "" in namespace_prefixes:
            return field_name
        else:
            namespace_prefix = namespace_prefixes[0]
        if field_name[0] == "@":
            return f"@{namespace_prefix}:{field_name[1:]}"
        return f"{namespace_prefix}:{field_name}"

    def _convert_to_dict(self, obj: BaseType) -> Dict:
        value = {}

        for prop, field_name in obj._simple_values:
            prop_value = getattr(obj, prop)
            if prop_value is not None:
                value[self._get_qualified_name(obj, field_name)] = prop_value
        for _, prop, field_name in obj._props:
            prop_value = getattr(obj, prop)
            if prop_value is not None:
                prop_value = self._convert_to_dict(cast("BaseType", prop_value))
                value[self._get_qualified_name(obj, field_name)] = prop_value
        for _, prop, container_name, _, field_name in obj._list_props:
            prop_value = getattr(obj, prop)
            if prop_value is not None and len(prop_value) > 0:
                prop_value = {
                    self._get_qualified_name(obj, field_name): [
                        self._convert_to_dict(item_obj) for item_obj in prop_value
                    ]
                }
                value[self._get_qualified_name(obj, container_name)] = prop_value
        obj._write_custom_fields(value, self)
        return value

    def convert_bom_to_dict(self, obj: BillOfMaterials) -> Dict:
        """
        Convert a BillOfMaterials object into its xmlschema dictionary form for serialization to XML.

        Parameters
        ----------
        obj: BillOfMaterials

        Returns
        -------
        Dict
            xmlschema formatted object for serialization
        """
        raw_obj = self._convert_to_dict(obj)
        for k, v in self._schema.namespaces.items():
            if k != "":
                raw_obj[f"@xmlns:{k}"] = v
            else:
                raw_obj["@xmlns"] = v
        return raw_obj
