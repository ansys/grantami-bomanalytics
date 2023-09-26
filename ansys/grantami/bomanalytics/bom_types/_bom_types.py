from __future__ import annotations

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
    cast,
)

if TYPE_CHECKING:
    from ._bom_reader import BoMReader
    from ._bom_writer import BoMWriter


class HasNamespace(Protocol):
    _namespace: str


class SupportsCustomFields(Protocol):
    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        ...

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        ...


class BaseType(HasNamespace, SupportsCustomFields):
    """Base type from which all XML DTOs inherit.

    Handles conversion from python properties to xmlschema objects.

    Attributes
    ----------
    _props : List[Tuple[str, str, str]]
        Properties that map to complex types in XML. The entries are the type target, the python attribute name
        and the XML element name.
    _list_props : List[Tuple[str, str, str, str]]
        Properties that map to sequences of complex types in XML. The entries are the type target for each entry, the
        python property name, the container XML element name, and the item XML element name.
    _simple_values : List[Tuple[str, str]]
        Properties that map to simple types in XML. The entries are the python property name and the item XML element
        name.
    _namespaces : Dict[str, str]
        Mapping from XML namespace prefix to namespace URI.
    _namespace : str
        XML Namespace URI for the object, should exist as a value in the ``_namespaces`` map.
    """

    _props: List[Tuple[str, str, str]] = []
    _list_props: List[Tuple[str, str, str, str, str]] = []
    _simple_values: List[Tuple[str, str]] = []

    _namespaces: Dict[str, str] = {}

    _namespace = "http://www.grantadesign.com/23/01/BillOfMaterialsEco"

    def __init__(self, *args: Iterable, **kwargs: Dict[str, Any]) -> None:
        pass

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        """
        Populates any fields on the object that are in a nonstandard configuration. This can anonymous complex types,
        Sequences of simple types and similar. This is called after the standard deserialization occurs, and should
        return a dictionary mapping constructor argument names to values.

        Parameters
        ----------
        obj: Dict
            The json representation of the source XML BoM to be parsed.
        bom_reader: BoMReader
            Helper object that maintains information about the global namespaces.

        Returns
        -------
        Dict[str, Any]
            Dictionary mapping constructor argument names to values for this type.
        """
        return {}

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        """
        Writes any fields on the serialized object that are in a nonstandard configuration. This can be anonymous
        complex types, Sequences of simple types and similar. This is called after the standard serialization occurs,
        and should modify the ``obj`` argument in place.

        Parameters
        ----------
        obj: Dict
            Dictionary representing the current state of the serialization of self. Modified in place by this method.
        bom_writer: BoMWriter
            Helper object that maintains information about the global namespaces.
        """
        pass


class DimensionType(Enum):
    Mass = 0  # If the process affects the bulk of the material or part (e.g. it is a shaping process) then
    # the amount of material affected by the process should be specified. The amount may be
    # specified as a percentage by weight or an absolute value.
    MassRemoved = 1  # Specifying the mass in this way allows one to specify processes that may have removed material
    # (e.g. milling or turning).
    Volume = 2
    Area = 3  # Some joining processes can have an associated area.
    Length = 4  # If the process is an edge joining process (e.g. welding) then the BOM must specify the length
    # of material affected by the process.
    Count = 5  # Certain fastening processes are quantified by the number of fasteners (e.g. the number of hot
    # rivets holding two plates together).
    Time = 6

    @classmethod
    def from_string(cls, value: str) -> DimensionType:
        """
        Convert string representation of this object into an instance of this object.

        Parameters
        ----------
        value: str
            String representation of this object.
        """
        return DimensionType[value]

    def to_string(self) -> str:
        """
        Convert this Enum object to its string representation.

        Returns
        -------
        str
            String representation of this object.
        """
        return self.name


class PseudoAttribute(Enum):
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


