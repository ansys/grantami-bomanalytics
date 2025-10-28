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
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, TextIO, Type, TypeAlias, TypeVar, cast

import xmlschema
from xmlschema import XMLSchema, XMLSchemaValidationError

from .bom_types import eco2301, eco2412, eco2505
from .schemas import bom_schema_2301, bom_schema_2412, bom_schema_2505

if TYPE_CHECKING:
    from .bom_types import _GenericBoMReader, _GenericBoMWriter
    from .bom_types.eco2301 import BillOfMaterials as BillOfMaterials2301
    from .bom_types.eco2412 import BillOfMaterials as BillOfMaterials2412
    from .bom_types.eco2505 import BillOfMaterials as BillOfMaterials2505


T = TypeVar("T", "BillOfMaterials2301", "BillOfMaterials2412", "BillOfMaterials2505")
BillOfMaterials: TypeAlias = "BillOfMaterials2301 | BillOfMaterials2412 | BillOfMaterials2505"

_type_map: dict[Type[BillOfMaterials], Path] = {
    eco2301.BillOfMaterials: bom_schema_2301,
    eco2412.BillOfMaterials: bom_schema_2412,
    eco2505.BillOfMaterials: bom_schema_2505,
}
_mod_map: dict[Type[BillOfMaterials], ModuleType] = {
    eco2301.BillOfMaterials: eco2301,
    eco2412.BillOfMaterials: eco2412,
    eco2505.BillOfMaterials: eco2505,
}


