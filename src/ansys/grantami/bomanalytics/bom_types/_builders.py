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

from typing import Optional

from .gbt1205._bom_types import (
    MIAttributeReference,
    MIRecordReference,
    PartialTableReference,
    PseudoAttribute,
)


class _AttributeReferenceByNameBuilder:
    _parent: AttributeReferenceBuilder

    def __init__(self, root_builder: AttributeReferenceBuilder) -> None:
        self._parent = root_builder

    def with_table_name(self, table_name: str) -> _FinalAttributeReferenceBuilder:
        """
        Specify the table by name

        Parameters
        ----------
        table_name : str
            The name of the table (TODO - Display names?)

        Returns
        -------
        _FinalAttributeReferenceBuilder
        """
        table_reference = PartialTableReference()
        table_reference.table_name = table_name
        self._set_table_reference(table_reference)
        return _FinalAttributeReferenceBuilder(self._parent)

    def with_table_identity(self, table_identity: int) -> _FinalAttributeReferenceBuilder:
        """
        Specify the table by its identity

        Parameters
        ----------
        table_identity : int
            The integer table identity

        Returns
        -------
        _FinalAttributeReferenceBuilder
        """
        table_reference = PartialTableReference()
        table_reference.table_identity = table_identity
        self._set_table_reference(table_reference)
        return _FinalAttributeReferenceBuilder(self._parent)

    def with_table_guid(self, table_guid: str) -> _FinalAttributeReferenceBuilder:
        """
        Specify the table by its GUID

        Parameters
        ----------
        table_guid : str
            The table GUID

        Returns
        -------
        _FinalAttributeReferenceBuilder
        """
        table_reference = PartialTableReference()
        table_reference.table_guid = table_guid
        self._set_table_reference(table_reference)
        return _FinalAttributeReferenceBuilder(self._parent)

    def _set_table_reference(self, table_reference: PartialTableReference) -> None:
        self._parent._build.table_reference = table_reference


class _FinalAttributeReferenceBuilder:
    _source: AttributeReferenceBuilder

    def __init__(self, source: AttributeReferenceBuilder) -> None:
        self._source = source

    def build(self) -> MIAttributeReference:
        """
        Build the finished MI Attribute Reference

        Returns
        -------
        MIAttributeReference
        """
        return self._source._build


class AttributeReferenceBuilder:
    """
    Create a MI Attribute Reference with a valid combination of properties.

    .. versionadded:: 2.0

    Parameters
    ----------
    db_key : str
        Database Key specifying the database the Attribute is in.
    """

    _build: MIAttributeReference

    def __init__(self, db_key: str) -> None:
        self._build = MIAttributeReference(db_key=db_key)

    def with_attribute_identity(self, attribute_identity: int) -> _FinalAttributeReferenceBuilder:
        """
        Specify the attribute by its identity.

        Parameters
        ----------
        attribute_identity : int
            The attribute's identity.

        Returns
        -------
        _FinalAttributeReferenceBuilder
        """
        self._build.attribute_identity = attribute_identity
        return _FinalAttributeReferenceBuilder(self)

    def as_pseudo_attribute(self, pseudo_attribute: PseudoAttribute) -> _FinalAttributeReferenceBuilder:
        """
        Specify the attribute as a specific pseudo-attribute.

        Parameters
        ----------
        pseudo_attribute : :class:`~._bom_types.PseudoAttribute`

        Returns
        -------
        _FinalAttributeReferenceBuilder
        """
        self._build.pseudo = pseudo_attribute
        return _FinalAttributeReferenceBuilder(self)

    def with_attribute_name(
        self, attribute_name: str, *, is_standard_name: bool = False
    ) -> _AttributeReferenceByNameBuilder:
        """
        Specify the attribute by name, which may be a standard name.

        Parameters
        ----------
        attribute_name : str
            The attribute's name.
        is_standard_name : bool
            If True, the attribute is defined by a standard name (default false).

        Returns
        -------
        _AttributeReferenceByNameBuilder
        """
        self._build.attribute_name = attribute_name
        self._build.is_standard = is_standard_name
        return _AttributeReferenceByNameBuilder(self)


class RecordReferenceBuilder:
    """
    Create a MIRecordReference with a valid combination of properties.

    .. versionadded:: 2.0

    Parameters
    ----------
    db_key : str
        Database key specifying the database to which the Record belongs.
    record_uid : Optional[str]
        Optional identifier to annotate this record reference, will be returned with the response unchanged.
    """

    _build: MIRecordReference

    def __init__(self, db_key: str, *, record_uid: Optional[str] = None) -> None:
        self._build = MIRecordReference(db_key=db_key, record_uid=record_uid)

    def with_record_history_id(
        self, record_history_id: int, *, record_version_number: Optional[int] = None
    ) -> _FinalRecordReferenceBuilder:
        """
        Specify the record by its history identity, and optionally the version number if the record is in a
        Version-Controlled table.

        Parameters
        ----------
        record_history_id : int
            The record history identity.
        record_version_number : Optional[int]
            If the record is in a Version-Controlled table, return a specific version of the record, otherwise
            the latest released version will be returned.

        Returns
        -------
        _FinalRecordReferenceBuilder
        """
        self._build.record_history_identity = record_history_id
        self._build.record_version_number = record_version_number
        return _FinalRecordReferenceBuilder(self)

    def with_record_guid(self, record_guid: str) -> _FinalRecordReferenceBuilder:
        """
        Specify the record by its GUID.

        This will specify an exact version if the table is Version-Controlled.

        Parameters
        ----------
        record_guid : str
            The record version GUID.

        Returns
        -------
        _FinalRecordReferenceBuilder
        """
        self._build.record_guid = record_guid
        return _FinalRecordReferenceBuilder(self)

    def with_record_history_guid(self, record_history_guid: str) -> _FinalRecordReferenceBuilder:
        """
        Specify the record by its History GUID.

        This will return the latest released version of the record. If a specific version is required then use the
        ``with_record_guid`` method instead.

        Parameters
        ----------
        record_history_guid : str
            The record history GUID.

        Returns
        -------
        _FinalRecordReferenceBuilder
        """
        self._build.record_history_guid = record_history_guid
        return _FinalRecordReferenceBuilder(self)

    def with_lookup_value(
        self, *, lookup_value: str, lookup_attribute_reference: MIAttributeReference
    ) -> _FinalRecordReferenceBuilder:
        """
        Specify the record by a unique value on a short-text attribute.

        You must specify both the attribute and the lookup value. If the value is not unique then an exception will be
        raised.

        Parameters
        ----------
        lookup_value : str
            The value identifying the record.
        lookup_attribute_reference : :class:`.MIAttributeReference`
            The short-text attribute or compatible pseudo-attribute to use for the lookup.

        Returns
        -------
        _FinalRecordReferenceBuilder
        """
        self._build.lookup_value = lookup_value
        self._build.lookup_attribute_reference = lookup_attribute_reference
        return _FinalRecordReferenceBuilder(self)


class _FinalRecordReferenceBuilder:
    _source: RecordReferenceBuilder

    def __init__(self, source: RecordReferenceBuilder) -> None:
        self._source = source

    def build(self) -> MIRecordReference:
        """
        Build the finished MI Record Reference.

        Returns
        -------
        MIRecordReference
        """
        return self._source._build
