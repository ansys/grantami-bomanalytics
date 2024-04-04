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

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Protocol, Tuple, cast

if TYPE_CHECKING:
    from ._bom_reader import BoMReader
    from ._bom_writer import BoMWriter


class HasNamespace(Protocol):
    """
    Protocol defining that an inheritor has an attribute *_namespace*.
    """

    _namespace: str


class SupportsCustomFields(Protocol):
    """
    Protocol defining that an inheritor has methods to process and write custom fields.
    """

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]: ...

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None: ...


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
        Populates any fields on the object that are in a nonstandard configuration. This can be anonymous complex types,
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


class DimensionType(Enum):
    """
    Valid values for DimensionType.
    """

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


class Category(Enum):
    """
    Valid values for Category.
    """

    Null = 0
    Incorporated = 1
    MayBeIncorporated = 2
    UsedInProduction = 3
    MayBeUsedInProduction = 4
    UsedInCoating = 5

    @classmethod
    def from_string(cls, value: str) -> Category:
        """
        Convert string representation of this object into an instance of this object.

        Parameters
        ----------
        value: str
            String representation of this object.
        """
        return Category[value]

    def to_string(self) -> str:
        """
        Convert this Enum object to its string representation.

        Returns
        -------
        str
            String representation of this object.
        """
        return self.name


@dataclass
class PartialTableReference(BaseType):
    """
    A type that partially identifies a Table, but does not specify the MI Database. Usually, just one of the several
    optional fields should be provided; where more than one is provided, the highest priority one is used, where the
    descending priority order is: tableIdentity, tableGUID, tableName.
    """

    _simple_values = [("table_identity", "tableIdentity"), ("table_guid", "tableGUID"), ("table_name", "tableName")]

    _namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

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

    _namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

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
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
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

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
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

    _namespace = "http://www.grantadesign.com/12/05/GrantaBaseTypes"

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
            attr_ref_obj = bom_reader.get_field(MIRecordReference, lookup_obj, "attributeReference")
            props["lookup_attribute_reference"] = bom_reader.create_type("MIAttributeReference", attr_ref_obj)
            props["lookup_value"] = bom_reader.get_field(MIRecordReference, lookup_obj, "attributeValue")
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
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


@dataclass
class EndOfLifeFate(BaseType):
    """
    The fate of a material at the end-of-life of the product. For example if a material can be recycled, and what
    fraction of the total mass or volume can be recycled.
    """

    _simple_values = [("fraction", "Fraction")]

    _props = [("MIRecordReference", "mi_end_of_life_reference", "MIEndOfLifeReference")]

    mi_end_of_life_reference: MIRecordReference
    """Reference identifying the applicable fate within the MI Database."""

    fraction: float
    """Fraction of the total mass or volume of material to which this fate applies."""


@dataclass
class UnittedValue(BaseType):
    """
    A physical quantity with a unit. If provided in an input then the unit must exist within the MI database,
    otherwise an error will be raised.
    """

    _simple_values = [("value", "$"), ("unit", "@Unit")]

    value: float
    """The value of the quantity in specified units."""

    unit: Optional[str] = None
    """If provided, specifies the unit symbol applying to the quantity. If absent the quantity will be treated as
    dimensionless."""


