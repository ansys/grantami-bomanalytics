from typing import Optional

from ansys.grantami.bomanalytics.bom_types import (
    PartialTableReference,
    MIAttributeReference,
    PseudoAttribute,
    MIRecordReference,
)


class _AttributeReferenceByNameBuilder:
    _parent: "AttributeReferenceBuilder"

    def __init__(self, root_builder: "AttributeReferenceBuilder") -> None:
        self._parent = root_builder

    def with_table_name(self, table_name: str) -> "AttributeReferenceBuilder":
        table_reference = PartialTableReference()
        table_reference.table_name = table_name
        self._set_table_reference(table_reference)
        return self._parent

    def with_table_identity(self, table_identity: int) -> "AttributeReferenceBuilder":
        table_reference = PartialTableReference()
        table_reference.table_identity = table_identity
        self._set_table_reference(table_reference)
        return self._parent

    def with_table_guid(self, table_guid: str) -> "AttributeReferenceBuilder":
        table_reference = PartialTableReference()
        table_reference.table_guid = table_guid
        self._set_table_reference(table_reference)
        return self._parent

    def _set_table_reference(self, table_reference: "PartialTableReference") -> None:
        self._parent._build.table_reference = table_reference
        self._parent._is_complete = True


class _FinalAttributeReferenceBuilder:
    _source: "AttributeReferenceBuilder"

    def __init__(self, source: "AttributeReferenceBuilder") -> None:
        self._source = source

    def build(self) -> "MIAttributeReference":
        return self._source._build


class AttributeReferenceBuilder:
    _build: "MIAttributeReference"
    _is_complete: bool

    def __init__(self, *, db_key: str) -> None:
        self._build = MIAttributeReference()
        self._build.db_key = db_key
        self._is_complete = False

    def with_attribute_identity(self, attribute_identity: int) -> "AttributeReferenceBuilder":
        self._build.attribute_identity = attribute_identity
        self._is_complete = True
        return self

    def as_pseudo_attribute(self, pseudo_attribute: PseudoAttribute) -> "AttributeReferenceBuilder":
        self._build.pseudo = pseudo_attribute
        self._is_complete = True
        return self

    def with_attribute_name(self, attribute_name: str, is_standard_name: bool = False):
        self._build.attribute_name = attribute_name
        self._build.is_standard = is_standard_name
        return _AttributeReferenceByNameBuilder(self)


class RecordReferenceBuilder:
    _build: "MIRecordReference"

    def __init__(self, *, db_key: str, record_uid: Optional[str] = None) -> None:
        self._build = MIRecordReference()
        self._build.db_key = db_key
        self._build.record_uid = record_uid

    def with_record_history_id(
        self, record_history_id: int, *, record_version_number: Optional[int] = None
    ) -> "_FinalRecordReferenceBuilder":
        self._build.record_history_identity = record_history_id
        self._build.record_version_number = record_version_number
        return _FinalRecordReferenceBuilder(self)

    def with_record_guid(self, record_guid: str) -> "_FinalRecordReferenceBuilder":
        self._build.record_guid = record_guid
        return _FinalRecordReferenceBuilder(self)

    def with_record_history_guid(self, record_history_guid: str) -> "_FinalRecordReferenceBuilder":
        self._build.record_history_guid = record_history_guid
        return _FinalRecordReferenceBuilder(self)

    def with_lookup_value(
        self, *, lookup_value: str, lookup_attribute_reference: MIAttributeReference
    ) -> "_FinalRecordReferenceBuilder":
        self._build.lookup_value = lookup_value
        self._build.lookup_attribute_reference = lookup_attribute_reference
        return _FinalRecordReferenceBuilder(self)


class _FinalRecordReferenceBuilder:
    _source: "RecordReferenceBuilder"

    def __init__(self, source: "RecordReferenceBuilder") -> None:
        self._source = source

    def build(self) -> "MIRecordReference":
        return self._source._build
