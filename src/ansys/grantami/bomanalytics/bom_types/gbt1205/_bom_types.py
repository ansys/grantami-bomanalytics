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
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from .._base_types import BaseType

if TYPE_CHECKING:
    from .._bom_reader import _GenericBoMReader
    from .._bom_writer import _GenericBoMWriter


class PseudoAttribute(Enum):
    """
    Valid values for PseudoAttribute.
    """

    Name = 0
    ShortName = 1
    Subsets = 2
    ReleasedDate = 3
    ModifiedDate = 4
    RecordType = 5
    RecordHistoryIdentity = 6
    RecordColor = 7
    LinkedRecords = 8
    VersionState = 9
    RecordGUID = 10
    RecordHistoryGUID = 11
    RecordVersionNumber = 12
    TableName = 13
    ChildRecords = 14
    TableFilters = 15

    @classmethod
    def from_string(cls, value: str) -> PseudoAttribute:
        """
        Convert string representation of this object into an instance of this object.

        Parameters
        ----------
        value: str
            String representation of this object.
        """
        return PseudoAttribute[f"{value[0].upper()}{value[1:]}"]

    def to_string(self) -> str:
        """
        Convert this Enum object to its string representation.

        Returns
        -------
        str
            String representation of this object.
        """
        return f"{self.name[0].lower()}{self.name[1:]}"


@dataclass
class PartialTableReference(BaseType):
    """
    A type that partially identifies a Table, but does not specify the MI Database. Usually, just one of the several
    optional fields should be provided; where more than one is provided, the highest priority one is used, where the
    descending priority order is: tableIdentity, tableGUID, tableName.
    """

    _simple_values = [("table_identity", "tableIdentity"), ("table_guid", "tableGUID"), ("table_name", "tableName")]

    namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

    table_identity: Optional[int] = None
    """The identity of the table, this is the fastest way to reference a table."""

    table_guid: Optional[str] = None
    """The GUID of the table, this is likely to be a persistent way to refer to a table."""

    table_name: Optional[str] = None
    """The name of the table. Note that table names can vary between localisations of a database, so this may not be a
    safe way to refer to a table if the MI Database supports multiple locales."""


@dataclass
class MIAttributeReference(BaseType):
    """A type that allows identification of a particular Attribute in an MI Database. This may be done directly by
    specifying the Identity of the Attribute, or indirectly by specifying a lookup that will match (only) the
    Attribute.

    Note: in certain cases, an MIAttributeReference may match more than one Attribute in
    the MI Database; depending on the operation, this may be legal or may result in
    a Fault.
    """

    _simple_values = [("db_key", "dbKey"), ("attribute_identity", "attributeIdentity")]

    namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

    db_key: str
    """The key that uniquely identifies a particular Database on the MI Server."""

    attribute_identity: Optional[int] = None
    """The identity of the attribute within the MI Database."""

    table_reference: Optional[PartialTableReference] = None
    """A reference to the table hosting the attribute. Required if ``attribute_name`` is specified and
    ``is_standard`` is not True."""

    attribute_name: Optional[str] = None
    """Name of the Attribute."""

    pseudo: Optional[PseudoAttribute] = None
    """The pseudo-attribute type if referring to a pseudo-attribute."""

    is_standard: Optional[bool] = None
    """If True indicates that the provided ``attribute_name`` is a Standard Name."""

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: "_GenericBoMReader") -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        name_obj = bom_reader.get_field(MIAttributeReference, obj, "name")
        if name_obj is not None:
            table_obj = bom_reader.get_field(MIAttributeReference, name_obj, "table")
            if table_obj is not None:
                props["table_reference"] = cast(
                    PartialTableReference, bom_reader.create_type("PartialTableReference", table_obj)
                )
            attribute_name_obj = bom_reader.get_field(MIAttributeReference, name_obj, "attributeName")
            if attribute_name_obj is not None:
                props["attribute_name"] = attribute_name_obj
            pseudo_obj = bom_reader.get_field(MIAttributeReference, name_obj, "pseudo")
            if pseudo_obj is not None:
                props["pseudo"] = PseudoAttribute.from_string(pseudo_obj)
            is_standard_obj = bom_reader.get_field(MIAttributeReference, name_obj, "@isStandard")
            if is_standard_obj is not None:
                props["is_standard"] = is_standard_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: "_GenericBoMWriter") -> None:
        super()._write_custom_fields(obj, bom_writer)
        name_dict: Dict[str, Any] = {}
        if self.table_reference is not None:
            name_dict[bom_writer._get_qualified_name(self, "table")] = bom_writer._convert_to_dict(self.table_reference)
        if self.attribute_name is not None:
            name_dict[bom_writer._get_qualified_name(self, "attributeName")] = self.attribute_name
        if self.pseudo is not None:
            name_dict[bom_writer._get_qualified_name(self, "pseudo")] = self.pseudo.to_string()
        if self.is_standard is not None:
            name_dict[bom_writer._get_qualified_name(self, "@isStandard")] = self.is_standard
        if name_dict != {}:
            obj[bom_writer._get_qualified_name(self, "name")] = name_dict


