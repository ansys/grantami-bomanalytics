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

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .._base_types import BaseType, QualifiedXMLName
from ..gbt1205 import MIRecordReference

if TYPE_CHECKING:
    from ._bom_reader import _BoMReader
    from ._bom_writer import _BoMWriter


class BaseTypeEco2301(BaseType):
    namespace = "http://www.grantadesign.com/23/01/BillOfMaterialsEco"


@dataclass(frozen=True)
class _QualifiedEco2301Name(QualifiedXMLName):
    """
    A fully qualified XML name. The local name must be supplied, and the namespace defaults to the Eco 23/01 namespace.
    """

    local_name: str
    namespace: str = BaseTypeEco2301.namespace


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
class EndOfLifeFate(BaseTypeEco2301):
    """
    The fate of a material at the end-of-life of the product. For example if a material can be recycled, and what
    fraction of the total mass or volume can be recycled.
    """

    _simple_values = [("fraction", _QualifiedEco2301Name("Fraction"))]

    _props = [("MIRecordReference", "mi_end_of_life_reference", _QualifiedEco2301Name("MIEndOfLifeReference"))]

    mi_end_of_life_reference: MIRecordReference
    """Reference identifying the applicable fate within the MI Database."""

    fraction: float
    """Fraction of the total mass or volume of material to which this fate applies."""


@dataclass
class UnittedValue(BaseTypeEco2301):
    """
    A physical quantity with a unit. If provided in an input then the unit must exist within the MI database,
    otherwise an error will be raised.
    """

    _simple_values = [("value", _QualifiedEco2301Name("$")), ("unit", _QualifiedEco2301Name("@Unit"))]

    value: float
    """The value of the quantity in specified units."""

    unit: Optional[str] = None
    """If provided, specifies the unit symbol applying to the quantity. If absent the quantity will be treated as
    dimensionless."""


