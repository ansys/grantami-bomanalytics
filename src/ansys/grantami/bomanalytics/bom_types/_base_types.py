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

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Protocol, Tuple


@dataclass(frozen=True)
class QualifiedXMLName:
    """A fully qualified XML element, including both namespace and local name."""

    local_name: str
    namespace: str


class HasNamespace(Protocol):
    """
    Protocol defining that an inheritor has an attribute *namespace*.
    """

    namespace: str


class SupportsCustomFields(Protocol):
    """
    Protocol defining that an inheritor has methods to process and write custom fields.
    """

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: Any) -> Dict[str, Any]: ...

    def _write_custom_fields(self, obj: Dict, bom_writer: Any) -> None: ...


class BaseType(HasNamespace, SupportsCustomFields):
    """Base type from which all XML DTOs inherit.

    Handles conversion from python properties to xmlschema objects.

    Attributes
    ----------
    _props : List[Tuple[str, str, QualifiedXMLName]]
        Properties that map to complex types in XML. The entries are the type target, the python attribute name
        and the element QualifiedXMLName.
    _list_props : List[Tuple[str, str, QualifiedXMLName, QualifiedXMLName]]
        Properties that map to sequences of complex types in XML. The entries are the type target for each entry, the
        python property name, the container QualifiedXMLName, and the item QualifiedXMLName.
    _simple_values : List[Tuple[str, QualifiedXMLName]]
        Properties that map to simple types in XML. The entries are the python property name and the element
        QualifiedXMLName.
    _namespaces : Dict[str, str]
        Mapping from XML namespace prefix to namespace URI.
    namespace : str
        XML Namespace URI for the object, should exist as a value in the ``_namespaces`` map.
    """

    _props: List[Tuple[str, str, QualifiedXMLName]] = []
    _list_props: List[Tuple[str, str, QualifiedXMLName, QualifiedXMLName]] = []
    _simple_values: List[Tuple[str, QualifiedXMLName]] = []

    _namespaces: Dict[str, str] = {}

    def __init__(self, *args: Iterable, **kwargs: Dict[str, Any]) -> None: ...

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: Any) -> Dict[str, Any]:
        """
        Populates any fields on the object that are in a nonstandard configuration. This can be anonymous complex types,
        Sequences of simple types and similar. This is called after the standard deserialization occurs, and should
        return a dictionary mapping constructor argument names to values.

        Parameters
        ----------
        obj: Dict
            The json representation of the source XML BoM to be parsed.
        bom_reader: BaseBoMReader
            Helper object that maintains information about the global namespaces.

        Returns
        -------
        Dict[str, Any]
            Dictionary mapping constructor argument names to values for this type.
        """
        return {}

    def _write_custom_fields(self, obj: Dict, bom_writer: Any) -> None:
        """
        Writes any fields on the serialized object that are in a nonstandard configuration. This can be anonymous
        complex types, Sequences of simple types and similar. This is called after the standard serialization occurs,
        and should modify the ``obj`` argument in place.

        Parameters
        ----------
        obj: Dict
            Dictionary representing the current state of the serialization of self. Modified in place by this method.
        bom_writer: BaseBoMWriter
            Helper object that maintains information about the global namespaces.
        """
