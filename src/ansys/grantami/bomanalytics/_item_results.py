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

"""BoM Analytics BoM item result definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are returned from
queries. These are mostly extensions of the classes in the ``_item_definitions.py`` file.
"""

from abc import ABC
from copy import deepcopy
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ansys.grantami.bomanalytics_openapi.v2 import models
from ansys.openapi.common import Unset, Unset_Type

from ._item_definitions import (
    CoatingReference,
    MaterialReference,
    PartReference,
    ProcessReference,
    RecordReference,
    ReferenceType,
    SpecificationReference,
    SubstanceReference,
    TransportReference,
)
from ._typing import _convert_unset_to_none, _raise_if_empty

if TYPE_CHECKING:
    from .indicators import RoHSIndicator, WatchListIndicator

Indicator_Definitions = Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]


class TransportCategory(Enum):
    """The stage of the product lifecycle to which a :class:`.TransportSummaryByPartResult` belongs.

    :class:`~enum.Enum` class.

    .. versionadded:: 2.3
    """

    MANUFACTURING = "Manufacturing"
    """Transportation of individual components before the product is completed."""

    DISTRIBUTION = "Distribution"
    """Transportation of the complete finished product."""


class ItemResultFactory:
    """Creates item results for a given type of API query."""

    @classmethod
    def create_material_impacted_substances_result(
        cls, result_with_impacted_substances: models.GetImpactedSubstancesForMaterialsMaterial
    ) -> "MaterialWithImpactedSubstancesResult":
        """
        Return a material impacted substances result.

        Parameters
        ----------
        result_with_impacted_substances
           Result from the REST API describing the impacted substances for a material.

        Returns
        -------
        MaterialWithImpactedSubstancesResult
           An object that describes the substances that impacted a material. Substances are grouped by legislation.
        """
        reference_type = cls.parse_reference_type(result_with_impacted_substances.reference_type)
        equivalent_references = (
            [
                MaterialReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_impacted_substances.equivalent_references
            ]
            if result_with_impacted_substances.equivalent_references
            else None
        )

        item_result = MaterialWithImpactedSubstancesResult(
            reference_type=reference_type,
            reference_value=result_with_impacted_substances.reference_value,
            database_key=_convert_unset_to_none(result_with_impacted_substances.database_key),
            legislations=_raise_if_empty(result_with_impacted_substances.legislations),
            identity=result_with_impacted_substances.id,
            external_identity=result_with_impacted_substances.external_identity,
            name=result_with_impacted_substances.name,
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_part_impacted_substances_result(
        cls, result_with_impacted_substances: models.GetImpactedSubstancesForPartsPart
    ) -> "PartWithImpactedSubstancesResult":
        """
        Return a part impacted substances result.

        Parameters
        ----------
        result_with_impacted_substances
           Result from the REST API describing the impacted substances for a part.

        Returns
        -------
        PartWithImpactedSubstancesResult
           An object that describes the substances that impacted a part. Substances are grouped by legislation.
        """
        reference_type = cls.parse_reference_type(result_with_impacted_substances.reference_type)
        equivalent_references = (
            [
                PartReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_impacted_substances.equivalent_references
            ]
            if result_with_impacted_substances.equivalent_references
            else None
        )

        item_result = PartWithImpactedSubstancesResult(
            reference_type=reference_type,
            reference_value=result_with_impacted_substances.reference_value,
            database_key=_convert_unset_to_none(result_with_impacted_substances.database_key),
            legislations=_raise_if_empty(result_with_impacted_substances.legislations),
            identity=result_with_impacted_substances.id,
            external_identity=result_with_impacted_substances.external_identity,
            name=result_with_impacted_substances.name,
            input_part_number=result_with_impacted_substances.input_part_number,
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_specification_impacted_substances_result(
        cls, result_with_impacted_substances: models.GetImpactedSubstancesForSpecificationsSpecification
    ) -> "SpecificationWithImpactedSubstancesResult":
        """
        Return a specification impacted substances result.

        Parameters
        ----------
        result_with_impacted_substances
           Result from the REST API describing the impacted substances for a specification.

        Returns
        -------
        SpecificationWithImpactedSubstancesResult
           An object that describes the substances that impacted a specification. Substances are grouped by legislation.
        """
        reference_type = cls.parse_reference_type(result_with_impacted_substances.reference_type)
        equivalent_references = (
            [
                SpecificationReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_impacted_substances.equivalent_references
            ]
            if result_with_impacted_substances.equivalent_references
            else None
        )

        item_result = SpecificationWithImpactedSubstancesResult(
            reference_type=reference_type,
            reference_value=result_with_impacted_substances.reference_value,
            database_key=_convert_unset_to_none(result_with_impacted_substances.database_key),
            legislations=_raise_if_empty(result_with_impacted_substances.legislations),
            identity=result_with_impacted_substances.id,
            external_identity=result_with_impacted_substances.external_identity,
            name=result_with_impacted_substances.name,
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_bom_impacted_substances_result(
        cls, result_with_impacted_substances: models.GetImpactedSubstancesForBomResponse
    ) -> "BoMWithImpactedSubstancesResult":
        """
        Return a bom impacted substances result.

        Parameters
        ----------
        result_with_impacted_substances
           Result from the REST API describing the impacted substances for a bom.

        Returns
        -------
        BoMWithImpactedSubstancesResult
           An object that describes the substances that impacted a bom. Substances are grouped by legislation.
        """
        item_result = BoMWithImpactedSubstancesResult(
            legislations=_raise_if_empty(result_with_impacted_substances.legislations)
        )
        return item_result

    @classmethod
    def create_material_compliance_result(
        cls,
        result_with_compliance: models.CommonMaterialWithCompliance,
        indicator_definitions: Indicator_Definitions,
    ) -> "MaterialWithComplianceResult":
        """Returns a material compliance result.

        Parameters
        ----------
        result_with_compliance
            Result from the REST API describing the compliance for this particular material.
        indicator_definitions
            Definitions of the indicators supplied to the original query. This is required because
            the REST API does not provide them in the response.

        Returns
        -------
        MaterialWithComplianceResult
            An object that describes the compliance of the material.
            This object is defined recursively, with each level of the BoM having a reported compliance
            status for each indicator.
        """
        reference_type = cls.parse_reference_type(result_with_compliance.reference_type)
        equivalent_references = (
            [
                MaterialReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_compliance.equivalent_references
            ]
            if result_with_compliance.equivalent_references
            else None
        )

        item_result = MaterialWithComplianceResult(
            reference_type=reference_type,
            reference_value=result_with_compliance.reference_value,
            database_key=_convert_unset_to_none(result_with_compliance.database_key),
            indicator_results=result_with_compliance.indicators,
            indicator_definitions=indicator_definitions,
            identity=result_with_compliance.id,
            external_identity=result_with_compliance.external_identity,
            name=result_with_compliance.name,
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_part_compliance_result(
        cls,
        result_with_compliance: models.CommonPartWithCompliance,
        indicator_definitions: Indicator_Definitions,
    ) -> "PartWithComplianceResult":
        """Returns a part compliance result.

        Parameters
        ----------
        result_with_compliance
            Result from the REST API describing the compliance for this particular part.
        indicator_definitions
            Definitions of the indicators supplied to the original query. This is required because
            the REST API does not provide them in the response.

        Returns
        -------
        PartWithComplianceResult
            An object that describes the compliance of the part.
            This object is defined recursively, with each level of the BoM having a reported compliance
            status for each indicator.
        """
        reference_type = cls.parse_reference_type(result_with_compliance.reference_type)
        equivalent_references = (
            [
                PartReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_compliance.equivalent_references
            ]
            if result_with_compliance.equivalent_references
            else None
        )

        item_result = PartWithComplianceResult(
            reference_type=reference_type,
            reference_value=result_with_compliance.reference_value,
            database_key=_convert_unset_to_none(result_with_compliance.database_key),
            indicator_results=result_with_compliance.indicators,
            indicator_definitions=indicator_definitions,
            identity=result_with_compliance.id,
            external_identity=result_with_compliance.external_identity,
            name=result_with_compliance.name,
            input_part_number=result_with_compliance.input_part_number,
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_specification_compliance_result(
        cls,
        result_with_compliance: models.CommonSpecificationWithCompliance,
        indicator_definitions: Indicator_Definitions,
    ) -> "SpecificationWithComplianceResult":
        """Returns a specification compliance result.

        Parameters
        ----------
        result_with_compliance
            Result from the REST API describing the compliance for this particular specification.
        indicator_definitions
            Definitions of the indicators supplied to the original query. This is required because
            the REST API does not provide them in the response.

        Returns
        -------
        SpecificationWithComplianceResult
            An object that describes the compliance of the specification.
            This object is defined recursively, with each level of the BoM having a reported compliance
            status for each indicator.
        """
        reference_type = cls.parse_reference_type(result_with_compliance.reference_type)
        equivalent_references = (
            [
                SpecificationReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_compliance.equivalent_references
            ]
            if result_with_compliance.equivalent_references
            else None
        )

        item_result = SpecificationWithComplianceResult(
            reference_type=reference_type,
            reference_value=result_with_compliance.reference_value,
            database_key=_convert_unset_to_none(result_with_compliance.database_key),
            indicator_results=result_with_compliance.indicators,
            indicator_definitions=indicator_definitions,
            identity=result_with_compliance.id,
            external_identity=result_with_compliance.external_identity,
            name=result_with_compliance.name,
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_coating_compliance_result(
        cls,
        result_with_compliance: models.CommonCoatingWithCompliance,
        indicator_definitions: Indicator_Definitions,
    ) -> "CoatingWithComplianceResult":
        """Returns a coating compliance result.

        Parameters
        ----------
        result_with_compliance
            Result from the REST API describing the compliance for this particular coating.
        indicator_definitions
            Definitions of the indicators supplied to the original query. This is required because
            the REST API does not provide them in the response.

        Returns
        -------
        CoatingWithComplianceResult
            An object that describes the compliance of the coating.
            This object is defined recursively, with each level of the BoM having a reported compliance
            status for each indicator.
        """
        reference_type = cls.parse_reference_type(result_with_compliance.reference_type)
        equivalent_references = (
            [
                CoatingReference(
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=_convert_unset_to_none(ref.id),
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_compliance.equivalent_references
            ]
            if result_with_compliance.equivalent_references
            else None
        )

        item_result = CoatingWithComplianceResult(
            reference_type=reference_type,
            reference_value=result_with_compliance.reference_value,
            database_key=_convert_unset_to_none(result_with_compliance.database_key),
            indicator_results=result_with_compliance.indicators,
            indicator_definitions=indicator_definitions,
            identity=result_with_compliance.id,
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_substance_compliance_result(
        cls,
        result_with_compliance: models.CommonSubstanceWithCompliance,
        indicator_definitions: Indicator_Definitions,
    ) -> "SubstanceWithComplianceResult":
        """Returns a substance compliance result.

        Parameters
        ----------
        result_with_compliance
            Result from the REST API describing the compliance for this particular substance.
        indicator_definitions
            Definitions of the indicators supplied to the original query. This is required because
            the REST API does not provide them in the response.

        Returns
        -------
        SubstanceWithComplianceResult
            An object that describes the compliance of the substance.
            This object is defined recursively, with each level of the BoM having a reported compliance
            status for each indicator.
        """
        reference_type = cls.parse_reference_type(result_with_compliance.reference_type)
        equivalent_references = (
            [
                SubstanceReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_compliance.equivalent_references
            ]
            if result_with_compliance.equivalent_references
            else None
        )

        item_result = SubstanceWithComplianceResult(
            reference_type=reference_type,
            reference_value=result_with_compliance.reference_value,
            database_key=_convert_unset_to_none(result_with_compliance.database_key),
            indicator_results=_raise_if_empty(result_with_compliance.indicators),
            indicator_definitions=indicator_definitions,
            identity=result_with_compliance.id,
            external_identity=result_with_compliance.external_identity,
            name=result_with_compliance.name,
            percentage_amount=_convert_unset_to_none(result_with_compliance.percentage_amount),
            equivalent_references=equivalent_references,
        )
        return item_result

    @classmethod
    def create_part_with_sustainability(
        cls,
        result_with_sustainability: models.CommonSustainabilityPartWithSustainability,
    ) -> "PartWithSustainabilityResult":
        """Returns a Part object with sustainability metrics and child items.

        Parameters
        ----------
        result_with_sustainability: models.CommonSustainabilityPartWithSustainability
            Result from the REST API describing the sustainability for this particular part.

        Returns
        -------
        PartWithSustainabilityResult
        """

        reference_type = cls.parse_reference_type(result_with_sustainability.reference_type)
        equivalent_references = (
            [
                PartReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_sustainability.equivalent_references
            ]
            if result_with_sustainability.equivalent_references
            else None
        )

        part_with_sustainability = PartWithSustainabilityResult(
            reference_type=reference_type,
            reference_value=result_with_sustainability.reference_value,
            database_key=_convert_unset_to_none(result_with_sustainability.database_key),
            embodied_energy=cls.create_unitted_value(result_with_sustainability.embodied_energy),
            climate_change=cls.create_unitted_value(result_with_sustainability.climate_change),
            reported_mass=cls.create_unitted_value(result_with_sustainability.reported_mass),
            identity=result_with_sustainability.id,
            external_identity=result_with_sustainability.external_identity,
            name=result_with_sustainability.name,
            input_part_number=result_with_sustainability.input_part_number,
            equivalent_references=equivalent_references,
        )
        part_with_sustainability._add_child_parts(_raise_if_empty(result_with_sustainability.parts))
        part_with_sustainability._add_child_materials(_raise_if_empty(result_with_sustainability.materials))
        part_with_sustainability._add_child_processes(_raise_if_empty(result_with_sustainability.processes))

        # transport_stages is optional, only returned by BAS 2025 R2 and later
        if result_with_sustainability.transport_stages:
            part_with_sustainability._add_child_transport_stages(result_with_sustainability.transport_stages)
        return part_with_sustainability

    @classmethod
    def create_process_with_sustainability(
        cls,
        result_with_sustainability: models.CommonSustainabilityProcessWithSustainability,
    ) -> "ProcessWithSustainabilityResult":
        """Returns a Process object with sustainability metrics.

        Parameters
        ----------
        result_with_sustainability: models.CommonSustainabilityProcessWithSustainability
            Result from the REST API describing the sustainability for this particular process.

        Returns
        -------
        ProcessWithSustainabilityResult
        """

        reference_type = cls.parse_reference_type(result_with_sustainability.reference_type)
        equivalent_references = (
            [
                ProcessReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_sustainability.equivalent_references
            ]
            if result_with_sustainability.equivalent_references
            else None
        )

        process_with_sustainability = ProcessWithSustainabilityResult(
            reference_type=reference_type,
            reference_value=result_with_sustainability.reference_value,
            database_key=_convert_unset_to_none(result_with_sustainability.database_key),
            embodied_energy=cls.create_unitted_value(result_with_sustainability.embodied_energy),
            climate_change=cls.create_unitted_value(result_with_sustainability.climate_change),
            identity=result_with_sustainability.id,
            external_identity=result_with_sustainability.external_identity,
            name=result_with_sustainability.name,
            equivalent_references=equivalent_references,
        )

        # transport_stages is optional, only returned by BAS 2025 R2 and later
        if result_with_sustainability.transport_stages:
            process_with_sustainability._add_child_transport_stages(result_with_sustainability.transport_stages)
        return process_with_sustainability

    @classmethod
    def create_material_with_sustainability(
        cls,
        result_with_sustainability: models.CommonSustainabilityMaterialWithSustainability,
    ) -> "MaterialWithSustainabilityResult":
        """Returns a Material object with sustainability metrics and child items.

        Parameters
        ----------
        result_with_sustainability: models.CommonSustainabilityMaterialWithSustainability
            Result from the REST API describing the sustainability for this particular material.

        Returns
        -------
        MaterialWithSustainabilityResult
        """

        reference_type = cls.parse_reference_type(result_with_sustainability.reference_type)
        equivalent_references = (
            [
                MaterialReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_sustainability.equivalent_references
            ]
            if result_with_sustainability.equivalent_references
            else None
        )

        material_with_sustainability = MaterialWithSustainabilityResult(
            reference_type=reference_type,
            reference_value=result_with_sustainability.reference_value,
            database_key=_convert_unset_to_none(result_with_sustainability.database_key),
            embodied_energy=cls.create_unitted_value(result_with_sustainability.embodied_energy),
            climate_change=cls.create_unitted_value(result_with_sustainability.climate_change),
            reported_mass=cls.create_unitted_value(result_with_sustainability.reported_mass),
            recyclable=result_with_sustainability.recyclable,
            biodegradable=result_with_sustainability.biodegradable,
            functional_recycle=result_with_sustainability.functional_recycle,
            identity=result_with_sustainability.id,
            external_identity=result_with_sustainability.external_identity,
            name=result_with_sustainability.name,
            equivalent_references=equivalent_references,
        )
        material_with_sustainability._add_child_processes(_raise_if_empty(result_with_sustainability.processes))
        return material_with_sustainability

    @classmethod
    def create_transport_with_sustainability(
        cls,
        result_with_sustainability: models.CommonSustainabilityTransportWithSustainability,
    ) -> "TransportWithSustainabilityResult":
        """Returns a Transport object with sustainability metrics.

        Parameters
        ----------
        result_with_sustainability: models.CommonSustainabilityTransportWithSustainability
            Result from the REST API describing the sustainability for this particular transport stage.

        Returns
        -------
        TransportWithSustainabilityResult
        """

        reference_type = cls.parse_reference_type(result_with_sustainability.reference_type)
        equivalent_references = (
            [
                TransportReference(
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=_convert_unset_to_none(ref.id),
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in result_with_sustainability.equivalent_references
            ]
            if result_with_sustainability.equivalent_references
            else None
        )

        transport_with_sustainability = TransportWithSustainabilityResult(
            reference_type=reference_type,
            reference_value=result_with_sustainability.reference_value,
            database_key=_convert_unset_to_none(result_with_sustainability.database_key),
            embodied_energy=cls.create_unitted_value(result_with_sustainability.embodied_energy),
            climate_change=cls.create_unitted_value(result_with_sustainability.climate_change),
            identity=result_with_sustainability.id,
            name=_raise_if_empty(result_with_sustainability.stage_name),
            equivalent_references=equivalent_references,
        )
        return transport_with_sustainability

    @classmethod
    def create_unitted_value(cls, result: Union[models.CommonValueWithUnit, Unset_Type]) -> "ValueWithUnit":
        """Returns a value with unit.

        Parameters
        ----------
        result: models.CommonValueWithUnit or Unset_Type
            Result from the REST API describing the value and unit.

        Returns
        -------
        ValueWithUnit
        """
        valid_result = _raise_if_empty(result)
        return ValueWithUnit(value=valid_result.value, unit=valid_result.unit)  # type: ignore[arg-type]

    @classmethod
    def create_phase_summary(
        cls, result: models.CommonSustainabilityPhaseSummary
    ) -> "SustainabilityPhaseSummaryResult":
        """Returns a SustainabilityPhaseSummaryResult instantiated from the low-level API model.

        Parameters
        ----------
        result: models.CommonSustainabilityPhaseSummary
            Result from the REST API describing the sustainability metrics for a particular phase.

        Returns
        -------
        SustainabilityPhaseSummaryResult
        """
        return SustainabilityPhaseSummaryResult(
            name=_raise_if_empty(result.phase),
            embodied_energy=cls.create_unitted_value(result.embodied_energy),
            embodied_energy_percentage=result.embodied_energy_percentage,
            climate_change=cls.create_unitted_value(result.climate_change),
            climate_change_percentage=result.climate_change_percentage,
        )

    @classmethod
    def create_transport_summary(
        cls, result: models.CommonSustainabilityTransportSummaryEntry
    ) -> "TransportSummaryResult":
        """Returns a TransportSummaryResult instantiated from the low-level API model.

        Parameters
        ----------
        result: models.CommonSustainabilityTransportSummaryEntry
            Result from the REST API describing the sustainability metrics for a transport stage.

        Returns
        -------
        TransportSummaryResult
        """
        record_reference = _raise_if_empty(result.record_reference)
        reference_type = cls.parse_reference_type(record_reference.reference_type)
        equivalent_references = (
            [
                TransportReference(
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    database_key=_convert_unset_to_none(ref.database_key),
                    identity=_convert_unset_to_none(ref.id),
                )
                for ref in record_reference.equivalent_references
            ]
            if record_reference.equivalent_references
            else None
        )

        return TransportSummaryResult(
            transport_reference=TransportReference(
                reference_type=reference_type,
                reference_value=record_reference.reference_value,
                identity=record_reference.id,
                database_key=_convert_unset_to_none(record_reference.database_key),
                equivalent_references=equivalent_references,
            ),
            name=_convert_unset_to_none(result.stage_name),
            distance=cls.create_unitted_value(result.distance),
            embodied_energy=cls.create_unitted_value(result.embodied_energy),
            embodied_energy_percentage=_raise_if_empty(result.embodied_energy_percentage),
            climate_change=cls.create_unitted_value(result.climate_change),
            climate_change_percentage=_raise_if_empty(result.climate_change_percentage),
        )

    @classmethod
    def create_transport_summary_by_category(
        cls, result: models.CommonSustainabilityTransportByCategorySummaryEntry
    ) -> "TransportSummaryByCategoryResult":
        """Returns a TransportSummaryByCategoryResult instantiated from the low-level API model.

        Parameters
        ----------
        result: models.CommonSustainabilityTransportByCategorySummaryEntry
            Result from the REST API describing the sustainability metrics for all transport stages in a category.

        Returns
        -------
        TransportSummaryByCategoryResult
        """
        return TransportSummaryByCategoryResult(
            distance=cls.create_unitted_value(result.distance),
            embodied_energy=cls.create_unitted_value(result.embodied_energy),
            embodied_energy_percentage=_raise_if_empty(result.embodied_energy_percentage),
            climate_change=cls.create_unitted_value(result.climate_change),
            climate_change_percentage=_raise_if_empty(result.climate_change_percentage),
        )

    @classmethod
    def create_transport_summary_by_part(
        cls, result: models.CommonSustainabilityTransportByPartSummaryEntry
    ) -> "TransportSummaryByPartResult":
        """Returns a TransportSummaryByPartResult instantiated from the low-level API model.

        Parameters
        ----------
        result: models.CommonSustainabilityTransportByPartSummaryEntry
            Result from the REST API describing the sustainability metrics for all transport stages associated with a
            part.

        Returns
        -------
        TransportSummaryByPartResult
        """

        # BAS does not support nullable enums in server responses, so NotApplicable is used to indicate that
        # the category should be null.
        if result.category == "NotApplicable":
            category = None
        else:
            category = TransportCategory(result.category)
        return TransportSummaryByPartResult(
            distance=cls.create_unitted_value(result.distance),
            embodied_energy=cls.create_unitted_value(result.embodied_energy),
            embodied_energy_percentage=_raise_if_empty(result.embodied_energy_percentage),
            climate_change=cls.create_unitted_value(result.climate_change),
            climate_change_percentage=_raise_if_empty(result.climate_change_percentage),
            parent_part_name=_convert_unset_to_none(result.parent_part_name),
            part_name=_convert_unset_to_none(result.part_name),
            transport_types=set(_raise_if_empty(result.transport_types)),
            category=category,
        )

    @classmethod
    def create_material_summary(
        cls, result: models.CommonSustainabilityMaterialSummaryEntry
    ) -> "MaterialSummaryResult":
        """Returns a MaterialSummaryResult instantiated from the low-level API model.

        Parameters
        ----------
        result: models.CommonSustainabilityMaterialSummaryEntry
            Result from the REST API describing the sustainability metrics for a unique material aggregated for the
            whole BoM.

        Returns
        -------
        MaterialSummaryResult
        """
        # TODO one of these is a bucket for all other materials that do not contribute >2% EE. Worth separating it?
        #  It does not have a valid record reference or contributors.
        record_reference = _raise_if_empty(result.record_reference)
        reference_type = cls.parse_reference_type(record_reference.reference_type)
        equivalent_references = (
            [
                MaterialReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in record_reference.equivalent_references
            ]
            if record_reference.equivalent_references
            else None
        )

        return MaterialSummaryResult(
            material_reference=MaterialReference(
                external_identity=_convert_unset_to_none(record_reference.external_identity),
                name=_convert_unset_to_none(record_reference.name),
                reference_type=reference_type,
                reference_value=record_reference.reference_value,
                identity=record_reference.id,
                database_key=_convert_unset_to_none(record_reference.database_key),
                equivalent_references=equivalent_references,
            ),
            identity=_raise_if_empty(result.identity),
            embodied_energy=cls.create_unitted_value(result.embodied_energy),
            embodied_energy_percentage=_raise_if_empty(result.embodied_energy_percentage),
            climate_change=cls.create_unitted_value(result.climate_change),
            climate_change_percentage=_raise_if_empty(result.climate_change_percentage),
            mass_after_processing=cls.create_unitted_value(result.mass_after_processing),
            mass_before_processing=cls.create_unitted_value(result.mass_before_processing),
            contributors=(
                [cls.create_contributing_component(component) for component in result.largest_contributors]
                if result.largest_contributors
                else []
            ),
        )

    @classmethod
    def create_contributing_component(
        cls, result: models.CommonSustainabilityMaterialContributingComponent
    ) -> "ContributingComponentResult":
        """Returns a ContributingComponentResult instantiated from the low-level API model.

        Parameters
        ----------
        result: models.CommonSustainabilityMaterialContributingComponent
            Result from the REST API describing parts contributing the most to a material's environmental footprint.

        Returns
        -------
        ContributingComponentResult
        """
        record_reference = _raise_if_empty(result.record_reference)
        reference_type = cls.parse_reference_type(record_reference.reference_type)
        equivalent_references = (
            [
                PartReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in record_reference.equivalent_references
            ]
            if record_reference.equivalent_references
            else None
        )

        return ContributingComponentResult(
            part_number=_convert_unset_to_none(result.component_part_number),
            part_reference=PartReference(
                external_identity=_convert_unset_to_none(record_reference.external_identity),
                name=_convert_unset_to_none(record_reference.name),
                reference_type=reference_type,
                reference_value=record_reference.reference_value,
                identity=record_reference.id,
                database_key=_convert_unset_to_none(record_reference.database_key),
                equivalent_references=equivalent_references,
            ),
            material_mass_before_processing=cls.create_unitted_value(result.material_mass_before_processing),
            name=_convert_unset_to_none(result.component_name),
        )

    @classmethod
    def create_process_summary(cls, result: models.CommonSustainabilityProcessSummaryEntry) -> "ProcessSummaryResult":
        """Returns a ProcessSummaryResult instantiated from the low-level API model.

        Parameters
        ----------
        result: models.CommonSustainabilityProcessSummaryEntry
            Result from the REST API describing the sustainability metrics for a unique process-material pair,
            aggregated for the whole BoM.

        Returns
        -------
        ProcessSummaryResult
        """
        material_record_reference = _raise_if_empty(result.material_record_reference)
        material_reference = (
            MaterialReference(
                external_identity=_convert_unset_to_none(material_record_reference.external_identity),
                name=_convert_unset_to_none(material_record_reference.name),
                reference_type=cls.parse_reference_type(material_record_reference.reference_type),
                reference_value=material_record_reference.reference_value,
                identity=material_record_reference.id,
                database_key=_convert_unset_to_none(material_record_reference.database_key),
            )
            if material_record_reference.reference_type is not Unset
            else None
        )
        if material_reference and material_record_reference.equivalent_references:
            material_reference._equivalent_references = [
                MaterialReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in material_record_reference.equivalent_references
            ]

        process_record_reference = _raise_if_empty(result.process_record_reference)
        process_reference = ProcessReference(
            external_identity=_convert_unset_to_none(process_record_reference.external_identity),
            name=_convert_unset_to_none(process_record_reference.name),
            reference_type=cls.parse_reference_type(process_record_reference.reference_type),
            reference_value=process_record_reference.reference_value,
            identity=process_record_reference.id,
            database_key=_convert_unset_to_none(process_record_reference.database_key),
        )
        if process_reference and process_record_reference.equivalent_references:
            process_reference._equivalent_references = [
                ProcessReference(
                    external_identity=_convert_unset_to_none(ref.external_identity),
                    name=_convert_unset_to_none(ref.name),
                    reference_type=cls.parse_reference_type(ref.reference_type),
                    reference_value=ref.reference_value,
                    identity=ref.id,
                    database_key=_convert_unset_to_none(ref.database_key),
                )
                for ref in process_record_reference.equivalent_references
            ]

        return ProcessSummaryResult(
            material_identity=_convert_unset_to_none(result.material_identity),
            material_reference=material_reference,
            process_name=_raise_if_empty(result.process_name),
            process_reference=process_reference,
            embodied_energy=cls.create_unitted_value(result.embodied_energy),
            embodied_energy_percentage=_convert_unset_to_none(result.embodied_energy_percentage),
            climate_change=cls.create_unitted_value(result.climate_change),
            climate_change_percentage=_convert_unset_to_none(result.climate_change_percentage),
        )

    @staticmethod
    def parse_reference_type(reference_type: Union[str, Unset_Type, None]) -> Optional[ReferenceType]:
        """Parse the ``reference_type`` returned by the low-level API into a ``ReferenceType``.

        Parameters
        ----------
        reference_type
            Type of record reference returned from the API for a result.

        Returns
        -------
        ReferenceType
            Specific enum value for the ``reference_type`` string.

        Raises
        ------
        KeyError
            Error to raise if the ``reference_type`` returned by the low-level API doesn't appear in ``ReferenceType``.
        """

        if isinstance(reference_type, Unset_Type) or reference_type is None:
            return None
        try:
            return ReferenceType[reference_type]
        except KeyError as e:
            raise KeyError(f"Unknown reference_type {reference_type} " f"returned.").with_traceback(e.__traceback__)

    @staticmethod
    def create_licensing_result(result: models.GetAvailableLicensesResponse) -> "Licensing":
        return Licensing(
            restricted_substances=_raise_if_empty(result.restricted_substances),
            sustainability=_raise_if_empty(result.sustainability),
        )


class ImpactedSubstance(SubstanceReference):
    """Represents a substance impacted by a legislation.

    This object includes two categories of attributes:

    * The reference to the substance in Granta MI. These attributes are all populated if data for them exists in
      Granta MI.
    * The amount of the substance in the parent item and the threshold above which it is impacted.

    Examples
    --------
    >>> result: MaterialImpactedSubstancesQueryResult
    >>> substance = result.impacted_substances[4]
    >>> print(f"{substance.cas_number}: {substance.max_percentage_amount_in_material}")
    1333-86-4: 20.0 %
    """

    def __init__(
        self,
        reference_type: Optional[ReferenceType],
        reference_value: Union[int, str],
        max_percentage_amount_in_material: Optional[float],
        legislation_threshold: Optional[float],
    ):
        """
        Parameters
        ----------
        reference_type
            Type of the record reference value.
        reference_value
            Value of the record reference. All are strings except for record history identities, which are integers.
        max_percentage_amount_in_material
            Maximum percentage of this substance that occurs in the parent material. In the case where a range
            is specified in the declaration, only the maximum is reported here.
        legislation_threshold
            Substance concentration threshold over which the material is non-compliant with the legislation.
        """

        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self._max_percentage_amount_in_material = max_percentage_amount_in_material
        self._legislation_threshold = legislation_threshold

    @property
    def max_percentage_amount_in_material(self) -> Optional[float]:
        """Maximum percentage of this substance that occurs in the parent material. In the case where a range is
        specified in the declaration, only the maximum is reported here. ``None`` means that the percentage amount
        has not been specified, not that the amount is 0 %."""
        return self._max_percentage_amount_in_material

    @property
    def legislation_threshold(self) -> Optional[float]:
        """Substance concentration threshold over which the material is non-compliant with the legislation. ``None``
        means that the threshold has not been specified, not that the threshold is 0 %."""
        return self._legislation_threshold

    def __repr__(self) -> str:
        return (
            f'<ImpactedSubstance: {{"cas_number": "{self.cas_number}", '
            f'"percent_amount": {self.max_percentage_amount_in_material}}}>'
        )


class ImpactedSubstancesResultMixin:
    """Adds results from an impacted substances query to an ``ItemDefinition`` class, turning it into an
    ``ItemWithImpactedSubstancesResult`` class.

    This class is an extension to the constructor only. It doesn't implement any additional methods.
    """

    def __init__(
        self,
        legislations: List[models.CommonLegislationWithImpactedSubstances],
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        legislations
            Substances that are found in the ``ItemDefinition`` item for the specified legislations.
        **kwargs
            Contains the ``reference_type`` and ``reference_value`` for ``RecordDefinition``-based objects.
            It is empty for ``BoM1711Definition``-based objects.
        """

        super().__init__(**kwargs)

        self._substances_by_legislation: Dict[str, List[ImpactedSubstance]] = {}

        for legislation in legislations:
            new_substances = [
                self._create_impacted_substance(substance)
                for substance in _raise_if_empty(legislation.impacted_substances)
            ]
            self._substances_by_legislation[_raise_if_empty(legislation.legislation_id)] = new_substances

    @staticmethod
    def _create_impacted_substance(
        substance: models.CommonImpactedSubstance,
    ) -> ImpactedSubstance:
        """Create an ``ImpactedSubstance`` result object based on the corresponding object returned from the low-level
        API.

        Parameters
        ----------
        substance
            Impacted substance result object that the low-level API is to return.

        Returns
        -------
        impacted_substance
            Corresponding object in this API.
        """

        # TODO: check if this is necessary
        if substance.cas_number:
            reference_type = ReferenceType.CasNumber
            reference_value = substance.cas_number
        elif substance.ec_number:
            reference_type = ReferenceType.EcNumber
            reference_value = substance.ec_number
        elif substance.substance_name:
            reference_type = ReferenceType.ChemicalName
            reference_value = substance.substance_name
        else:
            raise RuntimeError(
                "Substance result returned from Granta MI has no reference. Ensure any substances "
                "in your request include references, and check you are using an up-to-date version "
                "of the base BoM Analytics package."
            )
        impacted_substance = ImpactedSubstance(
            max_percentage_amount_in_material=_convert_unset_to_none(substance.max_percentage_amount_in_material),
            legislation_threshold=_convert_unset_to_none(substance.legislation_threshold),
            reference_type=reference_type,
            reference_value=reference_value,
        )
        return impacted_substance

    @property
    def substances_by_legislation(self) -> Dict[str, List[ImpactedSubstance]]:
        """Substances impacted for this item, grouped by legislation ID."""
        return self._substances_by_legislation

    @property
    def substances(self) -> List[ImpactedSubstance]:
        """Substances impacted for this item as a flattened list."""
        results = []
        for legislation_result in self.substances_by_legislation.values():
            results.extend(legislation_result)
        return results


class RecordWithImpactedSubstancesResultMixin(ImpactedSubstancesResultMixin, RecordReference):
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}({self._record_reference}), {len(self.substances_by_legislation)} legislations>"
        )


class MaterialWithImpactedSubstancesResult(RecordWithImpactedSubstancesResultMixin, MaterialReference):
    """Retrieves an individual material that is included as part of an impacted substances query result.

    This object includes two categories of attributes:

    * The reference to the material in Granta MI
    * The impacted substances associated with this material, both as a flat list and separated by legislation

    Notes
    -----
    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.

    Examples
    --------
    >>> result: MaterialImpactedSubstancesQueryResult
    >>> material_result = result.impacted_substances_by_material[0]
    >>> material_result.substances_by_legislation
    {'Prop65': [<ImpactedSubstance: {"cas_number": 90481-04-2}>]}

    >>> result: MaterialImpactedSubstancesQueryResult
    >>> material_result = result.impacted_substances_by_material[0]
    >>> material_result.substances
    [<ImpactedSubstance: {"cas_number": 90481-04-2}>]
    """


class PartWithImpactedSubstancesResult(RecordWithImpactedSubstancesResultMixin, PartReference):
    """Retrieves an individual part included as part of an impacted substances query result.

    This object includes two categories of attributes:

    * The reference to the part in Granta MI
    * The impacted substances associated with this part, both as a flat list and separated by legislation

    Notes
    -----
    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.

    Examples
    --------
    >>> result: PartImpactedSubstancesQueryResult
    >>> part_result = result.impacted_substances_by_part[0]
    >>> part_result.substances_by_legislation
    {'Prop65': [<ImpactedSubstance: {"cas_number": 90481-04-2}>]}

    >>> result: PartImpactedSubstancesQueryResult
    >>> part_result = result.impacted_substances_by_part[0]
    >>> part_result.substances
    [<ImpactedSubstance: {"cas_number": 90481-04-2}>]
    """


class SpecificationWithImpactedSubstancesResult(RecordWithImpactedSubstancesResultMixin, SpecificationReference):
    """Retrieves an individual specification included as part of an impacted substances query result.

    This object includes two categories of attributes:

    * The reference to the specification in Granta MI
    * The impacted substances associated with this specification, both as a flat list and separated by legislation

    Notes
    -----
    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.

    Examples
    --------
    >>> result: SpecificationImpactedSubstancesQueryResult
    >>> specification_result = result.impacted_substances_by_specification[0]
    >>> specification_result.substances_by_legislation
    {'Prop65': [<ImpactedSubstance: {"cas_number": 90481-04-2}>]}

    >>> result: SpecificationImpactedSubstancesQueryResult
    >>> specification_result = result.impacted_substances_by_specification[0]
    >>> specification_result.substances
    [<ImpactedSubstance: {"cas_number": 90481-04-2}>]
    """

    pass


class BoMWithImpactedSubstancesResult(ImpactedSubstancesResultMixin):
    """This class is instantiated, but since a BoM query can only return a single impacted substances result,
    this type is hidden and never seen by the user. As a result it is not documented.

    An individual BoM included as part of an impacted substances query result. This object includes only the impacted
    substances associated with the BoM, both as a flat list and separated by legislation. There is no item representing
    this BoM in Granta MI, and so there are no records to reference.

    Notes
    -----
    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(), {len(self.substances_by_legislation)} legislations>"


class HasIndicators(ABC):
    """Abstract base class to define the existence of indicator definitions."""

    _indicator_definitions: Indicator_Definitions


class ComplianceResultMixin(HasIndicators, RecordReference):
    """Adds results from a compliance query to a class deriving from ``ItemDefinition`` item, turning it into an
    ``[ItemType]WithComplianceResult`` class.

    A compliance query returns a BoM-like results, with indicator results attached to each level of the BoM.
    (For more information, see the notes.) This mixin implements only the indicator results for a given item.
    Separate mixins instantiate and add the child items to the parent.

    Parameters
    ----------
    indicator_results
        Compliance of the ``ItemDefinition`` item for the specified indicators. This parameter does not include
        the full indicator definition, only the indicator name.
    indicator_definitions
        Used as a base to create the indicator results for both this item and the child substances.
    **kwargs
        Contains the ``reference_type`` and ``reference_value`` for ``RecordDefinition``-based objects. It is
        empty for ``BoM1711Definition``-based objects.

    Notes
    -----
    BoMs are recursively defined structures. The top-level item is always a 'Part'. 'Parts' can
    contain zero or more:
    * 'Parts'
    * 'Specifications'
    * 'Materials'
    * 'Substances'

    'Specifications' can contain zero or more:
    * 'Specifications'
    * 'Materials'
    * 'Coatings'
    * 'Substances'

    'Materials' and 'Coatings' can both contain zero or more:
    * 'Substances'

    'Substances' have no children and are always leaf nodes.

    In addition to the items described above, a compliance query result adds ``Indicator`` objects to all items at
    every level.

    This mixin is applied to ``ItemDefinition`` objects to turn them into ``ItemWithCompliance`` objects, where
    'item' is a 'Part', 'Specification', 'Material', 'Coating', or 'Substance'.
    """

    def __init__(
        self,
        indicator_results: List[models.CommonIndicatorResult],
        indicator_definitions: Indicator_Definitions,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._indicator_definitions = indicator_definitions
        self._indicators: Indicator_Definitions = deepcopy(indicator_definitions)

        for indicator_result in indicator_results:
            self._indicators[indicator_result.name].flag = indicator_result.flag  # type: ignore[assignment, index]

    @property
    def indicators(self) -> Indicator_Definitions:
        """Compliance status of this item for each indicator included in the original query."""
        return self._indicators

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self._record_reference}), {len(self.indicators)} indicators>"


class ChildSubstanceWithComplianceMixin(HasIndicators, ABC):
    """Adds a ``substance`` attribute to an ``ItemWithComplianceResult`` class and populates it with child substances.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_substances
        Substances returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._substances: List[SubstanceWithComplianceResult] = []

    @property
    def substances(self) -> List["SubstanceWithComplianceResult"]:
        """Substance compliance result objects that are direct children of this item in the BoM."""

        return self._substances

    def _add_child_substances(self, child_substances: List[models.CommonSubstanceWithCompliance]) -> None:
        """Populate the ``substances`` attribute based on a list of low-level API substances with compliance
        results.

        Parameters
        ----------
        child_substances
            List of substances with compliance returned from the low-level API.
        """

        for child_substance in child_substances:
            child_substance_with_compliance = ItemResultFactory.create_substance_compliance_result(
                result_with_compliance=child_substance,
                indicator_definitions=self._indicator_definitions,
            )
            self._substances.append(child_substance_with_compliance)


class ChildMaterialWithComplianceMixin(HasIndicators, ABC):
    """Adds a ``materials`` attribute to an ``ItemWithComplianceResult`` class and populates it with child materials.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_materials
        Materials returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._materials: List[MaterialWithComplianceResult] = []

    @property
    def materials(self) -> List["MaterialWithComplianceResult"]:
        """Material compliance result objects that are direct children of this part or specification in the BoM."""

        return self._materials

    def _add_child_materials(
        self,
        child_materials: List[models.CommonMaterialWithCompliance],
    ) -> None:
        """Populates the ``materials`` attribute based on a list of low-level API materials with compliance
        results.

        This method operates recursively, adding any substances with compliance that are children of each material.

        Parameters
        ----------
        child_materials
            List of materials with compliance returned from the low-level API.
        """

        for child_material in child_materials:
            child_material_with_compliance = ItemResultFactory.create_material_compliance_result(
                result_with_compliance=child_material,
                indicator_definitions=self._indicator_definitions,
            )
            child_material_with_compliance._add_child_substances(_raise_if_empty(child_material.substances))
            self._materials.append(child_material_with_compliance)


class ChildSpecificationWithComplianceMixin(HasIndicators, ABC):
    """Adds a '`specification`' attribute to an ``ItemWithComplianceResult`` class and populates it with child
    specifications.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_specifications
        Specifications returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._specifications: List[SpecificationWithComplianceResult] = []

    @property
    def specifications(self) -> List["SpecificationWithComplianceResult"]:
        """Specification compliance result objects that are direct children of this item in the BoM."""

        return self._specifications

    def _add_child_specifications(
        self,
        child_specifications: List[models.CommonSpecificationWithCompliance],
    ) -> None:
        """Populate the ``specifications`` attribute based on a list of low-level API specifications with
        compliance results.

        This method operates recursively, adding any specifications, materials, coatings, and substances with compliance
        that are children of each specification.

        Parameters
        ----------
        child_specifications
            List of specifications with compliance returned from the low-level API
        """

        for child_specification in child_specifications:
            child_specification_with_compliance = ItemResultFactory.create_specification_compliance_result(
                result_with_compliance=child_specification,
                indicator_definitions=self._indicator_definitions,
            )
            child_specification_with_compliance._add_child_materials(_raise_if_empty(child_specification.materials))
            child_specification_with_compliance._add_child_specifications(
                _raise_if_empty(child_specification.specifications)
            )
            child_specification_with_compliance._add_child_coatings(_raise_if_empty(child_specification.coatings))
            child_specification_with_compliance._add_child_substances(_raise_if_empty(child_specification.substances))
            self._specifications.append(child_specification_with_compliance)


class ChildPartWithComplianceMixin(HasIndicators, ABC):
    """Adds a ``part`` attribute to an ``ItemWithComplianceResult`` class and populates it with child parts.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_parts
        Parts returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._parts: List[PartWithComplianceResult] = []

    @property
    def parts(self) -> List["PartWithComplianceResult"]:
        """Part compliance result objects that are direct children of this part in the BoM."""

        return self._parts

    def _add_child_parts(
        self,
        child_parts: List[models.CommonPartWithCompliance],
    ) -> None:
        """Populate the ``parts`` attribute based on a list of low-level API parts with compliance
        results.

        Operates recursively, adding any parts, materials, coatings, and substances with compliance
        that are children of each part.

        Parameters
        ----------
        child_parts
           List of parts with compliance returned from the low-level API
        """

        for child_part in child_parts:
            child_part_with_compliance = ItemResultFactory.create_part_compliance_result(
                result_with_compliance=child_part,
                indicator_definitions=self._indicator_definitions,
            )
            child_part_with_compliance._add_child_parts(_raise_if_empty(child_part.parts))
            child_part_with_compliance._add_child_specifications(_raise_if_empty(child_part.specifications))
            child_part_with_compliance._add_child_materials(_raise_if_empty(child_part.materials))
            child_part_with_compliance._add_child_substances(_raise_if_empty(child_part.substances))
            self._parts.append(child_part_with_compliance)


class ChildCoatingWithComplianceMixin(HasIndicators, ABC):
    """Adds a ``coating`` attribute to an ``ItemWithComplianceResult`` class and populates it with child coatings.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_coatings
         Coatings returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._coatings: List[CoatingWithComplianceResult] = []

    @property
    def coatings(self) -> List["CoatingWithComplianceResult"]:
        """Coating result objects that are direct children of this specification in the BoM."""

        return self._coatings

    def _add_child_coatings(
        self,
        child_coatings: List[models.CommonCoatingWithCompliance],
    ) -> None:
        """Populate the ``coatings`` attribute based on a list of low-level API coatings with compliance
        results.

        Operates recursively, adding any substances with compliance that are children of each coating.

        Parameters
        ----------
        child_coatings
            List of coatings with compliance returned from the low-level API.
        """

        for child_coating in child_coatings:
            child_coating_with_compliance = ItemResultFactory.create_coating_compliance_result(
                result_with_compliance=child_coating,
                indicator_definitions=self._indicator_definitions,
            )
            child_coating_with_compliance._add_child_substances(_raise_if_empty(child_coating.substances))
            self._coatings.append(child_coating_with_compliance)


class SubstanceWithComplianceResult(ComplianceResultMixin, SubstanceReference):
    """Retrieves an individual substance included as part of a compliance query result.
    This object includes three categories of attributes:

    * The reference to the substance in Granta MI
    * The compliance status of this substance, stored in a dictionary of one or more indicator objects
    * The amount of the substance present in the parent item
    """

    def __init__(self, percentage_amount: Optional[float], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._percentage_amount = percentage_amount

    @property
    def percentage_amount(self) -> Optional[float]:
        """Percentage amount of this substance in the parent item.

        .. versionadded:: 2.1
        """
        return self._percentage_amount


class MaterialWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, MaterialReference):
    """Retrieves an individual material included as part of a compliance query result.
    This object includes three categories of attributes:

    * The reference to the material in Granta MI
    * The compliance status of this material, stored in a dictionary of one or more indicator objects
    * Any substance objects that are a child of this material object
    """


class PartWithComplianceResult(
    ChildSubstanceWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildPartWithComplianceMixin,
    ComplianceResultMixin,
    PartReference,
):
    """Retrieves an individual part included as part of a compliance query result.
    This object includes three categories of attributes:

    * The reference to the part in Granta MI (if the part references a record)
    * The compliance status of this part, stored in a dictionary of one or more indicator objects
    * Any part, specification, material, or substance objects which are a child of this part object
    """


class SpecificationWithComplianceResult(
    ChildSubstanceWithComplianceMixin,
    ChildCoatingWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ComplianceResultMixin,
    SpecificationReference,
):
    """Retrieves an individual specification included as part of a compliance query result.
    This object includes three categories of attributes:

    * The reference to the specification in Granta MI
    * The compliance status of this specification, stored in a dictionary of one or more indicator objects
    * Any specification, material, coating, or substance objects which are a child of this specification object

    Notes
    -----
    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.
    """


class CoatingWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, CoatingReference):
    """Provides an individual coating included as part of a compliance query result.

    This object includes three categories of attributes:

    * The reference to the coating in Granta MI
    * The compliance status of this coating, stored in one or more indicator objects
    * Any substance objects which are a child of this coating object
    """

    record_history_identity: Optional[int]
    """Default reference type for compliance items returned as children of the queried item."""


class ValueWithUnit:
    """Describes a value obtained from the API.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        value: float,
        unit: str,
    ) -> None:
        self._value = value
        self._unit = unit

    @property
    def value(self) -> float:
        """
        Real number.
        """
        return self._value

    @property
    def unit(self) -> str:
        """
        Unit of the value.
        """
        return self._unit

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}(value={self._value}, unit="{self._unit}")>'


class SustainabilityResultMixin:
    """Adds results from a sustainability query to a class.

    A Bom-sustainability query returns a BoM-like results object, with additional sustainability information attached
    to each level of the BoM.
    This mixin implements only the sustainability metrics.

    Parameters
    ----------
    embodied_energy:
        Represents the direct and indirect energy use. Based on cumulative energy demand method developed by ecoinvent.
    climate_change:
        Estimates global warming potential considering emissions of different gases reported as carbon dioxide
        equivalents (CO2-eq.). Based on Intergovernmental Panel on Climate Change (IPCC) method.
    **kwargs
        Contains arguments handled by other mixins or base classes, e.g. ``reference_type`` and ``reference_value``
        for ``RecordDefinition``-based objects.
    """

    def __init__(
        self,
        embodied_energy: ValueWithUnit,
        climate_change: ValueWithUnit,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._embodied_energy = embodied_energy
        self._climate_change = climate_change

    @property
    def embodied_energy(self) -> ValueWithUnit:
        """Represents the direct and indirect energy use. Based on cumulative energy demand method developed by
        ecoinvent."""
        return self._embodied_energy

    @property
    def climate_change(self) -> ValueWithUnit:
        """Estimates global warming potential considering emissions of different gases reported as carbon dioxide
        equivalents (CO2-eq.). Based on Intergovernmental Panel on Climate Change (IPCC) method."""
        return self._climate_change


class MassResultMixin:
    """Adds results from a sustainability query to a class.

    A Bom-sustainability query returns a BoM-like results object, with additional sustainability information attached
    to each level of the BoM.
    This mixin implements only mass calculation results.

    Parameters
    ----------
    reported_mass:
        Indicates a mass value that is calculated by the analysis, that represents the total mass for the quantity of
        the item specified in the BoM, taking into account the quantities of parent assemblies.
    **kwargs
        Contains arguments handled by other mixins or base classes, e.g. ``reference_type`` and ``reference_value``
        for ``RecordDefinition``-based objects.
    """

    def __init__(
        self,
        reported_mass: ValueWithUnit,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._reported_mass = reported_mass

    @property
    def reported_mass(self) -> ValueWithUnit:
        """
        Indicates a mass value that is calculated by the analysis, that represents the total mass for the quantity of
        the item specified in the BoM, taking into account the quantities of parent assemblies.
        """
        return self._reported_mass


class ReusabilityResultMixin:
    """Adds results from a sustainability query to a class.

    A Bom-sustainability query returns a BoM-like results object, with additional sustainability information attached
    to each level of the BoM.
    This mixin implements only re-usability results, and are only relevant for Materials.

    Parameters
    ----------
    recyclable:
        Indicates whether a material can be recycled, regardless of the recyclates quality.
    biodegradable
        Indicates whether a material is biodegradable. Includes any waste that is capable of undergoing anaerobic or
        aerobic decomposition.
    functional_recycle:
        Indicates whether a material can be recycled into material of an equivalent quality, that can be used for the
        same (or similar) applications.
    **kwargs
        Contains arguments handled by other mixins or base classes, e.g. ``reference_type`` and ``reference_value``
        for ``RecordDefinition``-based objects.
    """

    def __init__(
        self,
        recyclable: bool,
        biodegradable: bool,
        functional_recycle: bool,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._recyclable: bool = recyclable
        self._biodegradable: bool = biodegradable
        self._functional_recycle: bool = functional_recycle

    @property
    def recyclable(self) -> bool:
        """
        Indicates whether the material can be recycled, regardless of the recyclates quality.
        """
        return self._recyclable

    @property
    def biodegradable(self) -> bool:
        """
        Indicates whether the material is biodegradable. Includes any waste that is capable of undergoing anaerobic or
        aerobic decomposition.
        """
        return self._biodegradable

    @property
    def functional_recycle(self) -> bool:
        """
        Indicates whether the material can be recycled into material of an equivalent quality, that can be used for the
        same (or similar) applications.
        """
        return self._functional_recycle


class ChildMaterialWithSustainabilityMixin:
    """Provides the implementation for managing children materials, by adding a ``materials`` property to the class.

    Parameters
    ----------
    child_materials
        Materials returned by the low-level API that are children of this item.
    **kwargs
        Contains arguments handled by other mixins or base classes.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._materials: List[MaterialWithSustainabilityResult] = []

    @property
    def materials(self) -> List["MaterialWithSustainabilityResult"]:
        """``MaterialWithSustainabilityResult`` objects that are direct children of this item in the BoM."""

        return self._materials

    def _add_child_materials(
        self,
        child_materials: List[models.CommonSustainabilityMaterialWithSustainability],
    ) -> None:
        """Populates the ``materials`` attribute based on a list of low-level API materials with sustainability
        results.

        Parameters
        ----------
        child_materials
            List of materials with sustainability returned from the low-level API.
        """

        for child_material in child_materials:
            child_material_with_sustainability = ItemResultFactory.create_material_with_sustainability(
                result_with_sustainability=child_material,
            )
            self._materials.append(child_material_with_sustainability)


class ChildPartWithSustainabilityMixin:
    """Provides the implementation for managing children parts, by adding a ``parts`` property to the class.

    Parameters
    ----------
    child_parts
        Parts returned by the low-level API that are children of this item.
    **kwargs
        Contains arguments handled by other mixins or base classes.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._parts: List[PartWithSustainabilityResult] = []

    @property
    def parts(self) -> List["PartWithSustainabilityResult"]:
        """``PartWithSustainabilityResult`` objects that are direct children of this item in the BoM."""

        return self._parts

    def _add_child_parts(
        self,
        child_parts: List[models.CommonSustainabilityPartWithSustainability],
    ) -> None:
        """Populate the ``parts`` attribute based on a list of low-level API parts with sustainability
        results.

        Parameters
        ----------
        child_parts
           List of parts with sustainability returned from the low-level API
        """

        for child_part in child_parts:
            child_part_with_sustainability = ItemResultFactory.create_part_with_sustainability(
                result_with_sustainability=child_part,
            )
            self._parts.append(child_part_with_sustainability)


class ChildProcessWithSustainabilityMixin:
    """Provides the implementation for managing children processes, by adding a ``processes`` property to the class.

    Parameters
    ----------
    child_processes
        Materials returned by the low-level API that are children of this item.
    **kwargs
        Contains arguments handled by other mixins or base classes.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._processes: List[ProcessWithSustainabilityResult] = []

    @property
    def processes(self) -> List["ProcessWithSustainabilityResult"]:
        """``ProcessWithSustainabilityResult`` objects that are direct children of this item in the BoM."""

        return self._processes

    def _add_child_processes(self, child_processes: List[models.CommonSustainabilityProcessWithSustainability]) -> None:
        """Populate the ``processes`` attribute based on a list of low-level API processes with sustainability
        results.

        Parameters
        ----------
        child_processes
            List of processes with sustainability returned from the low-level API.
        """

        for child_process in child_processes:
            child_process_result = ItemResultFactory.create_process_with_sustainability(
                result_with_sustainability=child_process,
            )
            self._processes.append(child_process_result)


class ChildTransportWithSustainabilityMixin:
    """Provides the implementation for managing child transport stages, by adding a ``transport_stages`` property to the
    class.

    Parameters
    ----------
    child_transport_stages
        Transport stages returned by the low-level API that are children of this item.
    **kwargs
        Contains arguments handled by other mixins or base classes.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._transport_stages: List[TransportWithSustainabilityResult] = []

    @property
    def transport_stages(self) -> List["TransportWithSustainabilityResult"]:
        """``TransportWithSustainabilityResult`` objects that are direct children of this item in the BoM.

        .. versionadded:: 2.3
        """

        return self._transport_stages

    def _add_child_transport_stages(
        self,
        child_transport_stages: List[models.CommonSustainabilityTransportWithSustainability],
    ) -> None:
        """Populates the ``transport_Stages`` attribute based on a list of low-level API materials with sustainability
        results.

        Parameters
        ----------
        child_transport_stages
            List of transport stages returned from the low-level API.
        """

        for child_transport_stage in child_transport_stages:
            child_transport_stage_result = ItemResultFactory.create_transport_with_sustainability(
                result_with_sustainability=child_transport_stage,
            )
            self._transport_stages.append(child_transport_stage_result)


class MaterialWithSustainabilityResult(
    ChildProcessWithSustainabilityMixin,
    SustainabilityResultMixin,
    ReusabilityResultMixin,
    MassResultMixin,
    MaterialReference,
):
    """Describes an individual material included as part of a sustainability query result.
    This object includes three categories of attributes:

    * The reference to the material in Granta MI
    * The sustainability information for this material
    * Any process objects that are a child of this material object

    .. versionadded:: 2.0
    """


class PartWithSustainabilityResult(
    ChildTransportWithSustainabilityMixin,
    ChildProcessWithSustainabilityMixin,
    ChildMaterialWithSustainabilityMixin,
    ChildPartWithSustainabilityMixin,
    SustainabilityResultMixin,
    MassResultMixin,
    PartReference,
):
    """Describes an individual part included as part of a sustainability query result.
    This object includes three categories of attributes:

    * The reference to the part in Granta MI (if the part references a record)
    * The sustainability information for this part
    * Any part, material, or process objects which are a child of this part object

    .. versionadded:: 2.0
    """


class ProcessWithSustainabilityResult(
    ChildTransportWithSustainabilityMixin,
    SustainabilityResultMixin,
    ProcessReference,
):
    """Describes a process included as part of a sustainability query result.
    This object includes two categories of attributes:

    * The reference to the process record in Granta MI
    * The sustainability information for this process

    .. versionadded:: 2.0
    """


class TransportWithSustainabilityResult(SustainabilityResultMixin, TransportReference):
    """Describes a transport stage included as part of a sustainability query result.
    This object includes two categories of attributes:

    * The reference to the transport record in Granta MI
    * The sustainability information for this transport stage

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        name: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._name = name

    @property
    def name(self) -> str:
        """
        Name of the transport stage.
        """
        return self._name


class SustainabilitySummaryBase:
    """Base class for sustainability summary results.

    Implements common environmental indicators.

    Parameters
    ----------
    embodied_energy : :class:`~ansys.grantami.bomanalytics._item_results.ValueWithUnit`
        Represents the direct and indirect energy use. Based on cumulative energy demand method developed by ecoinvent.
    embodied_energy_percentage : float
        Represents the percentage contribution of the item to total embodied energy of the parent collection.
    climate_change : :class:`~ansys.grantami.bomanalytics._item_results.ValueWithUnit`
        Estimates global warming potential considering emissions of different gases reported as carbon dioxide
        equivalents (CO2-eq.). Based on Intergovernmental Panel on Climate Change (IPCC) method.
    climate_change_percentage : float
        Represents the percentage contribution of the item to total climate change of the parent collection.
    """

    def __init__(
        self,
        embodied_energy: ValueWithUnit,
        embodied_energy_percentage: float,
        climate_change: ValueWithUnit,
        climate_change_percentage: float,
    ) -> None:
        self._embodied_energy = embodied_energy
        self._embodied_energy_percentage = embodied_energy_percentage
        self._climate_change = climate_change
        self._climate_change_percentage = climate_change_percentage

    @property
    def embodied_energy(self) -> ValueWithUnit:
        """
        Represents the direct and indirect energy use. Based on cumulative energy demand method developed by ecoinvent.
        """
        return self._embodied_energy

    @property
    def embodied_energy_percentage(self) -> float:
        """
        Represents the percentage contribution of the item to total embodied energy of the parent collection.
        """
        return self._embodied_energy_percentage

    @property
    def climate_change(self) -> ValueWithUnit:
        """
        Estimates global warming potential considering emissions of different gases reported as carbon dioxide
        equivalents (CO2-eq.). Based on Intergovernmental Panel on Climate Change (IPCC) method.
        """
        return self._climate_change

    @property
    def climate_change_percentage(self) -> float:
        """
        Represents the percentage contribution of the item to total climate change of the parent collection.
        """
        return self._climate_change_percentage


class SustainabilityPhaseSummaryResult(SustainabilitySummaryBase):
    """
    High-level sustainability summary for a phase.

    Phases currently include:

    * ``Material``
    * ``Processes``
    * ``Transport``

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        name: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._name = name

    @property
    def name(self) -> str:
        """Name of the phase. Supported values are ``Material``, ``Processes``, and ``Transport``."""
        return self._name

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}('{self.name}',"
            f" EE%={self.embodied_energy_percentage}, CC%={self.climate_change_percentage})>"
        )


class TransportSummaryBase(SustainabilitySummaryBase):
    """
    Base class for all transport summaries.

    Parameters
    ----------
    distance : :class:`~ansys.grantami.bomanalytics._item_results.ValueWithUnit`
        Represents the distance covered by this transport summary.
    """

    def __init__(
        self,
        distance: ValueWithUnit,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._distance = distance

    @property
    def distance(self) -> ValueWithUnit:
        """Distance covered by this transport summary."""
        return self._distance


class TransportSummaryResult(TransportSummaryBase):
    """
    Sustainability summary for a transport stage.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        name: Optional[str],
        transport_reference: TransportReference,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._transport_reference = transport_reference

    @property
    def name(self) -> Optional[str]:
        """Name of the transport stage."""
        return self._name

    @property
    def transport_reference(self) -> TransportReference:
        """
        Transport record reference.
        """
        return self._transport_reference

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}('{self.name}',"
            f" EE%={self.embodied_energy_percentage}, CC%={self.climate_change_percentage})>"
        )


class TransportSummaryByCategoryResult(TransportSummaryBase):
    """
    Aggregated sustainability summary for all transport stages in a category.

    .. versionadded:: 2.3
    """

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(EE%={self.embodied_energy_percentage}, "
            f"CC%={self.climate_change_percentage})>"
        )


class TransportSummaryByPartResult(TransportSummaryBase):
    """
    Aggregated sustainability summary for all transport stages associated with a part.

    .. versionadded:: 2.3
    """

    def __init__(
        self,
        part_name: Optional[str],
        parent_part_name: Optional[str],
        category: Optional[TransportCategory],
        transport_types: set[str],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._part_name = part_name if part_name else None
        self._parent_part_name = parent_part_name if parent_part_name else None
        self._category = category
        self._transport_types = transport_types

    @property
    def part_name(self) -> Optional[str]:
        """
        Name of the part (if populated in the input BoM used in the query).
        """
        return self._part_name

    @property
    def parent_part_name(self) -> Optional[str]:
        """
        Name of the parent part (if populated in the input BoM used in the query).
        """
        return self._parent_part_name

    @property
    def category(self) -> Optional[TransportCategory]:
        """
        The transport category for this summary.

        Returns ``None`` if this summary represents the aggregation of parts with transport stages that do not exceed
        the 5% threshold.
        """
        return self._category

    @property
    def transport_types(self) -> set[str]:
        """
        The transport types included in this summary.
        """
        return self._transport_types

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}('{self.part_name}',"
            f" EE%={self.embodied_energy_percentage}, CC%={self.climate_change_percentage})>"
        )


class ContributingComponentResult:
    """
    Describes a Part item of the BoM.

    Listed as :attr:`~.MaterialSummaryResult.contributors` of a :class:`~.MaterialSummaryResult`.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        name: Optional[str],
        part_number: Optional[str],
        part_reference: PartReference,
        material_mass_before_processing: ValueWithUnit,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._part_number = part_number
        self._part_reference = part_reference
        self._material_mass_before_processing = material_mass_before_processing

    @property
    def part_number(self) -> Optional[str]:
        """
        Part number.
        """
        return self._part_number

    @property
    def name(self) -> Optional[str]:
        """
        Name of the part (if populated in the input BoM used in the query).
        """
        return self._name

    @property
    def part_reference(self) -> PartReference:
        """
        Part record reference.
        """
        return self._part_reference

    @property
    def material_mass_before_processing(self) -> ValueWithUnit:
        """
        Original mass of parent material prior to any subtractive processing (removal of material).
        """
        return self._material_mass_before_processing

    def __repr__(self) -> str:
        _mass = f"{self._material_mass_before_processing.value}{self._material_mass_before_processing.unit}"
        return f"<{self.__class__.__name__}('{self.name}', mass={_mass})>"


class MaterialSummaryResult(SustainabilitySummaryBase):
    """
    Aggregated sustainability summary for a material.

    Describes the environmental footprint of a unique material, accounting for all occurrences of the material in BoM.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        identity: str,
        material_reference: MaterialReference,
        mass_before_processing: ValueWithUnit,
        mass_after_processing: ValueWithUnit,
        contributors: List[ContributingComponentResult],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._identity = identity
        self._material_reference = material_reference
        self._mass_before_processing = mass_before_processing
        self._mass_after_processing = mass_after_processing
        self._contributors = contributors

    @property
    def identity(self) -> str:
        """
        Material identity.
        """
        return self._identity

    @property
    def material_reference(self) -> MaterialReference:
        """
        Material record reference.
        """
        return self._material_reference

    @property
    def mass_before_processing(self) -> ValueWithUnit:
        """
        Original mass of material prior to any subtractive processing.
        """
        return self._mass_before_processing

    @property
    def mass_after_processing(self) -> ValueWithUnit:
        """Mass of material after any subtractive processing."""
        return self._mass_after_processing

    @property
    def contributors(self) -> List[ContributingComponentResult]:
        """Top three parts in the BoM that are made of this material (by :attr:`.mass_before_processing`)."""
        return self._contributors

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}('{self.identity}',"
            f" EE%={self.embodied_energy_percentage}, CC%={self.climate_change_percentage})>"
        )


class ProcessSummaryResult(SustainabilitySummaryBase):
    """
    Aggregated sustainability summary for a process.

    For primary and secondary processes, this corresponds to a unique process/material combination. For joining and
    finishing processes, this corresponds to a unique process, and :attr:`~.material_identity` and
    :attr:`~.material_reference` are `None`.

    Describes the environmental footprint of a process, accounting for all occurrences of the process-material pair
    found in the BoM.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        material_identity: Optional[str],
        material_reference: Optional[MaterialReference],
        process_name: str,
        process_reference: ProcessReference,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._material_identity = material_identity
        self._material_reference = material_reference
        self._process_name = process_name
        self._process_reference = process_reference

    @property
    def process_name(self) -> str:
        """
        Process name.
        """
        return self._process_name

    @property
    def process_reference(self) -> ProcessReference:
        """
        Process record reference.
        """
        return self._process_reference

    @property
    def material_identity(self) -> Optional[str]:
        """
        Material identity.

        Only populated for primary and secondary processes.
        """
        return self._material_identity

    @property
    def material_reference(self) -> Optional[MaterialReference]:
        """
        Material record reference.

        Only populated for primary and secondary processes.
        """
        return self._material_reference

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(process='{self.process_name}', material='{self.material_identity}', "
            f"EE%={self.embodied_energy_percentage}, CC%={self.climate_change_percentage})>"
        )


class Licensing:
    """Granta MI BomAnalytics Services licensing information.

    .. versionadded:: 2.0
    """

    def __init__(self, restricted_substances: bool, sustainability: bool):
        self._restricted_substances: bool = restricted_substances
        self._sustainability: bool = sustainability

    @property
    def restricted_substances(self) -> bool:
        """Whether the targeted Granta MI Server has a license for Restricted Substances analysis."""
        return self._restricted_substances

    @property
    def sustainability(self) -> bool:
        """Whether the targeted Granta MI Server has a license for Sustainability analysis."""
        return self._sustainability
