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
from typing import TYPE_CHECKING, Any, Optional, TextIO

import xmlschema
from xmlschema import XMLSchema, XMLSchemaValidationError

from .bom_types import eco2301, eco2412
from .schemas import bom_schema_2301, bom_schema_2412

if TYPE_CHECKING:
    from .bom_types._base_types import BaseBoMReader, BaseBoMWriter
    from .bom_types.eco2301 import BillOfMaterials as BillOfMaterials2301
    from .bom_types.eco2412 import BillOfMaterials as BillOfMaterials2412

type_map = {
    bom_schema_2301: eco2301,
    bom_schema_2412: eco2412,
}


class BoMHandler:
    """
    Handler for XML formatted BoMs, supports reading from files and strings, and serializing to string format.

    .. versionadded:: 2.0

    Parameters
    ----------
    bom_schema : :class:`~pathlib.Path`, optional
        The BoM schema used to validate against when reading and writing the BoM. Only the paths available in the
        :ref:`ref_grantami_bomanalytics_api_bomschemas` submodule are permitted as values for this parameter. If not
        provided, schemas will be used in the following order:

        1. :attr:`~ansys.grantami.bomanalytics.schemas.bom_schema_2301`
        2. :attr:`~ansys.grantami.bomanalytics.schemas.bom_schema_2412`

        .. versionadded:: 2.3
    """

    def __init__(self, bom_schema: Optional[Path] = None) -> None:
        self._schemas: list[XMLSchema] = []
        self._readers: dict[XMLSchema, "BaseBoMReader"] = {}
        self._writers: dict[XMLSchema, "BaseBoMWriter"] = {}

        if bom_schema:
            self._initialize_schema(bom_schema)
            return

        for bom_schema in type_map.keys():
            self._initialize_schema(bom_schema)

    def _initialize_schema(self, bom_schema: Path) -> None:
        schema = XMLSchema(bom_schema)
        schema.namespaces[""] = schema.namespaces["eco"]
        self._schemas.append(schema)
        self._readers[schema] = type_map[bom_schema].BoMReader(schema)
        self._writers[schema] = type_map[bom_schema].BoMWriter(schema)

    def load_bom_from_file(self, file_path: Path) -> "BillOfMaterials2301 | BillOfMaterials2412":
        """
        Read a BoM from a file and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        file_path : :class:`~pathlib.Path`
            Location of the BoM XML file.

        Returns
        -------
        :class:`~._bom_types.eco2301.BillOfMaterials` or :class:`~._bom_types.eco2412.BillOfMaterials`
        """
        deserializer = _Deserializer(self._schemas)

        with open(file_path, "r", encoding="utf8") as fp:
            deserializer._deserialize_file(fp)

        if len(deserializer.errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in deserializer.errors])}")

        assert isinstance(deserializer.object, dict)

        return self._readers[deserializer.selected_schema].read_bom(deserializer.result)  # type: ignore

    def load_bom_from_text(self, bom_text: str) -> "BillOfMaterials2301 | BillOfMaterials2412":
        """
        Read a BoM from a string and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        bom_text : str
            String object containing an XML representation of a BoM.

        Returns
        -------
        :class:`~._bom_types.eco2301.BillOfMaterials` or :class:`~._bom_types.eco2412.BillOfMaterials`
        """
        deserializer = _Deserializer(self._schemas)
        deserializer._deserialize_string(bom_text)

        if len(deserializer.errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in deserializer.errors])}")

        assert isinstance(deserializer.object, dict)

        return self._readers[deserializer.selected_schema].read_bom(deserializer.result)  # type: ignore

    # def convert_bom(self, bom: "BillOfMaterials2301 | BillOfMaterials2412"):
    #     pass

    def dump_bom(self, bom: "BillOfMaterials2301 | BillOfMaterials2412") -> str:
        """
        Convert a BillOfMaterials object into a string XML representation.

        Parameters
        ----------
        bom : :class:`~._bom_types.eco2301.BillOfMaterials` or :class:`~._bom_types.eco2412.BillOfMaterials`

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
        self.selected_schema: XMLSchema | None = None
        self.object: Any = None
        self.errors: list[XMLSchemaValidationError] = []

    def _deserialize_file(self, bom: TextIO) -> None:
        for schema in self._schemas:
            try:
                result = schema.decode(
                    bom,
                    validation="lax",
                    keep_empty=True,
                    xmlns_processing="collapsed",
                )
                self.selected_schema = schema
                if result:
                    self.object, self.errors = result
                return
            except xmlschema.exceptions.XMLSchemaKeyError:
                bom.seek(0)
        raise ValueError("Invalid BoM")

    def _deserialize_string(self, bom: str) -> None:
        for schema in self._schemas:
            try:
                result = schema.decode(
                    bom,
                    validation="lax",
                    keep_empty=True,
                    xmlns_processing="collapsed",
                )
                self.selected_schema = schema
                if result:
                    self.object, self.errors = result
                return
            except xmlschema.exceptions.XMLSchemaKeyError:
                pass
        raise ValueError("Invalid BoM")
