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

"""BoM Analytics BoM item definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are added to queries.
These are sub-classed in the ``_bom_item_results.py`` file to include the results of the queries.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
import numbers
from typing import Any, Dict, Optional, Union, cast

from ansys.grantami.bomanalytics_openapi.v2 import models
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

    Record references are always instantiated with at least two parameters: the type of the reference and the value of
    the reference. The reference may also include a database key and external identity.

    Parameters
    ----------
    reference_type
        Type of the record reference value. This class only supports 'generic' record properties.
    reference_value : str, int
        Value of the record reference. All are string values except for record history identities,
        which are integers.
    database_key : str, optional
        The database key that contains the record, if different to the database specified in
        :meth:`.BomAnalyticsClient.set_database_details`. Supported by MI Restricted Substances and Sustainability
        Reports 2026 R1 or later.

        .. versionadded:: 2.4
    """

    def __init__(
        self,
        reference_type: Optional[ReferenceType],
        reference_value: Union[int, str, Unset_Type, None],
        database_key: Optional[str] = None,
    ):
        self._reference_type = reference_type
        if isinstance(reference_value, Unset_Type):
            self._reference_value = None
        else:
            self._reference_value = reference_value
        self._database_key = database_key

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
    def database_key(self) -> Optional[str]:
        """
        The database key for the database that contains the record.

        This property is only populated if the record is in a different database to the one specified in
        :meth:`.BomAnalyticsClient.set_database_details`. Supported by MI Restricted Substances and Sustainability
        Reports 2026 R1 or later.

        .. versionadded:: 2.4
        """
        return self._database_key

    @property
    def _record_reference(self) -> Dict[str, str]:
        """Converts the separate reference attributes back into a single dictionary that describes the type, value,
        and database key.

        This method is used to create the low-level API model object that references this record and is returned as-is
        as the repr for this object and subobjects.
        """

        result = {}
        if self._reference_type is not None:
            result["reference_type"] = self._reference_type.name
        if self._reference_value is not None:
            result["reference_value"] = str(self._reference_value)
        if self._database_key is not None:
            result["database_key"] = self._database_key
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