@dataclass
class Location(BaseType):
    """
    Defines the manufacturing location for the BoM for use in process calculations.
    """

    _props = [("MIRecordReference", "mi_location_reference", "MILocationReference")]
    _simple_values = [
        ("identity", "Identity"),
        ("name", "Name"),
        ("external_identity", "ExternalIdentity"),
        ("internal_id", "@id"),
    ]

    mi_location_reference: Optional[MIRecordReference] = None  # TODO not optional though
    """Reference to a record in the MI database representing the manufacturing location."""

    identity: Optional[str] = None
    """A display identity for the object."""

    name: Optional[str] = None
    """A display name for the object."""

    external_identity: Optional[str] = None
    """A temporary reference populated and used by applications to refer to the item within the BoM."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""


@dataclass
class ElectricityMix(BaseType):
    """
    If the product consumes electrical power, then the amount of CO2 produced to generate depends upon the mix of
    fossil fuel burning power stations in the region of use.  This type lets you specify the electrical generation
    mix by either specifying the region or country of use or by specifying the percentage of power that comes from
    fossil fuel sources.
    """

    _props = [("MIRecordReference", "mi_region_reference", "MIRegionReference")]
    _simple_values = [("percentage_fossil_fuels", "PercentageFossilFuels")]

    mi_region_reference: Optional[MIRecordReference] = None
    """Reference to a record in the MI database representing the electricity mix for the destination country."""

    percentage_fossil_fuels: Optional[float] = None
    """The percentage of electrical power production within the destination country that comes from fossil fuels."""


@dataclass
class MobileMode(BaseType):
    """
    If the product is transported as part of its use then this type contains details about the way in which it is
    transported.
    """

    _props = [
        ("MIRecordReference", "mi_transport_reference", "MITransportReference"),
        ("UnittedValue", "distance_travelled_per_day", "DistanceTravelledPerDay"),
    ]
    _simple_values = [("days_used_per_year", "DaysUsedPerYear")]

    mi_transport_reference: MIRecordReference
    """Reference to a record in the MI database representing the means of transport for this product during use."""

    days_used_per_year: float
    """The number of days in a year the product will be transported during use."""

    distance_travelled_per_day: UnittedValue
    """The distance the product will be transported each day as part of its use."""


@dataclass
class StaticMode(BaseType):
    """
    Specifies the primary energy conversion that occurs during the product's use.
    """

    _props = [
        ("MIRecordReference", "mi_energy_conversion_reference", "MIEnergyConversionReference"),
        ("UnittedValue", "power_rating", "PowerRating"),
    ]

    mi_energy_conversion_reference: MIRecordReference
    """Reference to a record in the MI database representing the primary energy conversion taking place when the
    product is in use."""

    power_rating: UnittedValue
    """The power rating of the product whilst in use."""

    days_used_per_year: float
    """The number of days per year that the product will be used."""

    hours_used_per_day: float
    """The number of hours per day of use that the product will be used."""

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        usage_obj = bom_reader.get_field(cls, obj, "Usage")
        if usage_obj is not None:
            props["hours_used_per_day"] = bom_reader.get_field(cls, usage_obj, "HoursUsedPerDay")
            props["days_used_per_year"] = bom_reader.get_field(cls, usage_obj, "DaysUsedPerYear")
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)
        usage_dict = {
            bom_writer._get_qualified_name(self, "DaysUsedPerYear"): self.days_used_per_year,
            bom_writer._get_qualified_name(self, "HoursUsedPerDay"): self.hours_used_per_day,
        }
        obj[bom_writer._get_qualified_name(self, "Usage")] = usage_dict


@dataclass
class UtilitySpecification(BaseType):
    """
    Specifies how much use can be obtained from the product represented by this BoM in comparison to a
    representative industry average.
    """

    _simple_values = [
        ("industry_average_duration_years", "IndustryAverageDurationYears"),
        ("industry_average_number_of_functional_units", "IndustryAverageNumberOfFunctionalUnits"),
        ("utility", "Utility"),
    ]

    industry_average_duration_years: Optional[float] = None
    """The average lifespan of all examples, throughout the industry, of the kind of product described herein."""

    industry_average_number_of_functional_units: Optional[float] = None
    """The average number of functional units delivered, in their lifespan, by all examples, throughout the
    industry, of the kind of product represented by this object."""

    utility: Optional[float] = None
    """Directly specifies the utility."""


@dataclass
class ProductLifeSpan(BaseType):
    """
    Specifies the average life span for the product represented by the BoM.
    """

    _props = [("UtilitySpecification", "utility", "Utility")]
    _simple_values = [
        ("duration_years", "DurationYears"),
        ("number_of_functional_units", "NumberOfFunctionalUnits"),
        ("functional_unit_description", "FunctionalUnitDescription"),
    ]
    duration_years: float
    """The product lifespan in years."""

    number_of_functional_units: Optional[float] = None
    """The number of functional units delivered in the lifespan of the product represented by the BoM."""

    functional_unit_description: Optional[str] = None
    """A short (ideally one-word) description of a single functional unit."""

    utility: Optional[UtilitySpecification] = None
    """Indicates how much use can be obtained from the product represented by the BoM, compared to an
    industry-average example."""


@dataclass
class UsePhase(BaseType):
    """
    Provides information about the sustainability of the product whilst in use, including electricity use, emissions
    due to transport, emissions due to electricity consumption, and the expected life span of the product.
    """

    _props = [
        ("ProductLifeSpan", "product_life_span", "ProductLifeSpan"),
        ("ElectricityMix", "electricity_mix", "ElectricityMix"),
        ("StaticMode", "static_mode", "StaticMode"),
        ("MobileMode", "mobile_mode", "MobileMode"),
    ]

    product_life_span: ProductLifeSpan
    """Specifies the expected life span of the product."""

    electricity_mix: Optional[ElectricityMix] = None
    """ Specifies the proportion of electricity within the destination country that comes from fossil fuels."""

    static_mode: Optional[StaticMode] = None
    """Provides information about the expected static use of the product."""

    mobile_mode: Optional[MobileMode] = None
    """Provides information about the expected mobile use of the product."""


@dataclass
class BoMDetails(BaseType):
    """
    Explanatory information about a BoM.
    """

    _simple_values = [("notes", "Notes"), ("picture_url", "PictureUrl"), ("product_name", "ProductName")]

    notes: Optional[str] = None
    """General notes for the BoM object."""

    picture_url: Optional[str] = None
    """The URL of an image to include at the top of the report. This URL must be accessible from the reporting
    services server."""

    product_name: Optional[str] = None
    """The product name."""


@dataclass
class TransportStage(BaseType):
    """
    Defines the transportation applied to an object, in terms of the generic transportation type (stored in the
    Database) and the amount of that transport used in this instance.
    """

    _props = [
        ("MIRecordReference", "mi_transport_reference", "MITransportReference"),
        ("UnittedValue", "distance", "Distance"),
    ]
    _simple_values = [("name", "Name"), ("internal_id", "@id")]

    name: str
    """Name of this transportation stage, used only to identify the stage within the BoM."""

    mi_transport_reference: MIRecordReference
    """Reference to a record in the MI Database representing the means of transportation for this stage."""

    distance: UnittedValue
    """The distance covered by this transportation stage."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""


