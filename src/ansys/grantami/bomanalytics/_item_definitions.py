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

"""BoM Analytics BoM item definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are added to queries.
These are sub-classed in the ``_bom_item_results.py`` file to include the results of the queries.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
import numbers
from typing import Any, Dict, Optional, Union, cast

from ansys.grantami.bomanalytics_openapi import models
from ansys.openapi.common import Unset_Type


class ReferenceType(Enum):
    """Provides the reference types supported by the low-level API.

    This enum is not sorted, so values and comparisons between members are not supported.
    """

    MiRecordHistoryGuid = auto()
    MiRecordGuid = auto()
    MiRecordHistoryIdentity = auto()
    PartNumber = auto()
    MaterialId = auto()
    SpecificationId = auto()
    ChemicalName = auto()
    CasNumber = auto()
    EcNumber = auto()


class IdentifierMixin(ABC):
    def __init__(self, identity: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._identity: Optional[str] = identity

    @property
    def identity(self) -> Optional[str]:
        """Item unique identifier.

        This property is only populated on BoM query results and is equal to the ``id`` attribute of the
        corresponding input BoM item. If no ``id`` has been defined on the BoM item, a unique auto-generated value is
        assigned during analysis.
        """
        return self._identity


class CommonIdentifiersMixin(IdentifierMixin, ABC):
    def __init__(self, external_identity: Optional[str] = None, name: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._external_identity: Optional[str] = external_identity
        self._name: Optional[str] = name

    @property
    def external_identity(self) -> Optional[str]:
        """Item external identity.

        This property is only populated on BoM query results and is equal to the ``<ExternalIdentity>`` element of
        the corresponding input BoM item.
        """
        return self._external_identity

    @property
    def name(self) -> Optional[str]:
        """Item name.

        This property is only populated on BoM query results and is equal to the ``<Name>`` element of
        the corresponding input BoM item.
        """
        return self._name


class RecordReference(ABC):
    """Provides all references to records in Granta MI.

    Record references are always instantiated with two parameters: the type of the reference and the value of the
    reference. This follows the way that the REST API is structured.

    Parameters
    ----------
    reference_type
        Type of the record reference value. This class only supports 'generic' record properties.
    reference_value : str, int
        Value of the record reference. All are string values except for record history identities,
        which are integers.
    """

    def __init__(
        self,
        reference_type: Optional[ReferenceType],
        reference_value: Union[int, str, Unset_Type],
    ):
        self._reference_type = reference_type
        if isinstance(reference_value, Unset_Type):
            self._reference_value = None
        else:
            self._reference_value = reference_value

    @property
    def record_history_identity(self) -> Optional[int]:
        """Record history identity."""
        if self._reference_type == ReferenceType.MiRecordHistoryIdentity:
            return cast(int, self._reference_value)
        return None

    @property
    def record_history_guid(self) -> Optional[str]:
        """Record history GUID."""
        if self._reference_type == ReferenceType.MiRecordHistoryGuid:
            return cast(str, self._reference_value)
        return None

    @property
    def record_guid(self) -> Optional[str]:
        """Record GUID."""
        if self._reference_type == ReferenceType.MiRecordGuid:
            return cast(str, self._reference_value)
        return None

    @property
    def _record_reference(self) -> Dict[str, str]:
        """Converts the separate reference attributes back into a single dictionary that describes the type and value.

        This method is used to create the low-level API model object that references this record and is returned as-is
        as the repr for this object and subobjects.
        """

        result = {}
        if self._reference_type is not None:
            result["reference_type"] = self._reference_type.name
        if self._reference_value is not None:
            result["reference_value"] = str(self._reference_value)
        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self._record_reference})>"


class RecordDefinition(RecordReference):
    """Adds the ability to generate a definition of the record reference that can be supplied to the low-level API
    to run a query. As a result, this class is only implemented for record references that can serve as inputs to
    a query.
    """

    @property
    @abstractmethod
    def _definition(self) -> models.ModelBase:
        pass


class PartReference(RecordReference):
    """Represents a reference to a Part record.

    This class extends the base class to also support part numbers.
    """

    @property
    def part_number(self) -> Optional[str]:
        """Part number."""
        if self._reference_type == ReferenceType.PartNumber:
            return cast(str, self._reference_value)
        return None


class PartReferenceWithIdentifiers(CommonIdentifiersMixin, PartReference):
    def __init__(self, input_part_number: Optional[str] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self._input_part_number: Optional[str] = input_part_number

    @property
    def input_part_number(self) -> Optional[str]:
        """Input part number.

        This property is only populated on BoM query results and is equal to the ``<PartNumber>`` element of
        the corresponding input BoM item.
        """
        return self._input_part_number


class PartDefinition(RecordDefinition, PartReference):
    """Represents a part record from the concrete :class:`RecordDefinition` subclass."""

    @property
    def _definition(self) -> models.CommonPartReference:
        """Low-level API part definition.

        Returns
        -------
        Definition
        """

        result = models.CommonPartReference(**self._record_reference)
        return result


class MaterialReference(RecordReference):
    # Because of ProcessSummaryResult, this is publicly documented.
    """Represents a reference to a Material record.

    This class extends the base class to also support material IDs.
    """

    @property
    def material_id(self) -> Optional[str]:
        """Material ID."""
        if self._reference_type == ReferenceType.MaterialId:
            return cast(str, self._reference_value)
        return None


class MaterialReferenceWithIdentifiers(CommonIdentifiersMixin, MaterialReference):
    pass


class MaterialDefinition(RecordDefinition, MaterialReference):
    """Represents a material record from the concrete :class:`RecordDefinition` subclass."""

    @property
    def _definition(self) -> models.CommonMaterialReference:
        """Low-level API material definition.

        Returns
        -------
        Definition
        """

        result = models.CommonMaterialReference(**self._record_reference)
        return result


class SpecificationReference(RecordReference):
    """Represents a reference to a specification record from the concrete :class:`RecordReference` subclass.

    This class extends the base class to also support specification IDs.
    """

    @property
    def specification_id(self) -> Optional[str]:
        """Specification ID."""
        if self._reference_type == ReferenceType.SpecificationId:
            return cast(str, self._reference_value)
        return None


class SpecificationReferenceWithIdentifiers(CommonIdentifiersMixin, SpecificationReference):
    pass


class SpecificationDefinition(RecordDefinition, SpecificationReference):
    """Represents a specification record from the concrete :class:`RecordDefinition` subclass."""

    @property
    def _definition(self) -> models.CommonSpecificationReference:
        """Low-level API specification definition.

        Returns
        -------
        Definition
        """

        result = models.CommonSpecificationReference(**self._record_reference)
        return result


class SubstanceReference(RecordReference):
    """Represents a reference to a substance record from the abstract ``RecordReference`` subclass.

    This class extends the base constructor to also support CAS numbers, EC numbers, and chemical names.

    Substance references come in multiple flavors. Inputs, compliance results, and impacted substance results quantify
    substances in slightly different ways. This class implements the reference aspects of the substance record only.
    The quantifications are implemented in the subclasses.
    """

    @property
    def cas_number(self) -> Optional[str]:
        """CAS number."""
        if self._reference_type == ReferenceType.CasNumber:
            return cast(str, self._reference_value)
        return None

    @property
    def ec_number(self) -> Optional[str]:
        """EC number."""
        if self._reference_type == ReferenceType.EcNumber:
            return cast(str, self._reference_value)
        return None

    @property
    def chemical_name(self) -> Optional[str]:
        """Chemical name."""
        if self._reference_type == ReferenceType.ChemicalName:
            return cast(str, self._reference_value)
        return None


class SubstanceReferenceWithIdentifiers(CommonIdentifiersMixin, SubstanceReference):
    pass


class SubstanceDefinition(RecordDefinition, SubstanceReference):
    """Represents the definition of a substance as supplied to a compliance query from the concrete
    ``Substance`` subclass.

    Parameters
    ----------
    reference_type
       Type of the record reference value.
    reference_value
        Value of the record reference. All are strings except for record history identities,
        which are integers.
    percentage_amount : int, optional
        Percentage of the substance that appears in the parent BoM item. This value should be greater than 0 and
        less than or equal to 100. The default is ``100``, which is the worst case scenario.
    """

    _default_percentage_amount = 100  # Default to worst case scenario

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, Unset_Type],
        percentage_amount: Union[float, None] = None,
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self._percentage_amount = None
        if percentage_amount:
            self.percentage_amount = percentage_amount

    @property
    def percentage_amount(self) -> float:
        """Percentage of this substance in the parent item.

        Raises
        ------
        TypeError
            Error raised if the specified type is not a float or float-like object.
        ValueError
            Error raised if the specified value does not satisfy 0 < value <= 100.

        Returns
        -------
        Amount
            Defaults to ``100`` if not set.
        """

        return self._percentage_amount or self.__class__._default_percentage_amount

    @percentage_amount.setter
    def percentage_amount(self, value: float) -> None:
        if not isinstance(value, numbers.Real):
            raise TypeError(f'percentage_amount must be a number. Specified type was "{type(value)}"')
        value = float(value)
        if not 0.0 < value <= 100.0:
            raise ValueError(f'percentage_amount must be between 0 and 100. Specified value was "{value}"')
        self._percentage_amount = value

    @property
    def _definition(self) -> models.GetComplianceForSubstancesSubstanceWithAmount:
        """Low-level API substance definition.

        Returns
        -------
        Definition
        """

        definition = models.GetComplianceForSubstancesSubstanceWithAmount(
            **self._record_reference, percentage_amount=self.percentage_amount
        )
        return definition


class CoatingReference(RecordReference):
    """Extends RecordReference without changes, to re-define the class name, because it appears in the repr."""


class CoatingReferenceWithIdentifier(IdentifierMixin, CoatingReference):
    pass


class ProcessReference(RecordReference):
    # Because of ProcessSummaryResult, this is publicly documented.
    # Extends RecordReference without changes, to re-define the class name, because it appears in the repr.
    """Represents a reference to a Process record.

    .. versionadded:: 2.0
    """


class ProcessReferenceWithIdentifiers(CommonIdentifiersMixin, ProcessReference):
    pass


class TransportReference(RecordReference):
    """Represents a reference to a Transport record.

    .. versionadded:: 2.0
    """

    # Extends RecordReference without changes, to re-define the class name, because it appears in the repr


class TransportReferenceWithIdentifier(IdentifierMixin, TransportReference):
    pass


class BomItemDefinitionFactory(ABC):
    """Creates a specific definition object. This base factory class applies to definitions based on records only.

    These factories intentionally abstract away the concept of the :class:`ReferenceType` class and expose
    separate static methods to create definitions based on a specific reference type, which more closely
    relates to the structure in the :mod:`queries.py` builder.
    """

    @staticmethod
    @abstractmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
    ) -> "RecordDefinition":
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_guid(record_guid: str) -> "RecordDefinition":
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> "RecordDefinition":
        pass


class MaterialDefinitionFactory(BomItemDefinitionFactory):
    """Creates material definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
    ) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a record history identity.

        Parameters
        ----------
        record_history_identity
            Record history identity.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a record history GUID.

        Parameters
        ----------
        record_history_guid
            Record history GUID.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid)

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a record GUID.

        Parameters
        ----------
        record_guid
            Record GUID.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_material_id(material_id: str) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a material ID.

        Parameters
        ----------
        material_id
            Material ID.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MaterialId, reference_value=material_id)


