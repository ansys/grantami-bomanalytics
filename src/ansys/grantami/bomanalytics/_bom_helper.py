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
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, TextIO, Type, TypeAlias, TypeVar, cast

import xmlschema
from xmlschema import XMLSchema, XMLSchemaValidationError

from .bom_types import eco2301, eco2412
from .schemas import bom_schema_2301, bom_schema_2412

if TYPE_CHECKING:
    from .bom_types._bom_reader import GenericBoMReader
    from .bom_types._bom_writer import GenericBoMWriter
    from .bom_types.eco2301 import BillOfMaterials as BillOfMaterials2301
    from .bom_types.eco2412 import BillOfMaterials as BillOfMaterials2412


BillOfMaterials: TypeAlias = "BillOfMaterials2301 | BillOfMaterials2412"
T = TypeVar("T", bound=BillOfMaterials)

_type_map: dict[Type[BillOfMaterials], Path] = {
    eco2301.BillOfMaterials: bom_schema_2301,
    eco2412.BillOfMaterials: bom_schema_2412,
}
_mod_map: dict[Type[BillOfMaterials], ModuleType] = {
    eco2301.BillOfMaterials: eco2301,
    eco2412.BillOfMaterials: eco2412,
}


class BoMHandler:
    """
    Handler for XML formatted BoMs, supports reading from files and strings, and serializing to string format.

    .. versionadded:: 2.0

    """

    def __init__(self) -> None:
        self._schemas: list[XMLSchema] = []
        self._readers: dict[XMLSchema, "GenericBoMReader"] = {}
        self._writers: dict[XMLSchema, "GenericBoMWriter"] = {}

        for bom_type in _type_map.keys():
            self._initialize(bom_type)

    def _initialize(self, bom_type: Type[BillOfMaterials]) -> None:
        schema_file = _type_map[bom_type]
        schema = XMLSchema(schema_file)
        schema.namespaces[""] = schema.namespaces["eco"]
        self._schemas.append(schema)

        mod = _mod_map[bom_type]
        self._readers[schema] = mod.BoMReader(schema)
        self._writers[schema] = mod.BoMWriter(schema)

    def load_bom_from_file(self, file_path: Path) -> BillOfMaterials:
        """
        Read a BoM from a file and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        file_path : :class:`~pathlib.Path`
            Location of the BoM XML file.

        Returns
        -------
        :class:`eco2301.BillOfMaterials <.eco2301._bom_types.BillOfMaterials>` or :class:`eco2412.BillOfMaterials <.eco2412._bom_types.BillOfMaterials>`  # noqa: E501
        """
        deserializer = _Deserializer(self._schemas)
        with open(file_path, "r", encoding="utf-8") as fp:
            result = deserializer.deserialize_file(fp)
        bom = self._readers[deserializer.selected_schema].read_bom(result)
        return cast(BillOfMaterials, bom)

    def load_bom_from_text(self, bom_text: str) -> BillOfMaterials:
        """
        Read a BoM from a string and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        bom_text : str
            String object containing an XML representation of a BoM.

        Returns
        -------
        :class:`eco2301.BillOfMaterials <.eco2301._bom_types.BillOfMaterials>` or :class:`eco2412.BillOfMaterials <.eco2412._bom_types.BillOfMaterials>`  # noqa: E501
        """
        deserializer = _Deserializer(self._schemas)
        result = deserializer.deserialize_string(bom_text)
        bom = self._readers[deserializer.selected_schema].read_bom(result)
        return cast(BillOfMaterials, bom)

    def convert(self, bom: BillOfMaterials, target_bom_version: Type[T]) -> T:
        """
        Convert a BoM from one version to another.

        .. versionadded:: 2.3

        Parameters
        ----------
        bom : :class:`eco2301.BillOfMaterials <.eco2301._bom_types.BillOfMaterials>` or :class:`eco2412.BillOfMaterials <.eco2412._bom_types.BillOfMaterials>`  # noqa: E501
            The BoM to convert.
        target_bom_version : Type[:class:`eco2301.BillOfMaterials <.eco2301._bom_types.BillOfMaterials>`] or Type[:class:`eco2412.BillOfMaterials <.eco2412._bom_types.BillOfMaterials>`]  # noqa: E501
            The *definition* of a BoM class to convert the provided BoM to.

        Returns
        -------
        :class:`eco2301.BillOfMaterials <.eco2301._bom_types.BillOfMaterials>` or :class:`eco2412.BillOfMaterials <.eco2412._bom_types.BillOfMaterials>`  # noqa: E501
        """
        if target_bom_version not in _type_map:
            raise ValueError("BoM not valid target")

        current_eco_namespace = ""
        bom_dict: dict[str, Any] = {}
        for schema, writer in self._writers.items():
            try:
                bom_dict = writer.convert_bom_to_dict(bom)
                current_eco_namespace = schema.namespaces["eco"]
                break
            except KeyError:
                pass
        if current_eco_namespace is None:
            raise ValueError("bom is not complaint with any known schema")

        target_eco_namespace = target_bom_version._namespace
        self._modify_namespace(bom_dict, current_eco_namespace, target_eco_namespace)

        target_reader = next(r for r in self._readers.values() if r.eco_namespace == target_eco_namespace)
        return cast(T, target_reader.read_bom(bom_dict))

    def _modify_namespace(self, obj: dict[str, Any], current_namespace: str, new_namespace: str) -> None:
        for k, v in obj.items():
            if k.startswith("@xmlns") and v == current_namespace:
                obj[k] = new_namespace
            elif isinstance(v, dict):
                self._modify_namespace(v, current_namespace, new_namespace)

    def dump_bom(self, bom: BillOfMaterials) -> str:
        """
        Convert a BillOfMaterials object into a string XML representation.

        Parameters
        ----------
        bom : :class:`eco2301.BillOfMaterials <.eco2301._bom_types.BillOfMaterials>` or :class:`eco2412.BillOfMaterials <.eco2412._bom_types.BillOfMaterials>`  # noqa: E501

        Returns
        -------
        str
            Serialized representation of the BoM.
        """
        obj = None
        errors = []

        for schema, writer in self._writers.items():
            try:
                bom_dict = writer.convert_bom_to_dict(bom)
                obj, errors = schema.encode(bom_dict, validation="lax", namespaces=schema.namespaces, unordered=True)
                break
            except KeyError:
                pass
        if not obj or len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM object:\n{newline.join([error.msg for error in errors])}")

        output = xmlschema.etree_tostring(obj)
        assert isinstance(output, str)
        return output


