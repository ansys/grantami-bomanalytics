from typing import Optional
import uuid

import pytest

from ansys.grantami.bomanalytics.bom_types import (
    AttributeReferenceBuilder,
    PseudoAttribute,
    RecordReferenceBuilder,
)


class TestAttributeReferenceBuilder:
    _DB_KEY = "TEST_DB_KEY"
    _ATTRIBUTE_ID = 13
    _ATTRIBUTE_NAME = "Test Attribute"
    _TABLE_ID = 23
    _TABLE_GUID = "219267ba-2c04-4f40-9beb-a9d02af77c2f"
    _TABLE_NAME = "Test Table"

    def test_by_id(self):
        attribute_reference = (
            AttributeReferenceBuilder(db_key=self._DB_KEY)
            .with_attribute_identity(attribute_identity=self._ATTRIBUTE_ID)
            .build()
        )
        assert attribute_reference.db_key == self._DB_KEY
        assert attribute_reference.attribute_identity == self._ATTRIBUTE_ID
        assert attribute_reference.table_reference is None
        assert attribute_reference.attribute_name is None
        assert attribute_reference.pseudo is None

    @pytest.mark.parametrize("is_standard", [True, False])
    def test_by_name_and_table_id(self, is_standard: bool):
        attribute_reference = (
            AttributeReferenceBuilder(db_key=self._DB_KEY)
            .with_attribute_name(attribute_name=self._ATTRIBUTE_NAME, is_standard_name=is_standard)
            .with_table_identity(table_identity=self._TABLE_ID)
            .build()
        )
        assert attribute_reference.db_key == self._DB_KEY
        assert attribute_reference.attribute_identity is None
        assert attribute_reference.table_reference is not None
        assert attribute_reference.table_reference.table_name is None
        assert attribute_reference.table_reference.table_guid is None
        assert attribute_reference.table_reference.table_identity == self._TABLE_ID
        assert attribute_reference.attribute_name == self._ATTRIBUTE_NAME
        assert attribute_reference.is_standard == is_standard
        assert attribute_reference.pseudo is None

    @pytest.mark.parametrize("is_standard", [True, False])
    def test_by_name_and_table_gud(self, is_standard: bool):
        attribute_reference = (
            AttributeReferenceBuilder(db_key=self._DB_KEY)
            .with_attribute_name(attribute_name=self._ATTRIBUTE_NAME, is_standard_name=is_standard)
            .with_table_guid(table_guid=self._TABLE_GUID)
            .build()
        )
        assert attribute_reference.db_key == self._DB_KEY
        assert attribute_reference.attribute_identity is None
        assert attribute_reference.table_reference is not None
        assert attribute_reference.table_reference.table_name is None
        assert attribute_reference.table_reference.table_guid == self._TABLE_GUID
        assert attribute_reference.table_reference.table_identity is None
        assert attribute_reference.attribute_name == self._ATTRIBUTE_NAME
        assert attribute_reference.is_standard == is_standard
        assert attribute_reference.pseudo is None

    @pytest.mark.parametrize("is_standard", [True, False])
    def test_by_name_and_table_name(self, is_standard: bool):
        attribute_reference = (
            AttributeReferenceBuilder(db_key=self._DB_KEY)
            .with_attribute_name(attribute_name=self._ATTRIBUTE_NAME, is_standard_name=is_standard)
            .with_table_name(table_name=self._TABLE_NAME)
            .build()
        )
        assert attribute_reference.db_key == self._DB_KEY
        assert attribute_reference.attribute_identity is None
        assert attribute_reference.table_reference is not None
        assert attribute_reference.table_reference.table_name == self._TABLE_NAME
        assert attribute_reference.table_reference.table_guid is None
        assert attribute_reference.table_reference.table_identity is None
        assert attribute_reference.attribute_name == self._ATTRIBUTE_NAME
        assert attribute_reference.is_standard == is_standard
        assert attribute_reference.pseudo is None

    @pytest.mark.parametrize("pseudo_id", range(0, 16))
    def test_by_pseudo(self, pseudo_id: int):
        pseudo = PseudoAttribute(pseudo_id)
        attribute_reference = AttributeReferenceBuilder(db_key=self._DB_KEY).as_pseudo_attribute(pseudo).build()
        assert attribute_reference.db_key == self._DB_KEY
        assert attribute_reference.attribute_identity is None
        assert attribute_reference.attribute_name is None
        assert attribute_reference.table_reference is None
        assert attribute_reference.pseudo == pseudo