class PartDefinitionFactory(BomItemDefinitionFactory):
    """Creates part definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
    ) -> PartDefinition:
        """Instantiate and return a ``PartDefinition`` object based on a record history identity.

        Parameters
        ----------
        record_history_identity
            Record history identity.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> PartDefinition:
        """Instantiate and return a ``PartDefinition`` object based on a record history GUID.

        Parameters
        ----------
        record_history_guid
            Record history GUID.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid)

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> PartDefinition:
        """Instantiate and return a ``PartDefinition`` object based on a record GUID.

        Parameters
        ----------
        record_guid
            Record GUID.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_part_number(part_number: str) -> PartDefinition:
        """Instantiate and return a ``PartDefinition`` object based on a part number.

        Parameters
        ----------
        part_number
            Part number.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.PartNumber, reference_value=part_number)


class SpecificationDefinitionFactory(BomItemDefinitionFactory):
    """Creates specification definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
    ) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a record history identity.

        Parameters
        ----------
        record_history_identity
            Record history identity.


        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
        )

    @staticmethod
    def create_definition_by_record_history_guid(
        record_history_guid: str,
    ) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a record history GUID.

        Parameters
        ----------
        record_history_guid

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a record GUID.

        Parameters
        ----------
        record_guid
            Record GUID.

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_specification_id(specification_id: str) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a specification ID.

        Parameters
        ----------
        specification_id
            Specification ID.

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(reference_type=ReferenceType.SpecificationId, reference_value=specification_id)


class SubstanceComplianceDefinitionFactory(BomItemDefinitionFactory):
    """Creates substance compliance definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
    ) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a record history identity.

        Parameters
        ----------
        record_history_identity
            Record history identity.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a record history GUID.

        Parameters
        ----------
        record_history_guid
            Record history GUID.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a record GUID.

        Parameters
        ----------
        record_guid
            Record GUID.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_chemical_name(chemical_name: str) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a chemical name.

        Parameters
        ----------
        chemical_name
            Chemical name.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.ChemicalName, reference_value=chemical_name)

    @staticmethod
    def create_definition_by_cas_number(cas_number: str) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a CAS number.

        Parameters
        ----------
        cas_number
            CAS number.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.CasNumber, reference_value=cas_number)

    @staticmethod
    def create_definition_by_ec_number(ec_number: str) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on an EC number.

        Parameters
        ----------
        ec_number
            EC number.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.EcNumber, reference_value=ec_number)