@dataclass
class MIRecordReference(BaseType):
    """A type that allows identification of a particular Record in an
    MI Database. This may be done directly by specifying the Identity or GUID of the Record, or
    indirectly by specifying a lookup that will match (only) the Record.

    For input, you should provide exactly one of either identity, recordGUID, recordHistoryGUID
    or lookupValue. If more than one element identifying the record is given, only one is used; the descending
    order of priority is: identity, recordGUID, recordHistoryGUID, lookupValue. The Service Layer does not
    check that the several elements identifying the record are all referencing the same record, it just picks the
    highest-priority one and uses that.
    """

    _simple_values = [
        ("db_key", "dbKey"),
        ("record_guid", "recordGUID"),
        ("record_history_guid", "recordHistoryGUID"),
        ("record_uid", "@recordUID"),
    ]

    namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

    db_key: str
    """The key that uniquely identifies a particular Database on the MI Server."""

    record_history_identity: Optional[int] = None
    """This is the best-performing and highest-priority way to reference a record; however, identities might not
    be suitable for long-term persistence."""

    record_version_number: Optional[int] = None
    """If omitted, this means the latest version visible to the user."""

    record_guid: Optional[str] = None
    """Identifies a particular version of a record by its GUID, this is a more persistent way to refer to a record."""

    record_history_guid: Optional[str] = None
    """Identifies a record history, the latest visible version will be returned. ``record_version_number`` has no
    effect on references that use ``record_history_guid``."""

    lookup_attribute_reference: Optional[MIAttributeReference] = None
    """When provided in combination with ``lookup_value`` identifies a record by a unique short-text attribute.
    Specifies the attribute to be used for the lookup operation."""

    lookup_value: Optional[str] = None
    """When provided in combination with ``lookup_attribute_reference`` identifies a record by a unique short-text
    attribute. Specifies the value to be used for the lookup operation. If this is not unique an error will be
    returned."""

    record_uid: Optional[str] = None
    """The recordUID may be used to identify a particular XML element representing a record. It does not represent
    any property or attribute of an actual MI Record."""

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: "_GenericBoMReader") -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        identity_obj = bom_reader.get_field(MIRecordReference, obj, "identity")
        if identity_obj is not None:
            props["record_history_identity"] = bom_reader.get_field(
                MIRecordReference, identity_obj, "recordHistoryIdentity"
            )
            version_obj = bom_reader.get_field(MIRecordReference, identity_obj, "version")
            if version_obj is not None:
                props["record_version_number"] = version_obj
        lookup_obj = bom_reader.get_field(MIRecordReference, obj, "lookupValue")
        if lookup_obj is not None:
            attr_ref_obj = bom_reader.get_field(MIRecordReference, lookup_obj, "attributeReference")
            props["lookup_attribute_reference"] = bom_reader.create_type("MIAttributeReference", attr_ref_obj)
            props["lookup_value"] = bom_reader.get_field(MIRecordReference, lookup_obj, "attributeValue")
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: "_GenericBoMWriter") -> None:
        super()._write_custom_fields(obj, bom_writer)
        # Always write the wrapper object, even if incomplete. This way, users get an error when serializing, rather
        # than the serialization ignoring a populated value.
        identity_dict = {}
        if self.record_history_identity is not None:
            identity_dict[bom_writer._get_qualified_name(self, "recordHistoryIdentity")] = self.record_history_identity
        if self.record_version_number is not None:
            identity_dict[bom_writer._get_qualified_name(self, "version")] = self.record_version_number
        if identity_dict:
            obj[bom_writer._get_qualified_name(self, "identity")] = identity_dict
        lookup_dict: Dict[str, Any] = {}
        if self.lookup_value is not None:
            lookup_dict[bom_writer._get_qualified_name(self, "attributeValue")] = self.lookup_value
        if self.lookup_attribute_reference is not None:
            lookup_dict[bom_writer._get_qualified_name(self, "attributeReference")] = bom_writer._convert_to_dict(
                cast(BaseType, self.lookup_attribute_reference)
            )
        if lookup_dict:
            obj[bom_writer._get_qualified_name(self, "lookupValue")] = lookup_dict
