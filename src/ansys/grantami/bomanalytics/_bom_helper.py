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

from pathlib import Path
from typing import TYPE_CHECKING, Tuple, cast

import xmlschema
from xmlschema import XMLSchema

from .bom_types import BoMReader, BoMWriter
from .schemas import bom_schema_2301

if TYPE_CHECKING:
    from .bom_types import BillOfMaterials


class BoMHandler:
    """
    Handler for XML formatted BoMs, supports reading from files and strings, and serializing to string format.

    .. versionadded:: 2.0
    """

    _schema_path: Path = bom_schema_2301
    _schema: XMLSchema

    def __init__(self) -> None:
        self._schema = XMLSchema(self._schema_path)
        self._schema.namespaces[""] = self._schema.namespaces["eco"]
        self._reader = BoMReader(self._schema)
        self._writer = BoMWriter(self._schema)

    def load_bom_from_file(self, file_path: Path) -> "BillOfMaterials":
        """
        Read a BoM from a file and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        file_path : :class:`~pathlib.Path`
            Location of the BoM XML file.

        Returns
        -------
        :class:`~._bom_types.BillOfMaterials`
        """
        with open(file_path, "r", encoding="utf8") as fp:
            obj, errors = cast(Tuple, self._schema.decode(fp, validation="lax"))

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")

        assert isinstance(obj, dict)

        return self._reader.read_bom(obj)

    def load_bom_from_text(self, bom_text: str) -> "BillOfMaterials":
        """
        Read a BoM from a string and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        bom_text : str
            String object containing an XML representation of a BoM.

        Returns
        -------
        :class:`~._bom_types.BillOfMaterials`
        """
        obj, errors = cast(Tuple, self._schema.decode(bom_text, validation="lax", keep_empty=True))

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")

        assert isinstance(obj, dict)

        return self._reader.read_bom(obj)

    def dump_bom(self, bom: "BillOfMaterials") -> str:
        """
        Convert a BillOfMaterials object into a string XML representation.

        Parameters
        ----------
        bom : :class:`~._bom_types.BillOfMaterials`

        Returns
        -------
        str
            Serialized representation of the BoM.
        """
        bom_dict = self._writer.convert_bom_to_dict(bom)
        obj, errors = self._schema.encode(
            bom_dict, validation="lax", namespaces=self._schema.namespaces, unordered=True
        )

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM object:\n{newline.join([error.msg for error in errors])}")

        output = xmlschema.etree_tostring(obj)
        assert isinstance(output, str)
        return output