class PartReference(CommonIdentifiersMixin, RecordReference):
    """Represents a reference to a part record.

    This class extends the base class to also support part numbers.
    """

    def __init__(
        self,
        input_part_number: Optional[str] = None,
        equivalent_references: Optional[list["PartReference"]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._input_part_number: Optional[str] = input_part_number
        self._equivalent_references = equivalent_references

    @property
    def part_number(self) -> Optional[str]:
        """Part number."""
        if self._reference_type == ReferenceType.PartNumber:
            return cast(str, self._reference_value)
        return None

    @property
    def input_part_number(self) -> Optional[str]:
        """Input part number.

        This property is only populated on BoM query results and is equal to the ``<PartNumber>`` element of
        the corresponding input BoM item.
        """
        return self._input_part_number

    @property
    def equivalent_references(self) -> Optional[list["PartReference"]]:
        """
        Other part records which are defined as being equivalent to this record.

        Only populated if this record is a substitute for a record in a different database during analysis via a
        cross-database link.

        .. versionadded:: 2.4
        """
        return self._equivalent_references


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


class MaterialReference(CommonIdentifiersMixin, RecordReference):
    """Represents a reference to a material record.

    This class extends the base class to also support material IDs.
    """

    def __init__(
        self,
        equivalent_references: Optional[list["MaterialReference"]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._equivalent_references = equivalent_references

    @property
    def material_id(self) -> Optional[str]:
        """Material ID."""
        if self._reference_type == ReferenceType.MaterialId:
            return cast(str, self._reference_value)
        return None

    @property
    def equivalent_references(self) -> Optional[list["MaterialReference"]]:
        """
        Other material records which are defined as being equivalent to this record.

        Only populated if this record is a substitute for a record in a different database during analysis via a
        cross-database link.

        .. versionadded:: 2.4
        """
        return self._equivalent_references


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


class SpecificationReference(CommonIdentifiersMixin, RecordReference):
    """Represents a reference to a specification record.

    This class extends the base class to also support specification IDs.
    """

    def __init__(
        self,
        equivalent_references: Optional[list["SpecificationReference"]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._equivalent_references = equivalent_references

    @property
    def specification_id(self) -> Optional[str]:
        """Specification ID."""
        if self._reference_type == ReferenceType.SpecificationId:
            return cast(str, self._reference_value)
        return None

    @property
    def equivalent_references(self) -> Optional[list["SpecificationReference"]]:
        """
        Other specification records which are defined as being equivalent to this record.

        Only populated if this record is a substitute for a record in a different database during analysis via a
        cross-database link.

        .. versionadded:: 2.4
        """
        return self._equivalent_references


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


class SubstanceReference(CommonIdentifiersMixin, RecordReference):
    """Represents a reference to a substance record.

    This class extends the base constructor to also support CAS numbers, EC numbers, and chemical names.

    Substance references come in multiple flavors. Inputs, compliance results, and impacted substance results quantify
    substances in slightly different ways. This class implements the reference aspects of the substance record only.
    The quantifications are implemented in the subclasses.
    """

    def __init__(
        self,
        equivalent_references: Optional[list["SubstanceReference"]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._equivalent_references = equivalent_references

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

    @property
    def equivalent_references(self) -> Optional[list["SubstanceReference"]]:
        """
        Other substance records which are defined as being equivalent to this record.

        Only populated if this record is a substitute for a record in a different database during analysis via a
        cross-database link.

        .. versionadded:: 2.4
        """
        return self._equivalent_references


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
    database_key : str, optional
        The database key that contains the record, if different to the database specified in
        :meth:`.BomAnalyticsClient.set_database_details`. Supported by MI Restricted Substances and Sustainability
        Reports 2026 R1 or later.
    """

    _default_percentage_amount = 100  # Default to worst case scenario

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, Unset_Type],
        percentage_amount: Union[float, None] = None,
        database_key: Optional[str] = None,
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
            database_key=database_key,
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


class CoatingReference(IdentifierMixin, RecordReference):
    """Represents a reference to a coating record."""

    def __init__(
        self,
        equivalent_references: Optional[list["CoatingReference"]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._equivalent_references = equivalent_references

    @property
    def equivalent_references(self) -> Optional[list["CoatingReference"]]:
        """
        Other coating records which are defined as being equivalent to this record.

        Only populated if this record is a substitute for a record in a different database during analysis via a
        cross-database link.

        .. versionadded:: 2.4
        """
        return self._equivalent_references


class ProcessReference(CommonIdentifiersMixin, RecordReference):
    """Represents a reference to a process record.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        equivalent_references: Optional[list["ProcessReference"]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._equivalent_references = equivalent_references

    @property
    def equivalent_references(self) -> Optional[list["ProcessReference"]]:
        """
        Other process records which defined as being equivalent to this record.

        Only populated if this record is a substitute for a record in a different database during analysis via a
        cross-database link.

        .. versionadded:: 2.4
        """
        return self._equivalent_references


class TransportReference(IdentifierMixin, RecordReference):
    """Represents a reference to a transport record.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        equivalent_references: Optional[list["TransportReference"]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._equivalent_references = equivalent_references

    @property
    def equivalent_references(self) -> Optional[list["TransportReference"]]:
        """
        Other transport records which are defined as being equivalent to this record.

        Only populated if this record is a substitute for a record in a different database during analysis via a
        cross-database link.

        .. versionadded:: 2.4
        """
        return self._equivalent_references


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
        database_key: Optional[str] = None,
    ) -> "RecordDefinition":
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_guid(record_guid: str, database_key: Optional[str] = None) -> "RecordDefinition":
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_history_guid(
        record_history_guid: str,
        database_key: Optional[str] = None,
    ) -> "RecordDefinition":
        pass


class MaterialDefinitionFactory(BomItemDefinitionFactory):
    """Creates material definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
        database_key: Optional[str] = None,
    ) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a record history identity.

        Parameters
        ----------
        record_history_identity
            Record history identity.
        database_key
            Database key.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_history_guid(
        record_history_guid: str,
        database_key: Optional[str] = None,
    ) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a record history GUID.

        Parameters
        ----------
        record_history_guid
            Record history GUID.
        database_key
            Database key.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid,
            reference_value=record_history_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str, database_key: Optional[str] = None) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a record GUID.

        Parameters
        ----------
        record_guid
            Record GUID.
        database_key
            Database key.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(
            reference_type=ReferenceType.MiRecordGuid,
            reference_value=record_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_material_id(material_id: str, database_key: Optional[str] = None) -> MaterialDefinition:
        """Instantiate and return a ``MaterialDefinition`` object based on a material ID.

        Parameters
        ----------
        material_id
            Material ID.
        database_key
            Database key.

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(
            reference_type=ReferenceType.MaterialId,
            reference_value=material_id,
            database_key=database_key,
        )


class PartDefinitionFactory(BomItemDefinitionFactory):
    """Creates part definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
        database_key: Optional[str] = None,
    ) -> PartDefinition:
        """
        Instantiate and return a ``PartDefinition`` object based on a record history identity  and optional database
        key.

        Parameters
        ----------
        record_history_identity
            Record history identity.
        database_key
            Database key.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_history_guid(
        record_history_guid: str, database_key: Optional[str] = None
    ) -> PartDefinition:
        """Instantiate and return a ``PartDefinition`` object based on a record history GUID  and optional database key.

        Parameters
        ----------
        record_history_guid
            Record history GUID.
        database_key
            Database key.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid,
            reference_value=record_history_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str, database_key: Optional[str] = None) -> PartDefinition:
        """Instantiate and return a ``PartDefinition`` object based on a record GUID  and optional database key.

        Parameters
        ----------
        record_guid
            Record GUID.
        database_key
            Database key.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(
            reference_type=ReferenceType.MiRecordGuid,
            reference_value=record_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_part_number(part_number: str, database_key: Optional[str] = None) -> PartDefinition:
        """Instantiate and return a ``PartDefinition`` object based on a part number and optional database key.

        Parameters
        ----------
        part_number
            Part number.
        database_key
            Database key.

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(
            reference_type=ReferenceType.PartNumber,
            reference_value=part_number,
            database_key=database_key,
        )


class SpecificationDefinitionFactory(BomItemDefinitionFactory):
    """Creates specification definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
        database_key: Optional[str] = None,
    ) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a record history identity and optional
        database key.

        Parameters
        ----------
        record_history_identity
            Record history identity.
        database_key
            Database key.

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_history_guid(
        record_history_guid: str,
        database_key: Optional[str] = None,
    ) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a record history GUID and optional
        database key.

        Parameters
        ----------
        record_history_guid
            Record history GUID.
        database_key
            Database key.

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid,
            reference_value=record_history_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_guid(
        record_guid: str,
        database_key: Optional[str] = None,
    ) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a record GUID and optional database key.

        Parameters
        ----------
        record_guid
            Record GUID.
        database_key
            Database key.

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordGuid,
            reference_value=record_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_specification_id(
        specification_id: str,
        database_key: Optional[str] = None,
    ) -> SpecificationDefinition:
        """Instantiate and return a ``SpecificationDefinition`` object based on a specification ID and optional database
        key.

        Parameters
        ----------
        specification_id
            Specification ID.
        database_key
            Database key.

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(
            reference_type=ReferenceType.SpecificationId,
            reference_value=specification_id,
            database_key=database_key,
        )


class SubstanceComplianceDefinitionFactory(BomItemDefinitionFactory):
    """Creates substance compliance definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(
        record_history_identity: int,
        database_key: Optional[str] = None,
    ) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a record history identity and optional
        database key.

        Parameters
        ----------
        record_history_identity
            Record history identity.
        database_key
            Database key.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity,
            reference_value=record_history_identity,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_history_guid(
        record_history_guid: str,
        database_key: Optional[str] = None,
    ) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a record history GUID and optional database
        key.

        Parameters
        ----------
        record_history_guid
            Record history GUID.
        database_key
            Database key.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid,
            reference_value=record_history_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str, database_key: Optional[str] = None) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a record GUID and optional database key.

        Parameters
        ----------
        record_guid
            Record GUID.
        database_key
            Database key.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordGuid,
            reference_value=record_guid,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_chemical_name(
        chemical_name: str,
        database_key: Optional[str] = None,
    ) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a chemical name and optional database key.

        Parameters
        ----------
        chemical_name
            Chemical name.
        database_key
            Database key.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.ChemicalName,
            reference_value=chemical_name,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_cas_number(cas_number: str, database_key: Optional[str] = None) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on a CAS number and optional database key.

        Parameters
        ----------
        cas_number
            CAS number.
        database_key
            Database key.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.CasNumber,
            reference_value=cas_number,
            database_key=database_key,
        )

    @staticmethod
    def create_definition_by_ec_number(ec_number: str, database_key: Optional[str] = None) -> SubstanceDefinition:
        """Instantiate and return a ``SubstanceDefinition`` object based on an EC number and optional database key.

        Parameters
        ----------
        ec_number
            EC number.
        database_key
            Database key.

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.EcNumber,
            reference_value=ec_number,
            database_key=database_key,
        )