class BoMHandler:
    """
    Handler for XML formatted BoMs.

    Supports reading from files and strings, serializing to string format, and converting BoMs between different
    versions.

    .. versionadded:: 2.0
    """

    def __init__(self) -> None:
        self._schemas: list[XMLSchema] = []
        self._readers: dict[XMLSchema, "_GenericBoMReader"] = {}
        self._writers: dict[XMLSchema, "_GenericBoMWriter"] = {}

        for bom_type in _type_map.keys():
            self._initialize(bom_type)

    def _initialize(self, bom_type: Type[BillOfMaterials]) -> None:
        schema_file = _type_map[bom_type]
        schema = XMLSchema(schema_file)
        schema.namespaces[""] = schema.namespaces["eco"]
        self._schemas.append(schema)

        mod = _mod_map[bom_type]
        self._readers[schema] = mod._BoMReader(schema)
        self._writers[schema] = mod._BoMWriter(schema)

    def _get_xmlschema_for_bom(self, bom: BillOfMaterials) -> XMLSchema:
        try:
            return next(schema for schema, writer in self._writers.items() if writer.target_namespace == bom.namespace)
        except StopIteration:
            raise ValueError("Invalid BoM. BoM is not compliant with any supported Ansys Granta BoM XML schema.")

    def load_bom_from_file(self, file_path: Path, allow_unsupported_data: bool = True) -> BillOfMaterials:
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
        :class:`.eco2412.BillOfMaterials` or :class:`.eco2301.BillOfMaterials`

        Raises
        ------
        ValueError
            If the BoM cannot be deserialized. Additional detail is included in the exception message.
        ValueError
            If the BoM contains data that cannot be represented by :ref:`ref_grantami_bomanalytics_bom_eco2412` or
            :ref:`ref_grantami_bomanalytics_bom_eco2301` classes and ``allow_unsupported_data = False`` is specified.
            The additional data fields are reported in the exception message.
        """
        deserializer = _Deserializer(self._schemas)
        with open(file_path, "r", encoding="utf-8") as fp:
            result = deserializer.deserialize_file(fp)
        bom, undeserialized_fields = self._readers[result.selected_schema].read_bom(result.bom)
        if undeserialized_fields and not allow_unsupported_data:
            self._raise_undeserialized_fields(undeserialized_fields)
        return cast(BillOfMaterials, bom)

    def load_bom_from_text(self, bom_text: str, allow_unsupported_data: bool = True) -> BillOfMaterials:
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
        :class:`.eco2412.BillOfMaterials` or :class:`.eco2301.BillOfMaterials`

        Raises
        ------
        ValueError
            If the BoM cannot be deserialized.
        ValueError
            If the BoM contains data that cannot be represented by :ref:`ref_grantami_bomanalytics_bom_eco2412` or
            :ref:`ref_grantami_bomanalytics_bom_eco2301` classes and ``allow_unsupported_data = False`` is specified.
            The additional data fields are reported in the exception message.
        """
        deserializer = _Deserializer(self._schemas)
        result = deserializer.deserialize_string(bom_text)
        bom, undeserialized_fields = self._readers[result.selected_schema].read_bom(result.bom)
        if undeserialized_fields and not allow_unsupported_data:
            self._raise_undeserialized_fields(undeserialized_fields)
        return cast(BillOfMaterials, bom)

    def convert(self, bom: BillOfMaterials, target_bom_version: Type[T], allow_unsupported_data: bool = True) -> T:
        """
        Convert a BoM from one version to another.

        The BoM is returned as an instance of the type specified in the ``target_bom_version`` argument.

        .. versionadded:: 2.3

        Parameters
        ----------
        bom : :class:`.eco2412.BillOfMaterials` or :class:`.eco2301.BillOfMaterials`
            The BoM to convert.
        target_bom_version : Type[:class:`.eco2412.BillOfMaterials`] | Type[:class:`.eco2301.BillOfMaterials`]
            The ``BillOfMaterials`` class to convert the provided BoM to. Must be a **class**, not an instance of a
            class.
        allow_unsupported_data : bool, default: True
            If ``False``, an exception is raised if there is data in the provided BoM that cannot be represented in the
            target BoM version.

        Returns
        -------
        :class:`.eco2412.BillOfMaterials` or :class:`.eco2301.BillOfMaterials`

        Raises
        ------
        ValueError
            If the BoM cannot be deserialized. Additional detail is included in the exception message.
        ValueError
            If the BoM contains data that cannot be represented by classes in the target XML namespace and
            ``allow_unsupported_data = False`` is specified.
        ValueError
            If the ``target_bom_version`` argument is invalid.
        """
        if target_bom_version not in _type_map:
            raise ValueError(f'target_bom_version "{target_bom_version}" is not a valid BoM target.')

        # Convert Python objects to dictionary
        schema = self._get_xmlschema_for_bom(bom)
        writer = self._writers[schema]

        bom_dict = writer.convert_bom_to_dict(bom)
        current_eco_namespace = schema.namespaces["eco"]

        # Replace namespace recursively through dictionary
        target_eco_namespace = target_bom_version.namespace
        self._modify_namespace(bom_dict, current_eco_namespace, target_eco_namespace)

        # Convert dictionary to Python objects
        target_reader = next(r for r in self._readers.values() if r.target_namespace == target_eco_namespace)
        converted_bom, undeserialized_fields = target_reader.read_bom(bom_dict)
        if undeserialized_fields and not allow_unsupported_data:
            self._raise_undeserialized_fields(undeserialized_fields)
        return cast(T, converted_bom)

    @staticmethod
    def _raise_undeserialized_fields(fields: list[str]) -> None:
        formatted_fields = "  \n".join(fields)
        raise ValueError(f"The following fields in the provided BoM could not be deserialized:\n{formatted_fields}")

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
        bom : :class:`.eco2412.BillOfMaterials` or :class:`.eco2301.BillOfMaterials`

        Returns
        -------
        str
            Serialized representation of the BoM.
        """
        schema = self._get_xmlschema_for_bom(bom)
        writer = self._writers[schema]

        bom_dict = writer.convert_bom_to_dict(bom)
        result = schema.encode(bom_dict, validation="lax", namespaces=schema.namespaces, unordered=True)
        if result is None:
            raise ValueError("Unhandled error during BoM serialization.")

        obj, errors = result

        if obj is None or len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM object:\n{newline.join([error.msg for error in errors])}")

        output = xmlschema.etree_tostring(obj)
        return cast(str, output)


@dataclass
class _DeserializedBoM:
    bom: dict[str, Any]
    selected_schema: XMLSchema


class _Deserializer:
    def __init__(self, schemas: list[XMLSchema]):
        """
        Deserializes an XML BoM to a dictionary given a list of valid xmlschema.XMLSchema objects.

        Parameters
        ----------
        schemas : list[xmlschema.XMLSchema]
            The valid schemas against which to validate the incoming XML BoM.
        """
        self._schemas = schemas

    def deserialize_file(self, bom: TextIO) -> _DeserializedBoM:
        """
        Deserialize an XML BoM provided as a :class:`TextIO` object.

        Returns
        -------
        dict
            The deserialized BoM.

        Raises
        ------
        ValueError
            If the BoM could not be deserialized.
        """
        for schema in self._schemas:
            try:
                result = schema.decode(
                    bom,
                    validation="lax",
                    keep_empty=True,
                    xmlns_processing="collapsed",
                )
                deserialized_bom = self._postprocess_output(result)
                return _DeserializedBoM(deserialized_bom, schema)
            except xmlschema.exceptions.XMLSchemaKeyError:
                bom.seek(0)
        raise ValueError("Invalid BoM. BoM is not compliant with any supported Ansys Granta BoM XML schema.")

    def deserialize_string(self, bom: str) -> _DeserializedBoM:
        """
        Deserialize an XML BoM provided as a :class:`str` object.

        Returns
        -------
        dict
            The deserialized BoM.

        Raises
        ------
        ValueError
            If the BoM could not be deserialized.
        """
        for schema in self._schemas:
            try:
                result = schema.decode(
                    bom,
                    validation="lax",
                    keep_empty=True,
                    xmlns_processing="collapsed",
                )
                deserialized_bom = self._postprocess_output(result)
                return _DeserializedBoM(deserialized_bom, schema)
            except xmlschema.exceptions.XMLSchemaKeyError:
                pass
        raise ValueError("Invalid BoM. BoM is not compliant with any supported Ansys Granta BoM XML schema.")

    @staticmethod
    def _postprocess_output(result: tuple[Any | None, list[XMLSchemaValidationError]] | None) -> dict:
        """
        Raise any errors returned by xmlschema.XMLSchema.decode() as exceptions and return the result.

        Returns
        -------
        dict
            The deserialized BoM.

        Raises
        ------
        ValueError
            If any errors were returned by xmlschema.XMLSchema.decode()
        """
        if result is None:
            raise ValueError("BoM could not be deserialized.")
        deserialized_bom, errors = result
        if len(errors) > 0:
            newline = "\n"
            raise ValueError(f"Invalid BoM:\n{newline.join([error.msg for error in errors])}")
        return cast(dict, deserialized_bom)