class PartialTableReference(BaseType):
    _simple_values = [("table_identity", "tableIdentity"), ("table_guid", "tableGuid"), ("table_name", "tableName")]

    _namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

    def __init__(
        self,
        *,
        table_identity: Optional[int] = None,
        table_guid: Optional[str] = None,
        table_name: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        """
        A type that partially identifies a Table, but does not specify the MI Database. Usually, just one of the several
        optional fields should be provided; where more than one is provided, the highest priority one is used, where the
        descending priority order is: tableIdentity, tableGUID, tableName.

        Parameters
        ----------
        table_identity: Optional[int]
            The identity of the table, this is the fastest way to reference a table.
        table_guid: Optional[str]
            The GUID of the table, this is likely to be a persistent way to refer to a table.
        table_name: Optional[str]
            The name of the table, note that table names can vary between localisations of a database, so this may not
            be a safe way to refer to a table if the MI Database supports multiple locales.
        """
        super().__init__(**kwargs)
        self.table_identity = table_identity
        self.table_guid = table_guid
        self.table_name = table_name

    @property
    def table_identity(self) -> Optional[int]:
        """
        The identity of the table, this is the fastest way to reference a table.

        Returns
        -------
        Optional[int]
        """
        return self._table_identity

    @table_identity.setter
    def table_identity(self, value: Optional[int]) -> None:
        self._table_identity = value

    @property
    def table_guid(self) -> Optional[str]:
        """
        The GUID of the table, this is likely to be a persistent way to refer to a table.

        Returns
        -------
        Optional[str]
        """
        return self._table_guid

    @table_guid.setter
    def table_guid(self, value: Optional[str]) -> None:
        self._table_guid = value

    @property
    def table_name(self) -> Optional[str]:
        """
        The name of the table, note that table names can vary between localisations of a database, so this may not be a
        safe way to refer to a table if the MI Database supports multiple locales.

        Returns
        -------
        Optional[str]
        """
        return self._table_name

    @table_name.setter
    def table_name(self, value: Optional[str]) -> None:
        self._table_name = value


class MIAttributeReference(BaseType):
    _simple_values = [("db_key", "dbKey"), ("attribute_identity", "attributeIdentity")]

    _namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

    def __init__(
        self,
        *,
        db_key: str,
        attribute_identity: Optional[int] = None,
        table_reference: Optional[PartialTableReference] = None,
        attribute_name: Optional[str] = None,
        pseudo: Optional[PseudoAttribute] = None,
        is_standard: Optional[bool] = None,
        **kwargs: Dict[str, Any],
    ):
        """A type that allows identification of a particular Attribute in an MI Database. This may be done directly by
        specifying the Identity of the Attribute, or indirectly by specifying a lookup that will match (only) the
        Attribute.

        Note: in certain cases, an MIAttributeReference may match more than one Attribute in
        the MI Database; depending on the operation, this may be legal or may result in
        a Fault.

        Parameters
        ----------
        db_key: str
            The key that uniquely identifies a particular Database on the MI Server.
        attribute_identity: Optional[int]
            The identity of the attribute within the MI Database.
        table_reference: Optional[PartialTableReference]
            A reference to the table hosting the attribute. Required if ``attribute_name`` is specified and
            ``is_standard`` is not True.
        attribute_name: Optional[str]
            Name of the Attribute.
        pseudo: Optional[PseudoAttribute]
            The pseudo-attribute type if referring to a pseudo-attribute.
        is_standard: Optional[bool]
            If True indicates that the provided ``attribute_name`` is a Standard Name.
        """
        super().__init__(**kwargs)
        self.db_key = db_key
        self.attribute_identity = attribute_identity
        self.table_reference = table_reference
        self.attribute_name = attribute_name
        self.pseudo = pseudo
        self.is_standard = is_standard

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        name_obj = bom_reader.get_field(MIAttributeReference, obj, "name")
        if name_obj is not None:
            props["table_reference"] = cast(
                PartialTableReference, bom_reader.create_type("PartialTableReference", name_obj)
            )
            attribute_name_obj = bom_reader.get_field(MIAttributeReference, name_obj, "attributeName")
            if attribute_name_obj is not None:
                props["attribute_name"] = attribute_name_obj
            pseudo_obj = bom_reader.get_field(MIAttributeReference, name_obj, "pseudo")
            if pseudo_obj is not None:
                props["pseudo"] = pseudo_obj
            is_standard_obj = bom_reader.get_field(MIAttributeReference, name_obj, "@isStandard")
            if is_standard_obj is not None:
                props["is_standard"] = is_standard_obj
        return props

    @property
    def db_key(self) -> str:
        """
        The key that uniquely identifies a particular Database on the MI Server.

        Returns
        -------
        str
        """
        return self._db_key

    @db_key.setter
    def db_key(self, value: str) -> None:
        self._db_key = value

    @property
    def attribute_identity(self) -> Optional[int]:
        """
        The identity of the attribute within the MI Database.

        Returns
        -------
        Optional[int]
        """
        return self._attribute_identity

    @attribute_identity.setter
    def attribute_identity(self, value: Optional[int]) -> None:
        self._attribute_identity = value

    @property
    def table_reference(self) -> Optional[PartialTableReference]:
        """
        A reference to the table hosting the attribute. Required if ``attribute_name`` is specified and ``is_standard``
        is not True.

        Returns
        -------
        Optional[PartialTableReference]
        """
        return self._table_reference

    @table_reference.setter
    def table_reference(self, value: Optional[PartialTableReference]) -> None:
        self._table_reference = value

    @property
    def attribute_name(self) -> Optional[str]:
        """
        Name of the Attribute.

        Returns
        -------
        str
        """
        return self._attribute_name

    @attribute_name.setter
    def attribute_name(self, value: Optional[str]) -> None:
        self._attribute_name = value

    @property
    def pseudo(self) -> Optional[PseudoAttribute]:
        """
        The pseudo-attribute type if referring to a pseudo-attribute.

        Returns
        -------
        Optional[PseudoAttribute]
        """
        return self._pseudo

    @pseudo.setter
    def pseudo(self, value: Optional[PseudoAttribute]) -> None:
        self._pseudo = value

    @property
    def is_standard(self) -> Optional[bool]:
        """
        If True indicates that the provided ``attribute_name`` is a Standard Name.

        Returns
        -------
        Optional[bool]
        """
        return self._is_standard

    @is_standard.setter
    def is_standard(self, value: Optional[bool]) -> None:
        self._is_standard = value


class MIRecordReference(BaseType):
    _simple_values = [
        ("db_key", "dbKey"),
        ("record_guid", "recordGUID"),
        ("record_history_guid", "recordHistoryGUID"),
        ("record_uid", "@recordUID"),
    ]

    _namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

    def __init__(
        self,
        *,
        db_key: str,
        record_history_identity: Optional[int] = None,
        record_version_number: Optional[int] = None,
        record_guid: Optional[str] = None,
        record_history_guid: Optional[str] = None,
        lookup_attribute_reference: Optional[MIAttributeReference] = None,
        lookup_value: Optional[str] = None,
        record_uid: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        """A type that allows identification of a particular Record in an
        MI Database. This may be done directly by specifying the Identity or GUID of the Record, or
        indirectly by specifying a lookup that will match (only) the Record.

        For input, you should provide exactly one of either identity, recordGUID, recordHistoryGUID
        or lookupValue. If more than one element identifying the record is given, only one is used; the descending
        order of priority is: identity, recordGUID, recordHistoryGUID, lookupValue. The Service Layer does not
        check that the several elements identifying the record are all referencing the same record, it just picks the
        highest-priority one and uses that.

        Parameters
        ----------
        db_key: str
            The key that uniquely identifies a particular Database on the MI Server.
        record_history_identity: Optional[int]
            This is the best-performing and highest-priority way to reference a record; however, identities might not
            be suitable for long-term persistence.
        record_version_number: Optional[int]
            If omitted, this means the latest version visible to the user.
        record_guid: Optional[str]
            Identifies a particular version of a record by its GUID, this is a more persistent way to refer to a record.
        record_history_guid: Optional[str]
            Identifies a record history, the latest visible version will be returned. ``record_version_number`` has no
            effect on references that use ``record_history_guid``.
        lookup_attribute_reference: Optional[MIAttributeReference]
            When provided in combination with ``lookup_value`` identifies a record by a unique short-text attribute.
            Specifies the attribute to be used for the lookup operation.
        lookup_value: Optional[str]
            When provided in combination with ``lookup_attribute_reference`` identifies a record by a unique short-text
            attribute. Specifies the value to be used for the lookup operation. If this is not unique an error will be
            returned.
        record_uid: Optional[str]
            The recordUID may be used to identify a particular XML element representing a record. It does not represent
            any property or attribute of an actual MI Record.
        """
        super().__init__(**kwargs)
        self.db_key = db_key
        self.record_history_identity = record_history_identity
        self.record_version_number = record_version_number
        self.record_guid = record_guid
        self.record_history_guid = record_history_guid
        self.lookup_attribute_reference = lookup_attribute_reference
        self.lookup_value = lookup_value
        self.record_uid = record_uid

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
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
            props["lookup_attribute_reference"] = bom_reader.get_field(
                MIRecordReference, lookup_obj, "attributeReference"
            )
            props["lookup_value"] = bom_reader.get_field(MIRecordReference, lookup_obj, "attributeValue")
        return props

    @property
    def db_key(self) -> str:
        """
        Identifies the database to which this record belongs.

        Returns
        -------
        str
        """
        return self._db_key

    @db_key.setter
    def db_key(self, value: str) -> None:
        self._db_key = value

    @property
    def record_history_identity(self) -> Optional[int]:
        """
        Identifies a record by its history identity.

        Returns
        -------
        Optional[int]
        """
        return self._record_history_identity

    @record_history_identity.setter
    def record_history_identity(self, value: Optional[int]) -> None:
        self._record_history_identity = value

    @property
    def record_version_number(self) -> Optional[int]:
        """
        If ``record_history_identity`` is provided, identifies a specific version of that record history.

        Returns
        -------
        Optional[int]
        """
        return self._record_version_number

    @record_version_number.setter
    def record_version_number(self, value: Optional[int]) -> None:
        self._record_version_number = value

    @property
    def record_guid(self) -> Optional[str]:
        """
        Identifies a record by its GUID, gets a specific version.

        Returns
        -------
        Optional[str]
        """
        return self._record_guid

    @record_guid.setter
    def record_guid(self, value: Optional[str]) -> None:
        self._record_guid = value

    @property
    def record_history_guid(self) -> Optional[str]:
        """
        Identifies a record by its history GUID, returns the latest released version of the record the user can see.

        Returns
        -------
        Optional[str]
        """
        return self._record_history_guid

    @record_history_guid.setter
    def record_history_guid(self, value: Optional[str]) -> None:
        self._record_history_guid = value

    @property
    def lookup_attribute_reference(self) -> Optional[MIAttributeReference]:
        """
        Identifies a record by a short-text attribute value. Specifies which attribute should be used to perform this
        lookup. This should be either a Short-Text Attribute, or a compatible Pseudo-Attribute.

        Returns
        -------
        Optional[MIAttributeReference]
        """
        return self._lookup_attribute_reference

    @lookup_attribute_reference.setter
    def lookup_attribute_reference(self, value: Optional[MIAttributeReference]) -> None:
        self._lookup_attribute_reference = value

    @property
    def lookup_value(self) -> Optional[str]:
        """
        Identifies a record by a short-text attribute value. Specifies the value of the attribute should be used to
        perform this lookup.

        Returns
        -------
        Optional[str]
        """
        return self._lookup_value

    @lookup_value.setter
    def lookup_value(self, value: Optional[str]) -> None:
        self._lookup_value = value

    @property
    def record_uid(self) -> Optional[str]:
        """
        Identifies a record with an additional identifier, this is not used by the database, but will be returned
        in any response unchanged. Used to correlate requests with responses from the server.

        Returns
        -------
        Optional[str]
        """
        return self._record_uid

    @record_uid.setter
    def record_uid(self, value: Optional[str]) -> None:
        self._record_uid = value


# TODO - I don't like having a nice method to add props then replicating it here, can we do something better with
#  inheritance?
class InternalIdentifierMixin(SupportsCustomFields):
    def __init__(self, *, internal_id: Optional[str] = None, **kwargs: Dict[str, Any]):
        """A unique identity for this object in this BoM. This identity is only for internal use, allowing other
        elements to reference this element.

        Parameters
        ----------
        internal_id: Optional[str]
            The identifier to assign to this object.
        """
        super().__init__(**kwargs)
        self.internal_id = internal_id

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        instance = cast(Type[BaseType], cls)
        id_obj = bom_reader.get_field(instance, obj, "@id")
        if id_obj is not None:
            props["internal_id"] = id_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)
        if self._internal_id is not None:
            instance = cast(BaseType, self)
            field_name = bom_writer._get_qualified_name(instance, "@id")
            obj[field_name] = self._internal_id

    @property
    def internal_id(self) -> Optional[str]:
        """
        Internal identity used to refer to this object in references.

        Returns
        -------
        str
        """
        return self._internal_id

    @internal_id.setter
    def internal_id(self, value: Optional[str]) -> None:
        self._internal_id = value


class CommonIdentifiersMixin(SupportsCustomFields):
    def __init__(
        self,
        *,
        identity: Optional[str] = None,
        name: Optional[str] = None,
        external_identity: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        """
        A set of identifiers used by external applications to reference and display parts of the BoM.

        Parameters
        ----------
        identity: Optional[str]
            A display identity for the object.
        name: Optional[str]
            A display name for the object.
        external_identity: Optional[str]
            A temporary reference populated and used by applications to refer to the item within the BoM.
        """
        super().__init__(**kwargs)
        self.identity = identity
        self.name = name
        self.external_identity = external_identity

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)
        instance = cast(BaseType, self)
        if self._identity is not None:
            field_name = bom_writer._get_qualified_name(instance, "Identity")
            obj[field_name] = self._identity
        if self._name is not None:
            field_name = bom_writer._get_qualified_name(instance, "Name")
            obj[field_name] = self._name
        if self._external_identity is not None:
            field_name = bom_writer._get_qualified_name(instance, "ExternalIdentity")
            obj[field_name] = self._external_identity

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        instance = cast(Type[BaseType], cls)
        identity_obj = bom_reader.get_field(instance, obj, "Identity")
        if identity_obj is not None:
            props["identity"] = identity_obj
        name_obj = bom_reader.get_field(instance, obj, "Name")
        if name_obj is not None:
            props["name"] = name_obj
        external_identity_obj = bom_reader.get_field(instance, obj, "ExternalIdentity")
        if external_identity_obj is not None:
            props["external_identity"] = external_identity_obj
        return props

    @property
    def identity(self) -> Optional[str]:
        """
        A display identity for this object.

        Returns
        -------
        Optional[str]
        """
        return self._identity

    @identity.setter
    def identity(self, value: Optional[str]) -> None:
        self._identity = value

    @property
    def name(self) -> Optional[str]:
        """
        A display name for this object.

        Returns
        -------
        Optional[str]
        """
        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        self._name = value

    @property
    def external_identity(self) -> Optional[str]:
        """
        A temporary reference populated and used by applications to refer to this object within the BoM.

        Returns
        -------
        Optional[str]
        """
        return self._external_identity

    @external_identity.setter
    def external_identity(self, value: Optional[str]) -> None:
        self._external_identity = value


class EndOfLifeFate(BaseType):
    _simple_values = [("fraction", "Fraction")]

    _props = [("MIRecordReference", "mi_end_of_life_reference", "MIEndOfLifeReference")]

    def __init__(
        self, *, mi_end_of_life_reference: MIRecordReference, fraction: float, **kwargs: Dict[str, Any]
    ) -> None:
        """
        The fate of a material at the end-of-life of the product. For example if a material can be recycled, and what
        fraction of the total mass or volume can be recycled.

        Parameters
        ----------
        mi_end_of_life_reference : MIRecordReference
            Reference identifying the applicable fate within the MI Database.
        fraction : float
            Fraction of the total mass or volume of material to which this fate applies.
        """
        super().__init__(**kwargs)
        self.mi_end_of_life_reference = mi_end_of_life_reference
        self.fraction = fraction

    @property
    def mi_end_of_life_reference(self) -> MIRecordReference:
        """
        Reference identifying the applicable fate within the MI Database.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_end_of_life_reference

    @mi_end_of_life_reference.setter
    def mi_end_of_life_reference(self, value: MIRecordReference) -> None:
        self._mi_end_of_life_reference = value

    @property
    def fraction(self) -> float:
        """
        Fraction of the total mass or volume of material to which this fate applies.

        Returns
        -------
        float
        """
        return self._fraction

    @fraction.setter
    def fraction(self, value: float) -> None:
        self._fraction = value


class UnittedValue(BaseType):
    _simple_values = [("value", "$"), ("unit", "@Unit")]

    def __init__(self, *, value: float, unit: Optional[str] = None, **kwargs: Dict[str, Any]) -> None:
        """
        A physical quantity with a unit. If provided in a input then the unit should exist within the MI database,
        otherwise an error will be raised.

        Parameters
        ----------
        value: float
            The value of the quantity in specified units.
        unit: Optional[str]
            If provided, specifies the unit symbol applying to the quantity. If absent the quantity will be treated as
            dimensionless.
        """
        super().__init__(**kwargs)
        self.value = value
        self.unit = unit

    def __repr__(self) -> str:
        if self._unit is None:
            return f"<UnittedValue: {self._value}>"
        else:
            return f"<UnittedValue: {self._value} {self._unit}>"

    @property
    def value(self) -> float:
        """
        The value of the quantity in the provided unit.

        Returns
        -------
        float
        """
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    @property
    def unit(self) -> Optional[str]:
        """
        The unit symbol applying to the quantity.

        Returns
        -------
        Optional[str]
        """
        return self._unit

    @unit.setter
    def unit(self, value: Optional[str]) -> None:
        self._unit = value


class Location(CommonIdentifiersMixin, InternalIdentifierMixin, BaseType):
    _props = [("MIRecordReference", "mi_location_reference", "MILocationReference")]

    def __init__(self, *, mi_location_reference: Optional[MIRecordReference] = None, **kwargs: Any) -> None:
        """
        Defines the manufacturing location for the BoM for use in process calculations.

        Parameters
        ----------
        mi_location_reference: Optional[MIRecordReference]
            Reference to a record in the MI database representing the manufacturing location.
        """
        super().__init__(**kwargs)
        self.mi_location_reference = mi_location_reference

    @property
    def mi_location_reference(self) -> Optional[MIRecordReference]:
        """
        Reference to a record in the MI database representing the manufacturing location.

        Returns
        -------
        Optional[MIRecordReference]
        """
        return self._mi_location_reference

    @mi_location_reference.setter
    def mi_location_reference(self, value: Optional[MIRecordReference]) -> None:
        self._mi_location_reference = value


class ElectricityMix(BaseType):
    _props = [("MIRecordReference", "mi_region_reference", "MIRegionReference")]
    _simple_values = [("percentage_fossil_fuels", "PercentageFossilFuels")]

    def __init__(
        self,
        *,
        mi_region_reference: Optional[MIRecordReference] = None,
        percentage_fossil_fuels: Optional[float] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        If the product consumes electrical power, then the amount of CO2 produced to generate depends upon the mix of
        fossil fuel burning power stations in the region of use.  This type lets you specify the electrical generation
        mix by either specifying the region or country of use or by specifying the percentage of power that comes from
        fossil fuel sources.

        Parameters
        ----------
        mi_region_reference: Optional[MIRecordReference]
            Reference to a record in the MI database representing the electricity mix for the destination country.
        percentage_fossil_fuels: Optional[float]
            The percentage of electrical power production within the destination country that comes from fossil fuels.
        """
        super().__init__(**kwargs)
        self.mi_region_reference = mi_region_reference
        self.percentage_fossil_fuels = percentage_fossil_fuels

    @property
    def mi_region_reference(self) -> Optional[MIRecordReference]:
        """
        Reference to a record in the MI database representing the electricity mix for the destination country.

        Returns
        -------
        Optional[MIRecordReference]
        """
        return self._mi_region_reference

    @mi_region_reference.setter
    def mi_region_reference(self, value: Optional[MIRecordReference]) -> None:
        self._mi_region_reference = value

    @property
    def percentage_fossil_fuels(self) -> Optional[float]:
        """
        The percentage of electrical power production within the destination country that comes from fossil fuels.

        Returns
        -------
        Optional[float]
        """
        return self._percentage_fossil_fuels

    @percentage_fossil_fuels.setter
    def percentage_fossil_fuels(self, value: Optional[float]) -> None:
        self._percentage_fossil_fuels = value


class MobileMode(BaseType):
    _props = [
        ("MIRecordReference", "mi_transport_reference", "MITransportReference"),
        ("UnittedValue", "distance_travelled_per_day", "DistanceTravelledPerDay"),
    ]
    _simple_values = [("days_user_per_year", "DaysUsedPerYear")]

    def __init__(
        self,
        *,
        mi_transport_reference: MIRecordReference,
        days_used_per_year: float,
        distance_travelled_per_day: UnittedValue,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        If the product is transported as part of its use then this type contains details about the way in which it is
        transported.

        Parameters
        ----------
        mi_transport_reference: MIRecordReference
            Reference to a record in the MI database representing the means of transport for this product during use.
        days_used_per_year: float
            The number of days in a year the product will be transported during use.
        distance_travelled_per_day: UnittedValue
            The distance the product will be transported each day as part of its use.
        """
        super().__init__(**kwargs)
        self.mi_transport_reference = mi_transport_reference
        self.days_used_per_year = days_used_per_year
        self.distance_travelled_per_day = distance_travelled_per_day

    @property
    def mi_transport_reference(self) -> MIRecordReference:
        """
        Reference to a record in the MI database representing the means of transport for this product during use.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_transport_reference

    @mi_transport_reference.setter
    def mi_transport_reference(self, value: MIRecordReference) -> None:
        self._mi_transport_reference = value

    @property
    def days_used_per_year(self) -> float:
        """
        The number of days in a year the product will be transported during use.

        Returns
        -------
        float
        """
        return self._days_used_per_year

    @days_used_per_year.setter
    def days_used_per_year(self, value: float) -> None:
        self._days_used_per_year = value

    @property
    def distance_travelled_per_day(self) -> UnittedValue:
        """
        The distance the product will be transported each day as part of its use.

        Returns
        -------
        UnittedValue
        """
        return self._distance_travelled_per_day

    @distance_travelled_per_day.setter
    def distance_travelled_per_day(self, value: UnittedValue) -> None:
        self._distance_travelled_per_day = value


class StaticMode(BaseType):
    _props = [
        ("MIRecordReference", "mi_energy_conversion_reference", "MIEnergyConversionReference"),
        ("UnittedValue", "power_rating", "PowerRating"),
    ]
    _simple_values = [("days_used_per_year", "DaysUsedPerYear"), ("hours_used_per_day", "HoursUsedPerDay")]

    def __init__(
        self,
        *,
        mi_energy_conversion_reference: MIRecordReference,
        power_rating: UnittedValue,
        days_used_per_year: float,
        hours_used_per_day: float,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        Specifies the primary energy conversion that occurs during the product's use.

        Parameters
        ----------
        mi_energy_conversion_reference: MIRecordReference
            Reference to a record in the MI database representing the primary energy conversion taking place when the
            product is in use.
        power_rating: UnittedValue
            The power rating of the product whilst in use.
        days_used_per_year: float
            The number of days per year that the product will be used.
        hours_used_per_day: float
            The number of hours per day of use that the product will be used.
        """
        super().__init__(**kwargs)
        self.mi_energy_conversion_reference = mi_energy_conversion_reference
        self.power_rating = power_rating
        self.days_used_per_year = days_used_per_year
        self.hours_used_per_day = hours_used_per_day

    @property
    def mi_energy_conversion_reference(self) -> MIRecordReference:
        """
        Reference to a record in the MI database representing the primary energy conversion taking place when the
        product is in use.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_energy_conversion_reference

    @mi_energy_conversion_reference.setter
    def mi_energy_conversion_reference(self, value: MIRecordReference) -> None:
        self._mi_energy_conversion_reference = value

    @property
    def power_rating(self) -> UnittedValue:
        """
        The power rating of the product whilst in use.

        Returns
        -------
        UnittedValue
        """
        return self._power_rating

    @power_rating.setter
    def power_rating(self, value: UnittedValue) -> None:
        self._power_rating = value

    @property
    def days_used_per_year(self) -> float:
        """
        The number of days per year that the product will be used.

        Returns
        -------
        float
        """
        return self._days_used_per_year

    @days_used_per_year.setter
    def days_used_per_year(self, value: float) -> None:
        self._days_used_per_year = value

    @property
    def hours_used_per_day(self) -> float:
        """
        The number of hours per day of use that the product will be used.

        Returns
        -------
        float
        """
        return self._hours_used_per_day

    @hours_used_per_day.setter
    def hours_used_per_day(self, value: float) -> None:
        self._hours_used_per_day = value


class UtilitySpecification(BaseType):
    _simple_values = [
        ("industry_average_duration_years", "IndustryAverageDurationYears"),
        ("industry_average_number_of_functional_units", "IndustryAverageNumberOfFunctionalUnits"),
        ("utility", "Utility"),
    ]

    def __init__(
        self,
        *,
        industry_average_duration_years: Optional[float] = None,
        industry_average_number_of_functional_units: Optional[float] = None,
        utility: Optional[float] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        Specifies how much use can be obtained from the product represented by this BoM in comparison to a
        representative industry average.

        Parameters
        ----------
        industry_average_duration_years: Optional[float]
            The average lifespan of all examples, throughout the industry, of the kind of product described herein.
        industry_average_number_of_functional_units: Optional[float]
            The average number of functional units delivered, in their lifespan, by all examples, throughout the
            industry, of the kind of product represented by this object.
        utility: Optional[float]
            Directly specifies the utility.
        """
        super().__init__(**kwargs)
        self.industry_average_duration_years = industry_average_duration_years
        self.industry_average_number_of_functional_units = industry_average_number_of_functional_units
        self.utility = utility

    @property
    def industry_average_duration_years(self) -> Optional[float]:
        """
        The average lifespan of all examples, throughout the industry, of the kind of product described herein.

        Returns
        -------
        Optional[float]
        """
        return self._industry_average_duration_years

    @industry_average_duration_years.setter
    def industry_average_duration_years(self, value: Optional[float]) -> None:
        self._industry_average_duration_years = value

    @property
    def industry_average_number_of_functional_units(self) -> Optional[float]:
        """
        The average number of functional units delivered, in their lifespan, by all examples, throughout the industry,
        of the kind of product represented by this object.

        Returns
        -------
        Optional[float]
        """
        return self._industry_average_number_of_functional_units

    @industry_average_number_of_functional_units.setter
    def industry_average_number_of_functional_units(self, value: Optional[float]) -> None:
        self._industry_average_number_of_functional_units = value

    @property
    def utility(self) -> Optional[float]:
        """
        Directly specifies the utility.

        Returns
        -------
        float
        """
        return self._utility

    @utility.setter
    def utility(self, value: Optional[float]) -> None:
        self._utility = value


class ProductLifeSpan(BaseType):
    _props = [("UtilitySpecification", "utility", "Utility")]
    _simple_values = [
        ("duration_years", "DurationYears"),
        ("number_of_functional_units", "NumberOfFunctionalUnits"),
        ("functional_unit_description", "FunctionalUnitDescription"),
    ]

    def __init__(
        self,
        *,
        duration_years: float,
        number_of_functional_units: Optional[float] = None,
        functional_unit_description: Optional[str] = None,
        utility: Optional[UtilitySpecification] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        Specifies the average life span for the product represented by the BoM.

        Parameters
        ----------
        duration_years: float
            The product lifespan in years.
        number_of_functional_units: Optional[float]
            The number of functional units delivered in the lifespan of the product represented by the BoM.
        functional_unit_description: Optional[str]
            A short (ideally one-word) description of a single functional unit.
        utility: Optional[UtilitySpecification]
            Indicates how much use can be obtained from the product represented by the BoM, compared to an
            industry-average example.
        """
        super().__init__(**kwargs)
        self.duration_years = duration_years
        self.number_of_functional_units = number_of_functional_units
        self.functional_unit_description = functional_unit_description
        self.utility = utility

    @property
    def duration_years(self) -> float:
        """
        The product lifespan in years.

        Returns
        -------
        float
        """
        return self._duration_years

    @duration_years.setter
    def duration_years(self, value: float) -> None:
        self._duration_years = value

    @property
    def number_of_functional_units(self) -> Optional[float]:
        """
        The number of functional units delivered in the lifespan of the product represented by the BoM.

        Returns
        -------
        Optional[float]
        """
        return self._number_of_functional_units

    @number_of_functional_units.setter
    def number_of_functional_units(self, value: Optional[float]) -> None:
        self._number_of_functional_units = value

    @property
    def functional_unit_description(self) -> Optional[str]:
        """
        A short (ideally one-word) description of a single functional unit.

        Returns
        -------
        Optional[str]
        """
        return self._functional_unit_description

    @functional_unit_description.setter
    def functional_unit_description(self, value: Optional[str]) -> None:
        self._functional_unit_description = value

    @property
    def utility(self) -> Optional[UtilitySpecification]:
        """
        Indicates how much use can be obtained from the product represented by the BoM, compared to an industry-average
        example.

        Returns
        -------
        Optional[UtilitySpecification]
        """
        return self._utility

    @utility.setter
    def utility(self, value: Optional[UtilitySpecification]) -> None:
        self._utility = value


class UsePhase(BaseType):
    _props = [
        ("ProductLifeSpan", "product_life_span", "ProductLifeSpan"),
        ("ElectricityMix", "electricity_mix", "ElectricityMix"),
        ("StaticMode", "static_mode", "StaticMode"),
        ("MobileMode", "mobile_mode", "MobileMode"),
    ]

    def __init__(
        self,
        *,
        product_life_span: ProductLifeSpan,
        electricity_mix: Optional[ElectricityMix] = None,
        static_mode: Optional[StaticMode] = None,
        mobile_mode: Optional[MobileMode] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        Provides information about the sustainability of the product whilst in use, including electricity use, emissions
        due to transport, emissions due to electricity consumption, and the expected life span of the product.

        Parameters
        ----------
        product_life_span: ProductLifeSpan
            Specifies the expected life span of the product.
        electricity_mix: Optional[ElectricityMix]
            Specifies the proportion of electricity within the destination country that comes from fossil fuels.
        static_mode: Optional[StaticMode]
            Provides information about the expected static use of the product.
        mobile_mode: Optional[MobileMode]
            Provides information about the expected mobile use of the product.
        """
        super().__init__(**kwargs)
        self.product_life_span = product_life_span
        self.electricity_mix = electricity_mix
        self.static_mode = static_mode
        self.mobile_mode = mobile_mode

    @property
    def product_life_span(self) -> ProductLifeSpan:
        """
        Specifies the expected life span of the product.

        Returns
        -------
        ProductLifeSpan
        """
        return self._product_life_span

    @product_life_span.setter
    def product_life_span(self, value: ProductLifeSpan) -> None:
        self._product_life_span = value

    @property
    def electricity_mix(self) -> Optional[ElectricityMix]:
        """
        Specifies the proportion of electricity within the destination country that comes from fossil fuels.

        Returns
        -------
        Optional[ElectricityMix]
        """
        return self._electricity_mix

    @electricity_mix.setter
    def electricity_mix(self, value: Optional[ElectricityMix]) -> None:
        self._electricity_mix = value

    @property
    def static_mode(self) -> Optional[StaticMode]:
        """
        Provides information about the expected static use of the product.

        Returns
        -------
        Optional[StaticMode]
        """
        return self._static_mode

    @static_mode.setter
    def static_mode(self, value: Optional[StaticMode]) -> None:
        self._static_mode = value

    @property
    def mobile_mode(self) -> Optional[MobileMode]:
        """
        Provides information about the expected mobile use of the product.

        Returns
        -------
        Optional[MobileMode]
        """
        return self._mobile_mode

    @mobile_mode.setter
    def mobile_mode(self, value: Optional[MobileMode]) -> None:
        self._mobile_mode = value


class BoMDetails(BaseType):
    _simple_values = [("notes", "Notes"), ("picture_url", "PictureUrl"), ("product_name", "ProductName")]

    def __init__(
        self,
        *,
        notes: Optional[str] = None,
        picture_url: Optional[str] = None,
        product_name: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        Explanatory information about a BoM.

        Parameters
        ----------
        notes: Optional[str]
            General notes for the BoM object.
        picture_url: Optional[str]
            The URL of an image to include at the top of the report. This URL must be accessible from the reporting
            services server.
        product_name: Optional[str]
            The product name.
        """
        super().__init__(**kwargs)
        self.notes = notes
        self.picture_url = picture_url
        self.product_name = product_name

    @property
    def notes(self) -> Optional[str]:
        """
        General notes for the BoM object.

        Returns
        -------
        Optional[str]
        """
        return self._notes

    @notes.setter
    def notes(self, value: Optional[str]) -> None:
        self._notes = value

    @property
    def picture_url(self) -> Optional[str]:
        """
        The URL of an image to include at the top of the report. This URL must be accessible from the reporting
        services server.

        Returns
        -------
        Optional[str]
        """
        return self._picture_url

    @picture_url.setter
    def picture_url(self, value: Optional[str]) -> None:
        self._picture_url = value

    @property
    def product_name(self) -> Optional[str]:
        """
        The product name.

        Returns
        -------
        Optional[str]
        """
        return self._product_name

    @product_name.setter
    def product_name(self, value: Optional[str]) -> None:
        self._product_name = value


class TransportStage(InternalIdentifierMixin, BaseType):
    _props = [
        ("MIRecordReference", "mi_transport_reference", "MITransportReference"),
        ("UnittedValue", "distance", "Distance"),
    ]
    _simple_values = [("name", "Name")]

    def __init__(
        self,
        *,
        name: str,
        mi_transport_reference: MIRecordReference,
        distance: UnittedValue,
        **kwargs: Any,
    ) -> None:
        """
        Defines the transportation applied to an object, in terms of the generic transportation type (stored in the
        Database) and the amount of that transport used in this instance.

        Parameters
        ----------
        name: str
            Name of this transportation stage, used only to identify the stage within the BoM.
        mi_transport_reference: MIRecordReference
            Reference to a record in the MI Database representing the means of transportation for this stage.
        distance: UnittedValue
            The distance covered by this transportation stage.

        """
        super().__init__(**kwargs)
        self.name = name
        self.mi_transport_reference = mi_transport_reference
        self.distance = distance

    @property
    def name(self) -> str:
        """
        Name of this transportation stage, used only to identify the stage within the BoM.

        Returns
        -------
        str
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def mi_transport_reference(self) -> MIRecordReference:
        """
        Reference to a record in the MI Database representing the means of transportation for this stage.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_transport_reference

    @mi_transport_reference.setter
    def mi_transport_reference(self, value: MIRecordReference) -> None:
        self._mi_transport_reference = value

    @property
    def distance(self) -> UnittedValue:
        """
        The distance covered by this transportation stage.

        Returns
        -------
        UnittedValue
        """
        return self._distance

    @distance.setter
    def distance(self, value: UnittedValue) -> None:
        self._distance = value


class Specification(CommonIdentifiersMixin, InternalIdentifierMixin, BaseType):
    _props = [
        ("MIRecordReference", "mi_specification_reference", "MISpecificationReference"),
        ("UnittedValue", "quantity", "Quantity"),
    ]

    def __init__(
        self,
        *,
        mi_specification_reference: MIRecordReference,
        quantity: Optional[UnittedValue] = None,
        **kwargs: Any,
    ) -> None:
        """
        A specification for a part, process, or material. Refers to a record with the MI Database storing the details
        of the specification and its impact.

        Parameters
        ----------
        mi_specification_reference: MIRecordReference
            Reference identifying the record representing this specification in the MI Database.
        quantity: Optional[UnittedValue]
            A quantification of the specification, if applicable.
        """
        super().__init__(**kwargs)
        self.mi_specification_reference = mi_specification_reference
        self.quantity = quantity

    @property
    def mi_specification_reference(self) -> MIRecordReference:
        """
        Reference identifying the record representing this specification in the MI Database.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_specification_reference

    @mi_specification_reference.setter
    def mi_specification_reference(self, value: MIRecordReference) -> None:
        self._mi_specification_reference = value

    @property
    def quantity(self) -> Optional[UnittedValue]:
        """
        A quantification of the specification, if applicable.

        Returns
        -------
        Optional[UnittedValue]
        """
        return self._quantity

    @quantity.setter
    def quantity(self, value: Optional[UnittedValue]) -> None:
        self._quantity = value


class Substance(CommonIdentifiersMixin, InternalIdentifierMixin, BaseType):
    _simple_values = [("percentage", "Percentage"), ("category", "Category")]

    _props = [("MIRecordReference", "mi_substance_reference", "MISubstanceReference")]

    def __init__(
        self,
        *,
        mi_substance_reference: MIRecordReference,
        percentage: Optional[float] = None,
        category: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        A substance within a part, semi-finished part, material or specification. The substance is stored in the
        Database.

        Parameters
        ----------
        mi_substance_reference: MIRecordReference
            Reference identifying the record representing the substance in the MI Database.
        percentage: Optional[Float]
            If the parent object consists of more than one substance, this defines the percentage of this
            substance.
        category: Optional[str]
            TODO - What is this?
        """
        super().__init__(**kwargs)
        self.mi_substance_reference = mi_substance_reference
        self.percentage = percentage
        self.category = category

    @property
    def mi_substance_reference(self) -> MIRecordReference:
        """
        Reference identifying the record representing the substance in the MI Database.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_substance_reference

    @mi_substance_reference.setter
    def mi_substance_reference(self, value: MIRecordReference) -> None:
        self._mi_substance_reference = value

    @property
    def percentage(self) -> Optional[float]:
        """
        If the parent object consists of more than one substance, this defines the percentage of this substance.

        Returns
        -------
        Optional[float]
        """
        return self._percentage

    @percentage.setter
    def percentage(self, value: Optional[float]) -> None:
        self._percentage = value

    @property
    def category(self) -> Optional[str]:
        """
        TODO - Who can say?

        Returns
        -------
        Optional[str]
        """
        return self._category

    @category.setter
    def category(self, value: Optional[str]) -> None:
        self._category = value


class Process(CommonIdentifiersMixin, InternalIdentifierMixin, BaseType):
    _simple_values = [("percentage_of_part_affected", "Percentage")]

    _props = [
        ("MIRecordReference", "mi_process_reference", "MIProcessReference"),
        ("UnittedValue", "quantity_affected", "Quantity"),
    ]

    def __init__(
        self,
        *,
        mi_process_reference: MIRecordReference,
        dimension_type: DimensionType,
        percentage_of_part_affected: Optional[float] = None,
        quantity_affected: Optional[UnittedValue] = None,
        **kwargs: Any,
    ) -> None:
        """
        A process that is applied to a subassembly, part, semi-finished part or material. The process is stored in the
        Database.

        Parameters
        ----------
        mi_process_reference: MIRecordReference
            Reference identifying a record in the MI Database containing information about this process.
        dimension_type: DimensionType
            Object defining the dimension affected by the process, for example area for coatings, or volume for
            rough machining operations.
        percentage_of_part_affected: Optional[float]
            Fraction of the object affected by the process, with basis specified by ``dimension_type``.
        quantity_affected: Optional[UnittedValue]
            Number of items affected by the process, if applicable. For example 17 fasteners are galvanized out of 24
            total.
        """
        super().__init__(**kwargs)
        self.mi_process_reference = mi_process_reference
        self.dimension_type = dimension_type
        self.percentage_of_part_affected = percentage_of_part_affected
        self.quantity_affected = quantity_affected

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        dimension_type_obj = bom_reader.get_field(Process, obj, "DimensionType")
        props["dimension_type"] = DimensionType.from_string(dimension_type_obj)
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)

        dimension_field_name = bom_writer._get_qualified_name(self, "DimensionType")
        obj[dimension_field_name] = self.dimension_type.to_string()

    @property
    def mi_process_reference(self) -> MIRecordReference:
        """
        Reference identifying a record in the MI Database containing information about this process.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_process_reference

    @mi_process_reference.setter
    def mi_process_reference(self, value: MIRecordReference) -> None:
        self._mi_process_reference = value

    @property
    def dimension_type(self) -> DimensionType:
        """
        Object defining the dimension affected by the process, for example area for coatings, or volume for rough
        machining operations.

        Returns
        -------
        DimensionType
        """
        return self._dimension_type

    @dimension_type.setter
    def dimension_type(self, value: DimensionType) -> None:
        self._dimension_type = value

    @property
    def percentage_of_part_affected(self) -> Optional[float]:
        """
        Fraction of the object affected by the process, with basis specified by ``dimension_type``.

        Returns
        -------
        Optional[float]
        """
        return self._percentage_of_part_affected

    @percentage_of_part_affected.setter
    def percentage_of_part_affected(self, value: Optional[float]) -> None:
        self._percentage_of_part_affected = value

    @property
    def quantity_affected(self) -> Optional[UnittedValue]:
        """
        Number of items affected by the process, if applicable. For example 17 fasteners are galvanized out of 24 total.

        Returns
        -------
        Optional[UnittedValue]
        """
        return self._quantity_affected

    @quantity_affected.setter
    def quantity_affected(self, value: Optional[UnittedValue]) -> None:
        self._quantity_affected = value


class Material(CommonIdentifiersMixin, InternalIdentifierMixin, BaseType):
    _simple_values = [("percentage", "Percentage")]

    _props = [("UnittedValue", "mass", "Mass"), ("MIRecordReference", "mi_material_reference", "MIMaterialReference")]

    _list_props = [
        ("Process", "processes", "Processes", "http://www.grantadesign.com/23/01/BillOfMaterialsEco", "Process"),
        (
            "EndOfLifeFate",
            "end_of_life_fates",
            "EndOfLifeFates",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
            "EndOfLifeFate",
        ),
    ]

    def __init__(
        self,
        *,
        mi_material_reference: MIRecordReference,
        percentage: Optional[float] = None,
        mass: Optional[UnittedValue] = None,
        recycle_content_is_typical: Optional[bool] = None,
        recycle_content_percentage: Optional[float] = None,
        processes: Optional[List[Process]] = None,
        end_of_life_fates: Optional[List[EndOfLifeFate]] = None,
        **kwargs: Any,
    ) -> None:
        """
        A Material within a part or semi-finished part. The material is stored in the Database.

        Parameters
        ----------
        mi_material_reference: MIRecordReference
            Reference identifying the material record within the MI Database.
        percentage: Optional[float]
            The fraction of the part consisting of this material. Provide either this or ``mass``.
        mass: Optional[UnittedValue]
            The mass of this material present within the part. Provide either this or ``percentage``.
        recycle_content_is_typical: Optional[bool]
            If True, indicates that the material's recyclability is typical, the value in the MI record will be used.
        recycle_content_percentage: Optional[float]
            If the recyclability is not typical for this material, or no typical value is available in the MI Database,
            this value indicates which percentage of this material can be recycled.
        processes: List[Process]
            Any processes associated with the production and preparation of this material.
        end_of_life_fates: List[EndOfLifeFate]
            The fates of this material once the product is disposed of.
        """
        super().__init__(**kwargs)
        self.percentage = percentage
        self.mass = mass
        self.mi_material_reference = mi_material_reference
        self.recycle_content_is_typical = recycle_content_is_typical
        self.recycle_content_percentage = recycle_content_percentage
        if processes is None:
            processes = []
        self.processes = processes
        if end_of_life_fates is None:
            end_of_life_fates = []
        self.end_of_life_fates = end_of_life_fates

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        recycle_content_obj = bom_reader.get_field(Material, obj, "RecycleContent")
        if recycle_content_obj is not None:
            typical_obj = bom_reader.get_field(Material, recycle_content_obj, "Typical")
            if typical_obj is not None:
                props["recycle_content_is_typical"] = typical_obj
            percentage_obj = bom_reader.get_field(Material, recycle_content_obj, "Percentage")
            if percentage_obj is not None:
                props["recycle_content_percentage"] = percentage_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)
        recycle_content_name = bom_writer._get_qualified_name(self, "RecycleContent")
        recycle_element = {}
        if self._recycle_content_is_typical is not None:
            typical_name = bom_writer._get_qualified_name(self, "Typical")
            recycle_element[typical_name] = self._recycle_content_is_typical
        elif self._recycle_content_is_typical is not None:
            percentage_name = bom_writer._get_qualified_name(self, "Percentage")
            recycle_element[percentage_name] = self._recycle_content_percentage
        else:
            return
        obj[recycle_content_name] = recycle_element

    @property
    def mi_material_reference(self) -> MIRecordReference:
        """
        Reference identifying the material record within the MI Database.

        Returns
        -------
        MIRecordReference
        """
        return self._mi_material_reference

    @mi_material_reference.setter
    def mi_material_reference(self, value: MIRecordReference) -> None:
        self._mi_material_reference = value

    @property
    def percentage(self) -> Optional[float]:
        """
        The fraction of the part consisting of this material. Provide either this or ``mass``.

        Returns
        -------
        Optional[float]
        """
        return self._percentage

    @percentage.setter
    def percentage(self, value: Optional[float]) -> None:
        self._percentage = value

    @property
    def mass(self) -> Optional[UnittedValue]:
        """
        The mass of this material present within the part. Provide either this or ``percentage``.

        Returns
        -------
        Optional[UnittedValue]
        """
        return self._mass

    @mass.setter
    def mass(self, value: Optional[UnittedValue]) -> None:
        self._mass = value

    @property
    def recycle_content_is_typical(self) -> Optional[bool]:
        """
        If True, indicates that the material's recyclability is typical, the value in the MI record will be used. If
        False or not provided then you must provide the ``recycle_content_percentage`` value to manually specify what
        fraction of the material is recyclable.

        Returns
        -------
        Optional[bool]
        """
        return self._recycle_content_is_typical

    @recycle_content_is_typical.setter
    def recycle_content_is_typical(self, value: Optional[bool]) -> None:
        self._recycle_content_is_typical = value

    @property
    def recycle_content_percentage(self) -> Optional[float]:
        """
        If the recyclability is not typical for this material, or no typical value is available in the MI Database, this
        value indicates which percentage of this material can be recycled.

        Returns
        -------
        Optional[float]
        """
        return self._recycle_content_percentage

    @recycle_content_percentage.setter
    def recycle_content_percentage(self, value: Optional[float]) -> None:
        self._recycle_content_percentage = value

    @property
    def processes(self) -> List[Process]:
        """
        Any processes associated with the production and preparation of this material.

        Returns
        -------
        List[Process]
        """
        return self._processes

    @processes.setter
    def processes(self, value: List[Process]) -> None:
        self._processes = value

    @property
    def end_of_life_fates(self) -> List[EndOfLifeFate]:
        """
        The fates of this material once the product is disposed of.

        Returns
        -------
        List[EndOfLifeFate]
        """
        return self._end_of_life_fates

    @end_of_life_fates.setter
    def end_of_life_fates(self, value: List[EndOfLifeFate]) -> None:
        self._end_of_life_fates = value


class Part(InternalIdentifierMixin, BaseType):
    _props = [
        ("UnittedValue", "quantity", "Quantity"),
        ("UnittedValue", "mass_per_unit_of_measure", "MassPerUom"),
        ("UnittedValue", "volume_per_unit_of_measure", "VolumePerUom"),
        ("MIRecordReference", "mi_part_reference", "MIPartReference"),
    ]

    _simple_values = [("part_number", "PartNumber"), ("part_name", "Name"), ("external_id", "ExternalIdentity")]

    _list_props = [
        ("Part", "components", "Components", "http://www.grantadesign.com/23/01/BillOfMaterialsEco", "Part"),
        (
            "Specification",
            "specifications",
            "Specifications",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
            "Specification",
        ),
        ("Material", "materials", "Materials", "http://www.grantadesign.com/23/01/BillOfMaterialsEco", "Material"),
        ("Substance", "substances", "Substances", "http://www.grantadesign.com/23/01/BillOfMaterialsEco", "Substance"),
        ("Process", "processes", "Processes", "http://www.grantadesign.com/23/01/BillOfMaterialsEco", "Process"),
        (
            "EndOfLifeFate",
            "end_of_life_fates",
            "EndOfLifeFates",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
            "EndOfLifeFate",
        ),
    ]

    def __init__(
        self,
        *,
        part_number: str,
        quantity: Optional[UnittedValue] = None,
        mass_per_unit_of_measure: Optional[UnittedValue] = None,
        volume_per_unit_of_measure: Optional[UnittedValue] = None,
        mi_part_reference: Optional[MIRecordReference] = None,
        non_mi_part_reference: Optional[Union[str, int]] = None,
        part_name: Optional[str] = None,
        external_id: Optional[str] = None,
        components: Optional[List[Part]] = None,
        specifications: Optional[List[Specification]] = None,
        materials: Optional[List[Material]] = None,
        substances: Optional[List[Substance]] = None,
        processes: Optional[List[Process]] = None,
        rohs_exemptions: Optional[List[str]] = None,
        end_of_life_fates: Optional[List[EndOfLifeFate]] = None,
        **kwargs: Any,
    ):
        """
        A single part which may or may not be stored in the MI Database.

        Parameters
        ----------
        part_number: str
            The Part Number associated with this part.
        quantity: Optional[UnittedValue]
            The quantity of part(s) used in the parent part. For discrete parts, this will be the part count - an
            integer with a blank unit (or "Each"). For continuous parts, it will be a mass, length, area or volume - a
            float value with an appropriate units.
        mass_per_unit_of_measure: Optional[UnittedValue]
            The mass of the part, after processing, relative to the unit that Quantity is given in. If MassPerUom is
            specified and VolumePerUom is not, then specifying materials within this part is interpreted to be
            percentage by mass.
        volume_per_unit_of_measure: Optional[UnittedValue]
            The volume of the part, after processing, relative to the unit that Quantity is given in. If VolumePerUom
            is specified and MassPerUom is not, then specifying materials within this part is interpreted to be
            percentage by volume.
        mi_part_reference: Optional[MIRecordReference]
            A reference identifying a part stored in the MI Database.
        non_mi_part_reference: Optional[Union[str, int]]
            A reference to a part stored in another system, for informational purposes only.
        part_name: Optional[str]
            Display name for the part.
        external_id: Optional[str]
            A temporary reference populated and used by applications to refer to the item within the BoM.
        components: List[Part]
            List of subcomponents for this part.
        specifications: List[Specification]
            List of specifications applying to this part.
        materials: List[Material]
            List of constituent materials making up this part.
        substances: List[Substances]
            List of substances contained within this part.
        processes: List[Process]
            List of processes used in the manufacture of this part.
        rohs_exemptions: List[str]
            If the part has a RoHS exemption, provide one or more justifications for the exemptions here. If the part is
            analyzed as **Non-Compliant** then the RoHS indicator will return **Compliant with Exemptions** instead.
        end_of_life_fates: List[EndOfLifeFate]
            The fate(s) of the part, at the end-of-life of the product.
        """

        super().__init__(**kwargs)
        self.quantity = quantity
        self.mass_per_unit_of_measure = mass_per_unit_of_measure
        self.volume_per_unit_of_measure = volume_per_unit_of_measure
        self.mi_part_reference = mi_part_reference
        self.non_mi_part_reference = non_mi_part_reference
        self.part_number = part_number
        self.part_name = part_name
        self.external_id = external_id
        if components is None:
            components = []
        self.components = components
        if specifications is None:
            specifications = []
        self.specifications = specifications
        if materials is None:
            materials = []
        self.materials = materials
        if substances is None:
            substances = []
        self.substances = substances
        if processes is None:
            processes = []
        self.processes = processes
        if rohs_exemptions is None:
            rohs_exemptions = []
        self.rohs_exemptions = rohs_exemptions
        if end_of_life_fates is None:
            end_of_life_fates = []
        self.end_of_life_fates = end_of_life_fates

    def __repr__(self) -> str:
        if len(self._components) == 0:
            return f"<Part '{self._part_number}'>"
        return f"<Part '{self._part_number}' with {len(self._components)} child components>"

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        non_mi_part_ref_obj = bom_reader.get_field(Part, obj, "NonMIPartReference")
        if non_mi_part_ref_obj is not None:
            props["non_mi_part_reference"] = non_mi_part_ref_obj
        rohs_exemptions_obj = bom_reader.get_field(Part, obj, "RohsExemptions")
        if rohs_exemptions_obj is not None:
            rohs_exemption_obj = bom_reader.get_field(
                Part, rohs_exemptions_obj, "RohsExemption", "http://www.grantadesign.com/23/01/BillOfMaterialsEco"
            )
            if rohs_exemption_obj is not None:
                props["rohs_exemptions"] = rohs_exemption_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)
        if self._non_mi_part_reference is not None:
            non_mi_field_name = bom_writer._get_qualified_name(self, "NonMIPartReference")
            obj[non_mi_field_name] = self._non_mi_part_reference
        if len(self._rohs_exemptions) > 0:
            rohs_exemptions_field_name = bom_writer._get_qualified_name(self, "RohsExemptions")
            rohs_exemption_field_name = bom_writer._get_qualified_name(self, "RohsExemption")
            rohs_exemptions = {rohs_exemption_field_name: self._rohs_exemptions}
            obj[rohs_exemptions_field_name] = rohs_exemptions

    @property
    def quantity(self) -> Optional[UnittedValue]:
        """
        The quantity of part(s) used in the parent part. For discrete parts, this will be the part count - an integer
        with a blank unit (or "Each"). For continuous parts, it will be a mass, length, area or volume - a float value
        with appropriate units.

        Returns
        -------
        Optional[UnittedValue]
        """
        return self._quantity

    @quantity.setter
    def quantity(self, value: Optional[UnittedValue]) -> None:
        self._quantity = value

    @property
    def mass_per_unit_of_measure(self) -> Optional[UnittedValue]:
        """
        The mass of the part, after processing, relative to the unit that Quantity is given in. If MassPerUom is
        specified and VolumePerUom is not, then specifying materials within this part is interpreted to be percentage
        by mass.

        Returns
        -------
        Optional[UnittedValue]
        """
        return self._mass_per_unit_of_measure

    @mass_per_unit_of_measure.setter
    def mass_per_unit_of_measure(self, value: Optional[UnittedValue]) -> None:
        self._mass_per_unit_of_measure = value

    @property
    def volume_per_unit_of_measure(self) -> Optional[UnittedValue]:
        """
        The volume of the part, after processing, relative to the unit that Quantity is given in. If VolumePerUom is
        specified and MassPerUom is not, then specifying materials within this part is interpreted to be percentage by
        volume.

        Returns
        -------
        Optional[UnittedValue]
        """
        return self._volume_per_unit_of_measure

    @volume_per_unit_of_measure.setter
    def volume_per_unit_of_measure(self, value: Optional[UnittedValue]) -> None:
        self._volume_per_unit_of_measure = value

    @property
    def mi_part_reference(self) -> Optional[MIRecordReference]:
        """
        A reference identifying a part stored in the MI Database.

        Returns
        -------
        Optional[MIRecordReference]
        """
        return self._mi_part_reference

    @mi_part_reference.setter
    def mi_part_reference(self, value: Optional[MIRecordReference]) -> None:
        self._mi_part_reference = value

    @property
    def non_mi_part_reference(self) -> Optional[Union[str, int]]:
        """
        A reference to a part stored in another system, for informational purposes only.

        Returns
        -------
        Optional[Union[str, int]]
        """
        return self._non_mi_part_reference

    @non_mi_part_reference.setter
    def non_mi_part_reference(self, value: Optional[Union[str, int]]) -> None:
        self._non_mi_part_reference = value

    @property
    def part_number(self) -> str:
        """
        The Part Number associated with this part.

        Returns
        -------
        str
        """
        return self._part_number

    @part_number.setter
    def part_number(self, value: str) -> None:
        self._part_number = value

    @property
    def part_name(self) -> Optional[str]:
        """
        Display name for the part.

        Returns
        -------
        Optional[str]
        """
        return self._name

    @part_name.setter
    def part_name(self, value: Optional[str]) -> None:
        self._name = value

    @property
    def external_id(self) -> Optional[str]:
        """
        A temporary reference populated and used by applications to refer to the item within the BoM.

        Returns
        -------
        Optional[str]
        """
        return self._external_id

    @external_id.setter
    def external_id(self, value: Optional[str]) -> None:
        self._external_id = value

    @property
    def components(self) -> List[Part]:
        """
        List of subcomponents for this part.

        Returns
        -------
        List[Part]
        """
        return self._components

    @components.setter
    def components(self, value: List[Part]) -> None:
        self._components = value

    @property
    def specifications(self) -> List[Specification]:
        """
        List of substances contained within this part.

        Returns
        -------
        List[Specification]
        """

        return self._specifications

    @specifications.setter
    def specifications(self, value: List[Specification]) -> None:
        self._specifications = value

    @property
    def materials(self) -> List[Material]:
        """
        List of constituent materials making up this part.

        Returns
        -------
        List[Material]
        """
        return self._materials

    @materials.setter
    def materials(self, value: List[Material]) -> None:
        self._materials = value

    @property
    def substances(self) -> List[Substance]:
        """
        List of substances contained within this part.

        Returns
        -------
        List[Substance]
        """
        return self._substances

    @substances.setter
    def substances(self, value: List[Substance]) -> None:
        self._substances = value

    @property
    def processes(self) -> List[Process]:
        """
        List of processes used in the manufacture of this part.

        Returns
        -------
        List[Process]
        """
        return self._processes

    @processes.setter
    def processes(self, value: List[Process]) -> None:
        self._processes = value

    @property
    def rohs_exemptions(self) -> List[str]:
        """
        If the part has a RoHS exemption, provide one or more justifications for the exemptions here. If the part is
        analyzed as **Non-Compliant** then the RoHS indicator will return **Compliant with Exemptions** instead.

        Returns
        -------
        List[str]
        """
        return self._rohs_exemptions

    @rohs_exemptions.setter
    def rohs_exemptions(self, value: List[str]) -> None:
        self._rohs_exemptions = value

    @property
    def end_of_life_fates(self) -> List[EndOfLifeFate]:
        """
        The fate(s) of the part, at the end-of-life of the product.

        Returns
        -------
        List[EndOfLifeFate]
        """
        return self._end_of_life_fates

    @end_of_life_fates.setter
    def end_of_life_fates(self, value: List[EndOfLifeFate]) -> None:
        self._end_of_life_fates = value


class AnnotationSource(InternalIdentifierMixin, BaseType):
    _simple_values = [("name", "Name"), ("method", "Method")]

    def __init__(
        self, *, name: str, method: Optional[str] = None, data: Optional[List[Any]] = None, **kwargs: Any
    ) -> None:
        """
        An element indicating the source of annotations in the BoM. Each source may be
        referenced by zero or more annotations. The producer and consumer(s) of the BoM must agree the
        understood annotation source semantics, particularly regarding the untyped data therein. When a tool consumes
        and re-produces BoMs, it should generally retain any annotation sources that it does not understand (of course,
        it can also decide whether to keep, modify or discard those annotation sources that it does understand).

        The parameter documentation below is the suggested convention.

        Parameters
        ----------
        name: str
            The name of the software package that generated this annotation.
        method: Optional[str]
            The calculation method used to generate this annotation.
        data: List[Any]
            Data that the consumer of the BoM may require.
        """
        super().__init__(**kwargs)
        self.name = name
        self.method = method
        if data is None:
            data = []
        self.data = data

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        data_obj = bom_reader.get_field(AnnotationSource, obj, "Data")
        if data_obj is not None:
            props["data"] = data_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        if len(self._data) > 0:
            data_field_name = bom_writer._get_qualified_name(self, "Data")
            obj[data_field_name] = self._data

    @property
    def name(self) -> str:
        """
        The name of the software package that generated this annotation.

        Returns
        -------
        str
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def method(self) -> Optional[str]:
        """
        The calculation method used to generate this annotation.

        Returns
        -------
        Optional[str]
        """
        return self._method

    @method.setter
    def method(self, value: Optional[str]) -> None:
        self._method = value

    @property
    def data(self) -> List[Any]:
        """
        Data that the consumer of the BoM may require.

        Returns
        -------
        List[Any]
        """
        return self._data

    @data.setter
    def data(self, value: List[Any]) -> None:
        self._data = value


class Annotation(BaseType):
    _props = [("UnittedValue", "value", "Value")]

    _simple_values = [("type", "type"), ("target_id", "targetId"), ("source_id", "sourceId")]

    def __init__(
        self,
        *,
        target_id: str,
        source_id: Optional[str] = None,
        type_: str,
        value: Union[str, UnittedValue],
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        An annotation that can be attached to objects within a BoM. The understood annotation types must be agreed
        between the producer and consumer(s) of the BoM.  The producer and consumer(s) must also agree whether a
        particular type of annotation is allowed to have multiple instances assigned to a single element, or whether
        only a single annotation of that type per element is allowed. When a tool consumes and re-produces BoMs, it
        should generally retain any annotations that it does not understand (of course, it can also decide whether to
        keep, modify or discard those annotations that it does understand).

        Annotations can either be pure textual data, providing additional data or context for an object, or they can
        provide additional indicators, for example Embodied Energy of Production, or Cost of Raw Materials.

        Parameters
        ----------
        target_id: str
            The ``internal_identity`` of exactly one element to which the annotation applies.
        source_id: Optional[str]
            If provided, is the ``internal_identity`` of exactly one ``AnnotationSource`` object describing the source
            of the annotation. If absent, no source information is provided.
        type_: str
            A string value indicating the type of the annotation, the accepted values for this parameter must be agreed
            between the produced and consumer(s) of the BoM.
        value: Union[str, UnittedValue]
            The content of this annotation.
        """
        super().__init__(**kwargs)
        self.target_id = target_id
        self.source_id = source_id
        self.type_ = type_
        self.value = value

    @property
    def target_id(self) -> str:
        """
        The ``internal_identity`` of exactly one element to which the annotation applies.

        Returns
        -------
        str
        """
        return self._target_id

    @target_id.setter
    def target_id(self, value: str) -> None:
        self._target_id = value

    @property
    def source_id(self) -> Optional[str]:
        """
        If provided, is the ``internal_identity`` of exactly one ``AnnotationSource`` object describing the source of
        the annotation. If absent, no source information is provided.

        Returns
        -------
        str
        """
        return self.source_id

    @source_id.setter
    def source_id(self, value: Optional[str]) -> None:
        self._source_id = value

    @property
    def type_(self) -> str:
        """
        A string value indicating the type of the annotation, the accepted values for this parameter must be agreed
        between the produced and consumer(s) of the BoM.

        Returns
        -------
        str
        """
        return self._type_

    @type_.setter
    def type_(self, value: str) -> None:
        self._type_ = value

    @property
    def value(self) -> Union[str, UnittedValue]:
        """
        The content of this annotation

        Returns
        -------
        Union[str, UnittedValue]
        """
        return self._value

    @value.setter
    def value(self, value: Union[str, UnittedValue]) -> None:
        self._value = value


class BillOfMaterials(InternalIdentifierMixin, BaseType):
    _props = [
        ("UsePhase", "use_phase", "UsePhase"),
        ("Location", "location", "Location"),
        ("BoMDetails", "notes", "Notes"),
    ]
    _list_props = [
        ("Part", "components", "Components", "http://www.grantadesign.com/23/01/BillOfMaterialsEco", "Part"),
        (
            "TransportStage",
            "transport_phase",
            "TransportPhase",
            "http://www.grantadesign.com/23/01/BillOfMaterialsEco",
            "TransportStage",
        ),
    ]

    def __init__(
        self,
        *,
        components: List[Part],
        transport_phase: Optional[List[TransportStage]] = None,
        use_phase: Optional[UsePhase] = None,
        location: Optional[Location] = None,
        notes: Optional[BoMDetails] = None,
        annotations: Optional[List[Annotation]] = None,
        annotation_sources: Optional[List[AnnotationSource]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Type representing the root Bill of Materials object.

        Parameters
        ----------
        components: List[Part]
            The parts contained within this BoM.
        transport_phase: List[TransportStage]
            The different forms of transport to which the parts are subject.
        use_phase: Optional[UsePhase]
            The type of use to which this product is subject.
        location: Optional[Location]
            The location in which the object represented by the BoM is assembled.
        notes: Optional[BoMDetails]
            Any optional notes about this BoM.
        annotations: List[Annotation]
            Any annotations that are associated with objects within the BoM.
        annotation_sources: List[AnnotationSource]
            Sources for annotations present within the BoM.
        """
        super().__init__(**kwargs)
        self.components = components
        if transport_phase is None:
            transport_phase = []
        self.transport_phase = transport_phase
        self.use_phase = use_phase
        self.location = location
        self.notes = notes
        if annotations is None:
            annotations = []
        self.annotations = annotations
        if annotation_sources is None:
            annotation_sources = []
        self.annotation_sources = annotation_sources

    def __repr__(self) -> str:
        return f"<BillOfMaterials with {len(self._components)} root components>"

    @property
    def components(self) -> List[Part]:
        """
        The parts contained within this BoM.

        Returns
        -------
        List[Part]
        """
        return self._components

    @components.setter
    def components(self, value: List[Part]) -> None:
        self._components = value

    @property
    def transport_phase(self) -> List[TransportStage]:
        """
        The different forms of transport to which the parts are subject.

        Returns
        -------
        List[TransportStage]
        """
        return self._transport_phase

    @transport_phase.setter
    def transport_phase(self, value: List[TransportStage]) -> None:
        self._transport_phase = value

    @property
    def use_phase(self) -> Optional[UsePhase]:
        """
        The type of use to which this product is subject.

        Returns
        -------
        Optional[UsePhase]
        """
        return self._use_phase

    @use_phase.setter
    def use_phase(self, value: Optional[UsePhase]) -> None:
        self._use_phase = value

    @property
    def location(self) -> Optional[Location]:
        """
        The location in which the object represented by the BoM is assembled.

        Returns
        -------
        Optional[Location]
        """
        return self._location

    @location.setter
    def location(self, value: Optional[Location]) -> None:
        self._location = value

    @property
    def notes(self) -> Optional[BoMDetails]:
        """
        Any optional notes about this BoM.

        Returns
        -------
        Optional[BoMDetails]
        """
        return self._notes

    @notes.setter
    def notes(self, value: Optional[BoMDetails]) -> None:
        self._notes = value

    @property
    def annotations(self) -> List[Annotation]:
        """
        Any annotations that are associated with objects within the BoM.

        Returns
        -------
        List[Annotation]
        """
        return self._annotations

    @annotations.setter
    def annotations(self, value: List[Annotation]) -> None:
        self._annotations = value

    @property
    def annotation_sources(self) -> List[AnnotationSource]:
        """
        Sources for annotations present within the BoM.

        Returns
        -------
        List[AnnotationSource]
        """
        return self._annotation_sources

    @annotation_sources.setter
    def annotation_sources(self, value: List[AnnotationSource]) -> None:
        self._annotation_sources = value