class TestRecordReferenceBuilder:
    _DB_KEY = "TEST_DB_KEY"
    _LOOKUP_ATTRIBUTE_ID = 23
    _LOOKUP_ATTRIBUTE_REF = (
        AttributeReferenceBuilder(db_key=_DB_KEY)
        .with_attribute_identity(attribute_identity=_LOOKUP_ATTRIBUTE_ID)
        .build()
    )
    _LOOKUP_VALUE = "RECORD 1"
    _TABLE_ID = 23
    _TABLE_GUID = "219267ba-2c04-4f40-9beb-a9d02af77c2f"
    _TABLE_NAME = "Test Table"
    _RECORD_GUID = "5cfd6f47-a9f1-49ac-b65e-27b4e115e5f6"
    _RECORD_HISTORY_GUID = "1743b0d3-4784-472f-b199-ead0931eb1ca"
    _RECORD_ID = 1412
    _RECORD_HISTORY_ID = 248976

    @pytest.mark.parametrize("version_number", [None, 1, 19])
    @pytest.mark.parametrize("uid", [None, "a", str(uuid.uuid4())])
    def test_by_record_history_id(self, version_number: Optional[int], uid: Optional[str]):
        record_reference = (
            RecordReferenceBuilder(db_key=self._DB_KEY, record_uid=uid)
            .with_record_history_id(record_history_id=self._RECORD_HISTORY_ID, record_version_number=version_number)
            .build()
        )
        assert record_reference.db_key == self._DB_KEY
        assert record_reference.record_uid == uid
        assert record_reference.record_history_identity == self._RECORD_HISTORY_ID
        assert record_reference.record_version_number == version_number
        assert record_reference.record_guid is None
        assert record_reference.record_history_guid is None
        assert record_reference.lookup_attribute_reference is None
        assert record_reference.lookup_value is None

    @pytest.mark.parametrize("uid", [None, "a", str(uuid.uuid4())])
    def test_by_record_history_guid(self, uid: Optional[str]):
        record_reference = (
            RecordReferenceBuilder(db_key=self._DB_KEY, record_uid=uid)
            .with_record_history_guid(record_history_guid=self._RECORD_HISTORY_GUID)
            .build()
        )
        assert record_reference.db_key == self._DB_KEY
        assert record_reference.record_uid == uid
        assert record_reference.record_history_identity is None
        assert record_reference.record_version_number is None
        assert record_reference.record_guid is None
        assert record_reference.record_history_guid == self._RECORD_HISTORY_GUID
        assert record_reference.lookup_attribute_reference is None
        assert record_reference.lookup_value is None

    @pytest.mark.parametrize("uid", [None, "a", str(uuid.uuid4())])
    def test_by_record_guid(self, uid: Optional[str]):
        record_reference = (
            RecordReferenceBuilder(db_key=self._DB_KEY, record_uid=uid)
            .with_record_guid(record_guid=self._RECORD_GUID)
            .build()
        )
        assert record_reference.db_key == self._DB_KEY
        assert record_reference.record_uid == uid
        assert record_reference.record_history_identity is None
        assert record_reference.record_version_number is None
        assert record_reference.record_guid == self._RECORD_GUID
        assert record_reference.record_history_guid is None
        assert record_reference.lookup_attribute_reference is None
        assert record_reference.lookup_value is None

    @pytest.mark.parametrize("uid", [None, "a", str(uuid.uuid4())])
    def test_by_lookup_value(self, uid: Optional[str]):
        record_reference = (
            RecordReferenceBuilder(db_key=self._DB_KEY, record_uid=uid)
            .with_lookup_value(lookup_value=self._LOOKUP_VALUE, lookup_attribute_reference=self._LOOKUP_ATTRIBUTE_REF)
            .build()
        )
        assert record_reference.db_key == self._DB_KEY
        assert record_reference.record_uid == uid
        assert record_reference.record_history_identity is None
        assert record_reference.record_version_number is None
        assert record_reference.record_guid is None
        assert record_reference.record_history_guid is None
        assert record_reference.lookup_attribute_reference is not None
        assert record_reference.lookup_attribute_reference.db_key == self._DB_KEY
        assert record_reference.lookup_attribute_reference.attribute_identity == self._LOOKUP_ATTRIBUTE_ID
        assert record_reference.lookup_value == self._LOOKUP_VALUE