@dataclass
class Specification(BaseType):
    """
    A specification for a surface treatment, part, process, or material. Refers to a record within the MI Database
    storing the details of the specification and its impact.
    """

    _props = [
        ("MIRecordReference", "mi_specification_reference", "MISpecificationReference"),
        ("UnittedValue", "quantity", "Quantity"),
    ]
    _simple_values = [
        ("identity", "Identity"),
        ("name", "Name"),
        ("external_identity", "ExternalIdentity"),
        ("internal_id", "@id"),
    ]

    mi_specification_reference: MIRecordReference
    """Reference identifying the record representing this specification in the MI Database."""

    quantity: Optional[UnittedValue] = None
    """A quantification of the specification, if applicable."""

    identity: Optional[str] = None
    """A display identity for the object."""

    name: Optional[str] = None
    """A display name for the object."""

    external_identity: Optional[str] = None
    """A temporary reference populated and used by applications to refer to the item within the BoM."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""


@dataclass
class Substance(BaseType):
    """
    A substance within a part, semi-finished part, material or specification. The substance is stored in the
    Database."""

    _simple_values = [
        ("percentage", "Percentage"),
        ("identity", "Identity"),
        ("name", "Name"),
        ("external_identity", "ExternalIdentity"),
        ("internal_id", "@id"),
    ]
    _props = [("MIRecordReference", "mi_substance_reference", "MISubstanceReference")]

    mi_substance_reference: MIRecordReference
    """Reference identifying the record representing the substance in the MI Database."""

    percentage: Optional[float] = None
    """If the parent object consists of more than one substance, this defines the percentage of this
    substance."""

    category: Optional[Category] = None
    """Represents whether the substance remains present in the material after production."""

    identity: Optional[str] = None
    """A display identity for the object."""

    name: Optional[str] = None
    """A display name for the object."""

    external_identity: Optional[str] = None
    """A temporary reference populated and used by applications to refer to the item within the BoM."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        category_type_obj = bom_reader.get_field(Substance, obj, "Category")
        if category_type_obj is not None:
            props["category"] = Category.from_string(category_type_obj)
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)

        if self.category is not None:
            category_field_name = bom_writer._get_qualified_name(self, "Category")
            obj[category_field_name] = self.category.to_string()