@dataclass
class Location(BaseTypeEco2301):
    """
    Defines the manufacturing location for the BoM for use in process calculations.
    """

    _props = [("MIRecordReference", "mi_location_reference", _QualifiedEco2301Name("MILocationReference"))]
    _simple_values = [
        ("identity", _QualifiedEco2301Name("Identity")),
        ("name", _QualifiedEco2301Name("Name")),
        ("external_identity", _QualifiedEco2301Name("ExternalIdentity")),
        ("internal_id", _QualifiedEco2301Name("@id")),
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
class ElectricityMix(BaseTypeEco2301):
    """
    If the product consumes electrical power, then the amount of CO2 produced to generate depends upon the mix of
    fossil fuel burning power stations in the region of use.  This type lets you specify the electrical generation
    mix by either specifying the region or country of use or by specifying the percentage of power that comes from
    fossil fuel sources.
    """

    _props = [("MIRecordReference", "mi_region_reference", _QualifiedEco2301Name("MIRegionReference"))]
    _simple_values = [("percentage_fossil_fuels", _QualifiedEco2301Name("PercentageFossilFuels"))]

    mi_region_reference: Optional[MIRecordReference] = None
    """Reference to a record in the MI database representing the electricity mix for the destination country."""

    percentage_fossil_fuels: Optional[float] = None
    """The percentage of electrical power production within the destination country that comes from fossil fuels."""


@dataclass
class MobileMode(BaseTypeEco2301):
    """
    If the product is transported as part of its use then this type contains details about the way in which it is
    transported.
    """

    _props = [
        ("MIRecordReference", "mi_transport_reference", _QualifiedEco2301Name("MITransportReference")),
        ("UnittedValue", "distance_travelled_per_day", _QualifiedEco2301Name("DistanceTravelledPerDay")),
    ]
    _simple_values = [("days_used_per_year", _QualifiedEco2301Name("DaysUsedPerYear"))]

    mi_transport_reference: MIRecordReference
    """Reference to a record in the MI database representing the means of transport for this product during use."""

    days_used_per_year: float
    """The number of days in a year the product will be transported during use."""

    distance_travelled_per_day: UnittedValue
    """The distance the product will be transported each day as part of its use."""


@dataclass
class StaticMode(BaseTypeEco2301):
    """
    Specifies the primary energy conversion that occurs during the product's use.
    """

    _props = [
        ("MIRecordReference", "mi_energy_conversion_reference", _QualifiedEco2301Name("MIEnergyConversionReference")),
        ("UnittedValue", "power_rating", _QualifiedEco2301Name("PowerRating")),
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
    def _process_custom_fields(cls, obj: Dict, bom_reader: _BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        usage_ref = _QualifiedEco2301Name("Usage")
        usage_obj = bom_reader.get_field(obj, usage_ref)
        if usage_obj is not None:
            hours_ref = _QualifiedEco2301Name("HoursUsedPerDay")
            days_ref = _QualifiedEco2301Name("DaysUsedPerYear")
            props["hours_used_per_day"] = bom_reader.get_field(usage_obj, hours_ref)
            props["days_used_per_year"] = bom_reader.get_field(usage_obj, days_ref)
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: _BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)
        usage_dict = {
            bom_writer._get_qualified_name(self, "DaysUsedPerYear"): self.days_used_per_year,
            bom_writer._get_qualified_name(self, "HoursUsedPerDay"): self.hours_used_per_day,
        }
        obj[bom_writer._get_qualified_name(self, "Usage")] = usage_dict


@dataclass
class UtilitySpecification(BaseTypeEco2301):
    """
    Specifies how much use can be obtained from the product represented by this BoM in comparison to a
    representative industry average.
    """

    _simple_values = [
        ("industry_average_duration_years", _QualifiedEco2301Name("IndustryAverageDurationYears")),
        (
            "industry_average_number_of_functional_units",
            _QualifiedEco2301Name("IndustryAverageNumberOfFunctionalUnits"),
        ),
        ("utility", _QualifiedEco2301Name("Utility")),
    ]

    industry_average_duration_years: Optional[float] = None
    """The average lifespan of all examples, throughout the industry, of the kind of product described herein."""

    industry_average_number_of_functional_units: Optional[float] = None
    """The average number of functional units delivered, in their lifespan, by all examples, throughout the
    industry, of the kind of product represented by this object."""

    utility: Optional[float] = None
    """Directly specifies the utility."""


@dataclass
class ProductLifeSpan(BaseTypeEco2301):
    """
    Specifies the average life span for the product represented by the BoM.
    """

    _props = [("UtilitySpecification", "utility", _QualifiedEco2301Name("Utility"))]
    _simple_values = [
        ("duration_years", _QualifiedEco2301Name("DurationYears")),
        ("number_of_functional_units", _QualifiedEco2301Name("NumberOfFunctionalUnits")),
        ("functional_unit_description", _QualifiedEco2301Name("FunctionalUnitDescription")),
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
class UsePhase(BaseTypeEco2301):
    """
    Provides information about the sustainability of the product whilst in use, including electricity use, emissions
    due to transport, emissions due to electricity consumption, and the expected life span of the product.
    """

    _props = [
        ("ProductLifeSpan", "product_life_span", _QualifiedEco2301Name("ProductLifeSpan")),
        ("ElectricityMix", "electricity_mix", _QualifiedEco2301Name("ElectricityMix")),
        ("StaticMode", "static_mode", _QualifiedEco2301Name("StaticMode")),
        ("MobileMode", "mobile_mode", _QualifiedEco2301Name("MobileMode")),
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
class BoMDetails(BaseTypeEco2301):
    """
    Explanatory information about a BoM.
    """

    _simple_values = [
        ("notes", _QualifiedEco2301Name("Notes")),
        ("picture_url", _QualifiedEco2301Name("PictureUrl")),
        ("product_name", _QualifiedEco2301Name("ProductName")),
    ]

    notes: Optional[str] = None
    """General notes for the BoM object."""

    picture_url: Optional[str] = None
    """The URL of an image to include at the top of the report. This URL must be accessible from the reporting
    services server."""

    product_name: Optional[str] = None
    """The product name."""


@dataclass
class TransportStage(BaseTypeEco2301):
    """
    Defines the transportation applied to an object, in terms of the generic transportation type (stored in the
    Database) and the amount of that transport used in this instance.
    """

    _props = [
        ("MIRecordReference", "mi_transport_reference", _QualifiedEco2301Name("MITransportReference")),
        ("UnittedValue", "distance", _QualifiedEco2301Name("Distance")),
    ]
    _simple_values = [("name", _QualifiedEco2301Name("Name")), ("internal_id", _QualifiedEco2301Name("@id"))]

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
class Specification(BaseTypeEco2301):
    """
    A specification for a surface treatment, part, process, or material. Refers to a record within the MI Database
    storing the details of the specification and its impact.
    """

    _props = [
        ("MIRecordReference", "mi_specification_reference", _QualifiedEco2301Name("MISpecificationReference")),
        ("UnittedValue", "quantity", _QualifiedEco2301Name("Quantity")),
    ]
    _simple_values = [
        ("identity", _QualifiedEco2301Name("Identity")),
        ("name", _QualifiedEco2301Name("Name")),
        ("external_identity", _QualifiedEco2301Name("ExternalIdentity")),
        ("internal_id", _QualifiedEco2301Name("@id")),
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
class Substance(BaseTypeEco2301):
    """
    A substance within a part, semi-finished part, material or specification. The substance is stored in the
    Database."""

    _simple_values = [
        ("percentage", _QualifiedEco2301Name("Percentage")),
        ("identity", _QualifiedEco2301Name("Identity")),
        ("name", _QualifiedEco2301Name("Name")),
        ("external_identity", _QualifiedEco2301Name("ExternalIdentity")),
        ("internal_id", _QualifiedEco2301Name("@id")),
    ]
    _props = [("MIRecordReference", "mi_substance_reference", _QualifiedEco2301Name("MISubstanceReference"))]

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
    def _process_custom_fields(cls, obj: Dict, bom_reader: _BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        category_ref = _QualifiedEco2301Name("Category")
        category_type_obj = bom_reader.get_field(obj, category_ref)
        if category_type_obj is not None:
            props["category"] = Category.from_string(category_type_obj)
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: _BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)

        if self.category is not None:
            category_field_name = bom_writer._get_qualified_name(self, "Category")
            obj[category_field_name] = self.category.to_string()


@dataclass
class Process(BaseTypeEco2301):
    """
    A process that is applied to a subassembly, part, semi-finished part or material. The process is stored in the
    Database.
    """

    _simple_values = [
        ("percentage", _QualifiedEco2301Name("Percentage")),
        ("identity", _QualifiedEco2301Name("Identity")),
        ("name", _QualifiedEco2301Name("Name")),
        ("external_identity", _QualifiedEco2301Name("ExternalIdentity")),
        ("internal_id", _QualifiedEco2301Name("@id")),
    ]

    _props = [
        ("MIRecordReference", "mi_process_reference", _QualifiedEco2301Name("MIProcessReference")),
        ("UnittedValue", "quantity", _QualifiedEco2301Name("Quantity")),
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
    def _process_custom_fields(cls, obj: Dict, bom_reader: _BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        dimension_type_ref = _QualifiedEco2301Name("DimensionType")
        dimension_type_obj = bom_reader.get_field(obj, dimension_type_ref)
        props["dimension_type"] = DimensionType.from_string(dimension_type_obj)
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: _BoMWriter) -> None:
        super()._write_custom_fields(obj, bom_writer)

        dimension_field_name = bom_writer._get_qualified_name(self, "DimensionType")
        obj[dimension_field_name] = self.dimension_type.to_string()


@dataclass
class Material(BaseTypeEco2301):
    """
    A Material within a part or semi-finished part. The material is stored in the Database.
    """

    _simple_values = [
        ("percentage", _QualifiedEco2301Name("Percentage")),
        ("identity", _QualifiedEco2301Name("Identity")),
        ("name", _QualifiedEco2301Name("Name")),
        ("external_identity", _QualifiedEco2301Name("ExternalIdentity")),
        ("internal_id", _QualifiedEco2301Name("@id")),
    ]

    _props = [
        ("MIRecordReference", "mi_material_reference", _QualifiedEco2301Name("MIMaterialReference")),
        ("UnittedValue", "mass", _QualifiedEco2301Name("Mass")),
    ]

    _list_props = [
        ("Process", "processes", _QualifiedEco2301Name("Processes"), _QualifiedEco2301Name("Process")),
        (
            "EndOfLifeFate",
            "end_of_life_fates",
            _QualifiedEco2301Name("EndOfLifeFates"),
            _QualifiedEco2301Name("EndOfLifeFate"),
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
    def _process_custom_fields(cls, obj: Dict, bom_reader: _BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)

        recycle_content_ref = _QualifiedEco2301Name("RecycleContent")
        recycle_content_obj = bom_reader.get_field(obj, recycle_content_ref)
        if recycle_content_obj is not None:
            # TODO support recycle content (issue #95)
            # typical_obj = bom_reader.get_field(Material, recycle_content_obj, "Typical")
            # if typical_obj is not None:
            #     props["recycle_content_is_typical"] = typical_obj
            percentage_ref = _QualifiedEco2301Name("Percentage")
            percentage_obj = bom_reader.get_field(recycle_content_obj, percentage_ref)
            if percentage_obj is not None:
                props["recycle_content_percentage"] = percentage_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: _BoMWriter) -> None:
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
class Part(BaseTypeEco2301):
    """
    A single part which may or may not be stored in the MI Database.
    """

    _props = [
        ("UnittedValue", "quantity", _QualifiedEco2301Name("Quantity")),
        ("UnittedValue", "mass_per_unit_of_measure", _QualifiedEco2301Name("MassPerUom")),
        ("UnittedValue", "volume_per_unit_of_measure", _QualifiedEco2301Name("VolumePerUom")),
        ("MIRecordReference", "mi_part_reference", _QualifiedEco2301Name("MIPartReference")),
    ]

    _simple_values = [
        ("part_number", _QualifiedEco2301Name("PartNumber")),
        ("part_name", _QualifiedEco2301Name("Name")),
        ("external_identity", _QualifiedEco2301Name("ExternalIdentity")),
        ("internal_id", _QualifiedEco2301Name("@id")),
    ]

    _list_props = [
        ("Part", "components", _QualifiedEco2301Name("Components"), _QualifiedEco2301Name("Part")),
        (
            "Specification",
            "specifications",
            _QualifiedEco2301Name("Specifications"),
            _QualifiedEco2301Name("Specification"),
        ),
        ("Material", "materials", _QualifiedEco2301Name("Materials"), _QualifiedEco2301Name("Material")),
        ("Substance", "substances", _QualifiedEco2301Name("Substances"), _QualifiedEco2301Name("Substance")),
        ("Process", "processes", _QualifiedEco2301Name("Processes"), _QualifiedEco2301Name("Process")),
        (
            "EndOfLifeFate",
            "end_of_life_fates",
            _QualifiedEco2301Name("EndOfLifeFates"),
            _QualifiedEco2301Name("EndOfLifeFate"),
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
    def _process_custom_fields(cls, obj: Dict, bom_reader: _BoMReader) -> Dict[str, Any]:
        props = super()._process_custom_fields(obj, bom_reader)
        # TODO support non_mi_part_reference (issue #95)
        # non_mi_part_ref_obj = bom_reader.get_field(Part, obj, "NonMIPartReference")
        # if non_mi_part_ref_obj is not None:
        #     props["non_mi_part_reference"] = non_mi_part_ref_obj
        rohs_exemptions_ref = _QualifiedEco2301Name("RohsExemptions")
        rohs_exemptions_obj = bom_reader.get_field(obj, rohs_exemptions_ref)
        if rohs_exemptions_obj is not None:
            rohs_exemption_ref = _QualifiedEco2301Name("RohsExemption")
            rohs_exemption_obj = bom_reader.get_field(rohs_exemptions_obj, rohs_exemption_ref)
            if rohs_exemption_obj is not None:
                props["rohs_exemptions"] = rohs_exemption_obj
        return props

    def _write_custom_fields(self, obj: Dict, bom_writer: _BoMWriter) -> None:
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
# class AnnotationSource(BaseType2301):
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
#     def _process_custom_fields(cls, obj: Dict, bom_reader: _BoMReader) -> Dict[str, Any]:
#         props = super()._process_custom_fields(obj, bom_reader)
#
#         data_obj = bom_reader.get_field(AnnotationSource, obj, "Data")
#         if data_obj is not None:
#             props["data"] = data_obj
#         return props
#
#     def _write_custom_fields(self, obj: Dict, bom_writer: _BoMWriter) -> None:
#         if len(self.data) > 0:
#             data_field_name = bom_writer._get_qualified_name(self, "Data")
#             obj[data_field_name] = self.data
#
#
# @dataclass
# class Annotation(BaseType2301):
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
class BillOfMaterials(BaseTypeEco2301):
    """
    Type representing the root Bill of Materials object.
    """

    _simple_values = [("internal_id", _QualifiedEco2301Name("@id"))]
    _props = [
        ("UsePhase", "use_phase", _QualifiedEco2301Name("UsePhase")),
        ("Location", "location", _QualifiedEco2301Name("Location")),
        ("BoMDetails", "notes", _QualifiedEco2301Name("Notes")),
    ]
    _list_props = [
        ("Part", "components", _QualifiedEco2301Name("Components"), _QualifiedEco2301Name("Part")),
        (
            "TransportStage",
            "transport_phase",
            _QualifiedEco2301Name("TransportPhase"),
            _QualifiedEco2301Name("TransportStage"),
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
