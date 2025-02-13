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
from typing import TYPE_CHECKING, Any, Dict, List, TextIO, Tuple, Union, cast

import xmlschema
from xmlschema import XMLSchema

from .bom_types.eco2301._bom_reader import BoMReader
from .bom_types.eco2301._bom_writer import BoMWriter
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

    def load_bom_from_file(self, file_path: Path, allow_unsupported_data: bool = True) -> "BillOfMaterials":
        """
        Read a BoM from a file and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        file_path : :class:`~pathlib.Path`
            Location of the BoM XML file.
        allow_unsupported_data : bool, default: True
            If ``False``, an exception is raised if there is data in the BoM XML that cannot be deserialized.

            .. versionadded:: 2.3

        Returns
        -------
        :class:`~._bom_types.BillOfMaterials`

        Raises
        ------
        ValueError
            If the BoM cannot be deserialized. Additional detail is included in the exception message.
        ValueError
            If the BoM contains data that cannot be represented by the classes in the
            :ref:`ref_grantami_bomanalytics_bom_eco2301` and ``allow_unsupported_data = False`` is specified. The
            additional data fields are reported in the exception message.
        """
        with open(file_path, "r", encoding="utf8") as fp:
            obj, errors = self._deserialize_bom(fp)

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")

        assert isinstance(obj, dict)

        bom, undeserialized_fields = self._reader.read_bom(obj)
        if undeserialized_fields and not allow_unsupported_data:
            self._raise_undeserialized_fields(undeserialized_fields)
        return bom

    def load_bom_from_text(self, bom_text: str, allow_unsupported_data: bool = True) -> "BillOfMaterials":
        """
        Read a BoM from a string and return the corresponding BillOfMaterials object for use.

        Parameters
        ----------
        bom_text : str
            String object containing an XML representation of a BoM.
        allow_unsupported_data : bool, default: True
            If ``False``, an exception is raised if there is data in the BoM XML that cannot be deserialized.

            .. versionadded:: 2.3

        Returns
        -------
        :class:`~._bom_types.BillOfMaterials`

        Raises
        ------
        ValueError
            If the BoM cannot be deserialized. Additional detail is included in the exception message.
        ValueError
            If the BoM contains data that cannot be represented by the classes in the
            :ref:`ref_grantami_bomanalytics_bom_eco2301` and ``allow_unsupported_data = False`` is specified. The
            additional data fields are reported in the exception message.
        """
        obj, errors = self._deserialize_bom(bom_text)

        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")

        assert isinstance(obj, dict)

        bom, undeserialized_fields = self._reader.read_bom(obj)
        if undeserialized_fields and not allow_unsupported_data:
            self._raise_undeserialized_fields(undeserialized_fields)
        return bom

    @staticmethod
    def _raise_undeserialized_fields(fields: list[str]) -> None:
        formatted_fields = "  \n".join(fields)
        raise ValueError(f"The following fields in the provided BoM could not be deserialized:\n{formatted_fields}")

    def _deserialize_bom(self, bom: Union[TextIO, str]) -> Tuple[Dict[str, Any], List]:
        """
        Deserialize either a string or I/O stream BoM.

        Parameters
        ----------
        bom : Union[TextIO, str]
            Object containing an XML representation of a BoM, either as text or I/O stream.

        Returns
        -------
        Tuple[Dict[str, Any], List]
            A tuple of the deserialized dictionary and a list of errors.
        """
        result = self._schema.decode(bom, validation="lax", keep_empty=True, xmlns_processing="collapsed")
        return cast(Tuple[Dict[str, Any], List], result)

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