@dataclass
class Process(BaseType):
    """
    A process that is applied to a subassembly, part, semi-finished part or material. The process is stored in the
    Database.
    """

    _simple_values = [
        ("percentage", "Percentage"),
        ("identity", "Identity"),
        ("name", "Name"),
        ("external_identity", "ExternalIdentity"),
        ("internal_id", "@id"),
    ]

    _props = [
        ("MIRecordReference", "mi_process_reference", "MIProcessReference"),
        ("UnittedValue", "quantity", "Quantity"),
    ]

    mi_process_reference: MIRecordReference
    """Reference identifying a record in the MI Database containing information about this process."""

    dimension_type: DimensionType
    """Object defining the dimension affected by the process, for example area for coatings, or mass removed for
    machining operations."""

    percentage: Optional[float] = None
    """Fraction of the object affected by the process, with basis specified by ``dimension_type``. Only supported for
    dimension types ``Mass`` and ``MassRemoved``."""

    quantity: Optional[UnittedValue] = None
    """A quantification of the process according to its dimension type."""

    identity: Optional[str] = None
    """A display identity for the object."""

    name: Optional[str] = None
    """A display name for the object."""

    external_identity: Optional[str] = None
    """A temporary reference populated and used by applications to refer to the item within the BoM."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""

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


@dataclass
class Material(BaseType):
    """
    A Material within a part or semi-finished part. The material is stored in the Database.
    """

    _simple_values = [
        ("percentage", "Percentage"),
        ("identity", "Identity"),
        ("name", "Name"),
        ("external_identity", "ExternalIdentity"),
        ("internal_id", "@id"),
    ]

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
    mi_material_reference: MIRecordReference
    """Reference identifying the material record within the MI Database."""

    percentage: Optional[float] = None
    """The fraction of the part consisting of this material. Provide either this or ``mass``."""

    mass: Optional[UnittedValue] = None
    """The mass of this material present within the part. Provide either this or ``percentage``."""

    # TODO support recycle content (issue #95)
    # recycle_content_is_typical: Optional[bool] = None
    # """If True, indicates that the material's recyclability is typical, the value in the MI record will be used."""

    recycle_content_percentage: Optional[float] = None
    """If the recyclability is not typical for this material, or no typical value is available in the MI Database,
    this value indicates which percentage of this material can be recycled."""

    processes: List[Process] = field(default_factory=list)
    """Any processes associated with the production and preparation of this material."""

    end_of_life_fates: List[EndOfLifeFate] = field(default_factory=list)
    """The fates of this material once the product is disposed of."""

    identity: Optional[str] = None
    """A display identity for the object."""

    name: Optional[str] = None
    """A display name for the object."""

    external_identity: Optional[str] = None
    """A temporary reference populated and used by applications to refer to the item within the BoM."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        recycle_content_obj = bom_reader.get_field(Material, obj, "RecycleContent")
        if recycle_content_obj is not None:
            # TODO support recycle content (issue #95)
            # typical_obj = bom_reader.get_field(Material, recycle_content_obj, "Typical")
            # if typical_obj is not None:
            #     props["recycle_content_is_typical"] = typical_obj
            percentage_obj = bom_reader.get_field(Material, recycle_content_obj, "Percentage")
            if percentage_obj is not None:
                props["recycle_content_percentage"] = percentage_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)
        recycle_content_name = bom_writer._get_qualified_name(self, "RecycleContent")
        recycle_element = {}
        # TODO support recycle content (issue #95)
        # if self.recycle_content_is_typical is not None:
        #     typical_name = bom_writer._get_qualified_name(self, "Typical")
        #     recycle_element[typical_name] = self.recycle_content_is_typical
        if self.recycle_content_percentage is not None:
            percentage_name = bom_writer._get_qualified_name(self, "Percentage")
            recycle_element[percentage_name] = self.recycle_content_percentage
            obj[recycle_content_name] = recycle_element


@dataclass
class Part(BaseType):
    """
    A single part which may or may not be stored in the MI Database.
    """

    _props = [
        ("UnittedValue", "quantity", "Quantity"),
        ("UnittedValue", "mass_per_unit_of_measure", "MassPerUom"),
        ("UnittedValue", "volume_per_unit_of_measure", "VolumePerUom"),
        ("MIRecordReference", "mi_part_reference", "MIPartReference"),
    ]

    _simple_values = [
        ("part_number", "PartNumber"),
        ("part_name", "Name"),
        ("external_identity", "ExternalIdentity"),
        ("internal_id", "@id"),
    ]

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

    part_number: str
    """The Part Number associated with this part."""

    quantity: Optional[UnittedValue] = None
    """The quantity of part(s) used in the parent part. For discrete parts, this will be the part count - an
    integer with a blank unit (or "Each"). For continuous parts, it will be a mass, length, area or volume - a
    float value with an appropriate units."""

    mass_per_unit_of_measure: Optional[UnittedValue] = None
    """The mass of the part, after processing, relative to the unit that Quantity is given in. If MassPerUom is
    specified and VolumePerUom is not, then specifying materials within this part is interpreted to be
    percentage by mass."""

    volume_per_unit_of_measure: Optional[UnittedValue] = None
    """The volume of the part, after processing, relative to the unit that Quantity is given in. If VolumePerUom
    is specified and MassPerUom is not, then specifying materials within this part is interpreted to be
    percentage by volume."""

    mi_part_reference: Optional[MIRecordReference] = None
    """A reference identifying a part stored in the MI Database."""

    # TODO support non_mi_part_reference (issue #95)
    # non_mi_part_reference: Optional[str] = None
    # """A reference to a part stored in another system, for informational purposes only."""

    part_name: Optional[str] = None
    """Display name for the part."""

    external_identity: Optional[str] = None
    """A temporary reference populated and used by applications to refer to the item within the BoM."""

    components: List[Part] = field(default_factory=list)
    """List of subcomponents for this part."""

    specifications: List[Specification] = field(default_factory=list)
    """List of specifications applying to this part."""

    materials: List[Material] = field(default_factory=list)
    """List of constituent materials making up this part."""

    substances: List[Substance] = field(default_factory=list)
    """List of substances contained within this part."""

    processes: List[Process] = field(default_factory=list)
    """List of processes used in the manufacture of this part."""

    rohs_exemptions: List[str] = field(default_factory=list)
    """If the part has a RoHS exemption, provide one or more justifications for the exemptions here. If the part is
    analyzed as **Non-Compliant** then the RoHS indicator will return **Compliant with Exemptions** instead."""

    end_of_life_fates: List[EndOfLifeFate] = field(default_factory=list)
    """The fate(s) of the part, at the end-of-life of the product."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""

    @classmethod
    def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        # TODO support non_mi_part_reference (issue #95)
        # non_mi_part_ref_obj = bom_reader.get_field(Part, obj, "NonMIPartReference")
        # if non_mi_part_ref_obj is not None:
        #     props["non_mi_part_reference"] = non_mi_part_ref_obj
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
        # TODO support non_mi_part_reference (issue #95)
        # if self.non_mi_part_reference is not None:
        #     non_mi_field_name = bom_writer._get_qualified_name(self, "NonMIPartReference")
        #     obj[non_mi_field_name] = self.non_mi_part_reference
        if len(self.rohs_exemptions) > 0:
            rohs_exemptions_field_name = bom_writer._get_qualified_name(self, "RohsExemptions")
            rohs_exemption_field_name = bom_writer._get_qualified_name(self, "RohsExemption")
            rohs_exemptions = {rohs_exemption_field_name: self.rohs_exemptions}
            obj[rohs_exemptions_field_name] = rohs_exemptions