class _Deserializer:
    def __init__(self, schemas: list[XMLSchema]):
        self._schemas = schemas
        self._selected_schema: XMLSchema | None = None

    @property
    def selected_schema(self) -> XMLSchema:
        if not self._selected_schema:
            raise ValueError
        return self._selected_schema

    def deserialize_file(self, bom: TextIO) -> Any:
        for schema in self._schemas:
            try:
                result = schema.decode(
                    bom,
                    validation="lax",
                    keep_empty=True,
                    xmlns_processing="collapsed",
                )
                self._selected_schema = schema
                return self._postprocess_output(result)
            except xmlschema.exceptions.XMLSchemaKeyError:
                bom.seek(0)
        raise ValueError("Invalid BoM")

    def deserialize_string(self, bom: str) -> Any:
        for schema in self._schemas:
            try:
                result = schema.decode(
                    bom,
                    validation="lax",
                    keep_empty=True,
                    xmlns_processing="collapsed",
                )
                self._selected_schema = schema
                return self._postprocess_output(result)
            except xmlschema.exceptions.XMLSchemaKeyError:
                pass
        raise ValueError("Invalid BoM")

    @staticmethod
    def _postprocess_output(result: tuple[Any | None, list[XMLSchemaValidationError]] | None) -> Any:
        if result is None:
            raise ValueError("BoM could not be deserialized.")
        deserialized_bom, errors = result
        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")
        return cast(Any, deserialized_bom)