# @dataclass
# class AnnotationSource(BaseType):
#     """
#     An element indicating the source of annotations in the BoM. Each source may be
#     referenced by zero or more annotations. The producer and consumer(s) of the BoM must agree the
#     understood annotation source semantics, particularly regarding the untyped data therein. When a tool consumes
#     and re-produces BoMs, it should generally retain any annotation sources that it does not understand (of course,
#     it can also decide whether to keep, modify or discard those annotation sources that it does understand).
#     """
#
#     _simple_values = [("name", "Name"), ("method", "Method")]
#
#     name: str
#     """The name of the software package that generated this annotation."""
#
#     method: Optional[str] = None
#     """The calculation method used to generate this annotation."""
#
#     data: List[Any] = field(default_factory=list)
#     """Data that the consumer of the BoM may require."""
#
#     internal_id: Optional[str] = None
#     """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
#     to reference this element."""
#
#     @classmethod
#     def _process_custom_fields(cls, obj: Dict, bom_reader: BoMReader) -> Dict[str, Any]:
#         props = super()._process_custom_fields(obj, bom_reader)
#
#         data_obj = bom_reader.get_field(AnnotationSource, obj, "Data")
#         if data_obj is not None:
#             props["data"] = data_obj
#         return props
#
#     def _write_custom_fields(self, obj: Dict, bom_writer: BoMWriter) -> None:
#         if len(self.data) > 0:
#             data_field_name = bom_writer._get_qualified_name(self, "Data")
#             obj[data_field_name] = self.data
#
#
# @dataclass
# class Annotation(BaseType):
#     """
#     An annotation that can be attached to objects within a BoM. The understood annotation types must be agreed
#     between the producer and consumer(s) of the BoM.  The producer and consumer(s) must also agree whether a
#     particular type of annotation is allowed to have multiple instances assigned to a single element, or whether
#     only a single annotation of that type per element is allowed. When a tool consumes and re-produces BoMs, it
#     should generally retain any annotations that it does not understand (of course, it can also decide whether to
#     keep, modify or discard those annotations that it does understand).
#
#     Annotations can either be pure textual data, providing additional data or context for an object, or they can
#     provide additional indicators, for example Embodied Energy of Production, or Cost of Raw Materials.
#     """
#
#     _props = [("UnittedValue", "value", "Value")]
#
#     _simple_values = [("type_", "@type"), ("target_id", "@targetId"), ("source_id", "@sourceId")]
#
#     target_id: str
#     """The ``internal_id`` of exactly one element to which the annotation applies."""
#
#     type_: str
#     """A string value indicating the type of the annotation, the accepted values for this parameter must be agreed
#     between the produced and consumer(s) of the BoM."""
#
#     value: Union[str, UnittedValue]
#     """The content of this annotation."""
#
#     source_id: Optional[str] = None
#     """If provided, is the ``internal_id`` of exactly one ``AnnotationSource`` object describing the source
#     of the annotation. If absent, no source information is provided."""


@dataclass
class BillOfMaterials(BaseType):
    """
    Type representing the root Bill of Materials object.
    """

    _simple_values = [("internal_id", "@id")]
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

    components: List[Part]
    """The parts contained within this BoM."""

    transport_phase: List[TransportStage] = field(default_factory=list)
    """The different forms of transport to which the parts are subject."""

    use_phase: Optional[UsePhase] = None
    """The type of use to which this product is subject."""

    location: Optional[Location] = None
    """The location in which the object represented by the BoM is assembled."""

    notes: Optional[BoMDetails] = None
    """Any optional notes about this BoM."""

    # TODO support annotations (issue #95)
    # annotations: List[Annotation] = field(default_factory=list)
    # """Any annotations that are associated with objects within the BoM."""
    #
    # annotation_sources: List[AnnotationSource] = field(default_factory=list)
    # """Sources for annotations present within the BoM."""

    internal_id: Optional[str] = None
    """A unique identity for this object in this BoM. This identity is only for internal use, allowing other elements
    to reference this element."""
