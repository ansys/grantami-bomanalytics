"""BoM Analytics BoM item definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are added to queries.
These are sub-classed in _bom_item_results.py to include the results of the queries.
"""

from abc import ABC, abstractmethod
from typing import Callable, Type, Union, List, SupportsFloat, Dict, Optional, cast
from enum import Enum, auto

from ansys.grantami.bomanalytics_openapi import models  # type: ignore[import]


class ReferenceType(Enum):
    """The supported reference types by the low-level API.

    This `Enum` is not sorted, so values and comparisons between members is not supported.
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


class RecordReference(ABC):
    """Base class for all references to records in Granta MI.

    Record references are always instantiated with two parameters; the type of the reference, and the value of the
    reference. This follows the way the REST API is structured.

    Parameters
    ----------
    reference_type
        The type of the record reference value. This class only supports 'generic' record properties.
    reference_value
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, None],
    ):
        self.record_history_identity = None
        self.record_guid = None
        self.record_history_guid = None
        if reference_type == ReferenceType.MiRecordHistoryIdentity:
            self.record_history_identity = cast(int, reference_value)
        elif reference_type == ReferenceType.MiRecordGuid:
            self.record_guid = cast(str, reference_value)
        elif reference_type == ReferenceType.MiRecordHistoryGuid:
            self.record_history_guid = cast(str, reference_value)

    @property
    def record_reference(self) -> Dict[str, Optional[str]]:
        """Converts the separate reference attributes back into a single dict that describes the type and value.

        Is used both to create the low-level API model object that references this record, and is returned as-is as the
        repr for this (and sub) objects.
        """

        if self.record_guid:
            result: Dict[str, Optional[str]] = {
                "reference_type": ReferenceType.MiRecordGuid.name,
                "reference_value": self.record_guid,
            }
        elif self.record_history_guid:
            result = {
                "reference_type": ReferenceType.MiRecordHistoryGuid.name,
                "reference_value": self.record_history_guid,
            }
        elif self.record_history_identity:
            result = {
                "reference_type": ReferenceType.MiRecordHistoryIdentity.name,
                "reference_value": str(self.record_history_identity),
            }
        else:
            result = {
                "reference_type": None,
                "reference_value": None,
            }
        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.record_reference})>"


class RecordDefinition(RecordReference):
    """Adds the ability to generate a definition of the record reference that can be supplied to the low-level API
    to run a query. As a result, is only implemented for record references that can server as inputs to a query.
    """

    @property
    @abstractmethod
    def _definition(self) -> models.Model:
        pass


class PartDefinition(RecordDefinition):
    """Concrete :class:`RecordDefinition` subclass which represents a part record.

    Parameters
    ----------
    reference_type
        The type of the record reference value. This class extends the base constructor to also support part numbers.
    reference_value
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, None],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.part_number = None
        if reference_type == ReferenceType.PartNumber:
            self.part_number = cast(str, reference_value)

    @property
    def record_reference(self) -> Dict[str, Optional[str]]:
        if self.part_number:
            return {
                "reference_type": ReferenceType.PartNumber.name,
                "reference_value": self.part_number,
            }
        else:
            return super().record_reference

    @property
    def _definition(self) -> models.CommonPartReference:
        """The low-level API material definition.

        Returns
        -------
        Definition
        """

        result = models.CommonPartReference(**self.record_reference)
        return result


class MaterialDefinition(RecordDefinition):
    """Concrete `RecordDefinition` subclass which represents a material record.

    Parameters
    ----------
    reference_type
        The type of the record reference value. This class extends the base constructor to also support material ids.
    reference_value
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, None],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.material_id = None
        if reference_type == ReferenceType.MaterialId:
            self.material_id = cast(str, reference_value)

    @property
    def record_reference(self) -> Dict[str, Optional[str]]:
        if self.material_id:
            return {
                "reference_type": ReferenceType.MaterialId.name,
                "reference_value": self.material_id,
            }
        else:
            return super().record_reference

    @property
    def _definition(self) -> models.CommonMaterialReference:
        """The low-level API material definition.

        Returns
        -------
        Definition
        """

        result = models.CommonMaterialReference(**self.record_reference)
        return result


class SpecificationDefinition(RecordDefinition):
    """Concrete `RecordDefinition` subclass which represents a specification record.

    Parameters
    ----------
    reference_type
        The type of the record reference value. This class extends the base constructor to also support specification
         ids.
    reference_value
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, None],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.specification_id = None
        if reference_type == ReferenceType.SpecificationId:
            self.specification_id = cast(str, reference_value)

    @property
    def record_reference(self) -> Dict[str, Optional[str]]:
        if self.specification_id:
            return {
                "reference_type": ReferenceType.SpecificationId.name,
                "reference_value": self.specification_id,
            }
        else:
            return super().record_reference

    @property
    def _definition(self) -> models.CommonSpecificationReference:
        """The low-level API specification definition.

        Returns
        -------
        Definition
        """

        result = models.CommonSpecificationReference(**self.record_reference)
        return result


class BaseSubstanceReference(RecordReference, ABC):
    """Abstract `RecordReference` subclass which represents a reference to a substance record.

    Substance references come in multiple flavors; inputs, compliance results and impacted substance results quantify
    substances in slightly different ways. This class implements the reference aspects of the substance record only;
    the quantification are implemented in the sub-classes.

    Parameters
    ----------
    reference_type
        The type of the record reference value. This class extends the base constructor to also support CAS numbers,
        EC numbers, and chemical names.
    reference_value
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, None],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.chemical_name = None
        self.cas_number = None
        self.ec_number = None
        if reference_type == ReferenceType.ChemicalName:
            self.chemical_name = cast(str, reference_value)
        elif reference_type == ReferenceType.CasNumber:
            self.cas_number = cast(str, reference_value)
        elif reference_type == ReferenceType.EcNumber:
            self.ec_number = cast(str, reference_value)

    @property
    def record_reference(self) -> Dict[str, Optional[str]]:
        if self.chemical_name:
            return {"reference_type": ReferenceType.ChemicalName.name, "reference_value": self.chemical_name}
        elif self.cas_number:
            return {"reference_type": ReferenceType.CasNumber.name, "reference_value": self.cas_number}
        elif self.ec_number:
            return {"reference_type": ReferenceType.EcNumber.name, "reference_value": self.ec_number}
        else:
            return super().record_reference


class SubstanceDefinition(RecordDefinition, BaseSubstanceReference):
    """Concrete substance subclass which represents the definition of a substance as supplied to a compliance query.

    Parameters
    ----------
    reference_type
        The type of the record reference value.
    reference_value
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    percentage_amount
        The amount of the substance that appears in the parent BoM item. Should be greater than 0 and less than or
        equal to 100.
    """

    _default_percentage_amount = 100  # Default to worst case scenario

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, None],
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
        """The amount of this substance in the parent item.

        Raises
        ------
        TypeError
            If the specified type is not a float or float-like object
        ValueError
            If the specified value does not satisfy 0 < value <= 100.

        Returns
        -------
        Amount
            Defaults to 100 if not set.
        """

        return self._percentage_amount or self.__class__._default_percentage_amount

    @percentage_amount.setter
    def percentage_amount(self, value: SupportsFloat) -> None:
        if not isinstance(value, SupportsFloat):
            raise TypeError(f'percentage_amount must be a number. Specified type was "{type(value)}"')
        value = float(value)
        if not 0.0 < value <= 100.0:
            raise ValueError(f'percentage_amount must be between 0 and 100. Specified value was "{value}"')
        self._percentage_amount = value

    @property
    def _definition(self) -> models.GetComplianceForSubstancesSubstanceWithAmount:
        """The low-level API substance definition.

        Returns
        -------
        Definition
        """

        definition = models.GetComplianceForSubstancesSubstanceWithAmount(
            **self.record_reference, percentage_amount=self.percentage_amount
        )
        return definition


class CoatingReference(RecordReference, ABC):
    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str, None],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )


class BoM1711Definition:
    """Represents a BoM that is supplied as part of a BoM query.

    The XML contains record references within it, so there are no explicit references to records in this object.

    Parameters
    ----------
    bom
        The bill of materials in XML 1711 format.
    """

    def __init__(self, bom: str):
        super().__init__()
        self._bom = bom

    @property
    def _definition(self) -> str:
        """The low-level API BoM definition.

        Returns
        -------
        Definition
        """

        return self._bom


class AbstractBomFactory:
    """Creates factories for a given type of API query. The key to control which definition is created is the
    request object in the low-level API.
    """

    registry: Dict[Type[models.Model], Type["BomItemDefinitionFactory"]] = {}
    """Mapping between a factory class and the definition object it can create"""

    @classmethod
    def register(cls, request_types: List[Type[models.Model]]) -> Callable:
        """Decorator function to register a specific factory class with a low-level API request type.

        Parameters
        ----------
        request_types

        Returns
        -------
        Callable
            The function that's being decorated.
        """

        def inner(item_factory: Type[BomItemDefinitionFactory]) -> Type[BomItemDefinitionFactory]:
            for request_type in request_types:
                cls.registry[request_type] = item_factory
            return item_factory

        return inner

    @classmethod
    def create_factory_for_request_type(cls, request_type: Type[models.Model]) -> "BomItemDefinitionFactory":
        """Factory method to instantiate and return a specific item definition factory.

        Parameters
        ----------
        request_type
            The request type for which a definition is needed

        Returns
        -------
        Factory
            An instance of a factory to create the appropriate definitions.

        Raises
        ------
        RuntimeError
            If a request type is not registered to any factory.
        """

        try:
            item_factory_class = cls.registry[request_type]
        except KeyError as e:
            raise RuntimeError(f'Unregistered request type "{request_type}"').with_traceback(e.__traceback__)
        item_factory = item_factory_class()
        return item_factory


class BomItemDefinitionFactory(ABC):
    """Base factory to create a specific definition object. Applies to definitions based on records only.

    These factories intentionally abstract away the concept of :class:`ReferenceType` and expose separate static methods
    to create definitions based on a specific reference type, which more closely relates to the structure in the
    :mod:`queries.py` builder.
    """

    @staticmethod
    @abstractmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> "RecordDefinition":
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_guid(record_guid: str) -> "RecordDefinition":
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> "RecordDefinition":
        pass


@AbstractBomFactory.register(
    [
        models.GetComplianceForMaterialsRequest,
        models.GetImpactedSubstancesForMaterialsRequest,
    ]
)
class MaterialDefinitionFactory(BomItemDefinitionFactory):
    """Creates material definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> MaterialDefinition:
        """Instantiate and return a `MaterialDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> MaterialDefinition:
        """Instantiate and return a `MaterialDefinition` object based on the provided record history GUID.

        Parameters
        ----------
        record_history_guid

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid)

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> MaterialDefinition:
        """Instantiate and return a `MaterialDefinition` object based on the provided record GUID.

        Parameters
        ----------
        record_guid

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_material_id(material_id: str) -> MaterialDefinition:
        """Instantiate and return a `MaterialDefinition` object based on the provided material ID.

        Parameters
        ----------
        material_id

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MaterialId, reference_value=material_id)


@AbstractBomFactory.register(
    [
        models.GetComplianceForPartsRequest,
        models.GetImpactedSubstancesForPartsRequest,
    ]
)
class PartDefinitionFactory(BomItemDefinitionFactory):
    """Creates part definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> PartDefinition:
        """Instantiate and return a `PartDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> PartDefinition:
        """Instantiate and return a `PartDefinition` object based on the provided record history GUID.

        Parameters
        ----------
        record_history_guid

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid)

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> PartDefinition:
        """Instantiate and return a `PartDefinition` object based on the provided record GUID.

        Parameters
        ----------
        record_guid

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_part_number(part_number: str) -> PartDefinition:
        """Instantiate and return a `PartDefinition` object based on the provided part number.

        Parameters
        ----------
        part_number

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.PartNumber, reference_value=part_number)


@AbstractBomFactory.register(
    [
        models.GetComplianceForSpecificationsRequest,
        models.GetImpactedSubstancesForSpecificationsRequest,
    ]
)
class SpecificationDefinitionFactory(BomItemDefinitionFactory):
    """Creates specification definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> SpecificationDefinition:
        """Instantiate and return a `SpecificationDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> SpecificationDefinition:
        """Instantiate and return a `SpecificationDefinition` object based on the provided record history GUID.

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
        """Instantiate and return a `SpecificationDefinition` object based on the provided record GUID.

        Parameters
        ----------
        record_guid

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_specification_id(specification_id: str) -> SpecificationDefinition:
        """Instantiate and return a `SpecificationDefinition` object based on the provided specification id.

        Parameters
        ----------
        specification_id

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(reference_type=ReferenceType.SpecificationId, reference_value=specification_id)


@AbstractBomFactory.register([models.GetComplianceForSubstancesRequest])
class SubstanceComplianceDefinitionFactory(BomItemDefinitionFactory):
    """Creates substance compliance definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided record history GUID.

        Parameters
        ----------
        record_history_guid

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided record GUID.

        Parameters
        ----------
        record_guid

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_chemical_name(chemical_name: str) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided chemical name.

        Parameters
        ----------
        chemical_name

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.ChemicalName, reference_value=chemical_name)

    @staticmethod
    def create_definition_by_cas_number(cas_number: str) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided CAS number.

        Parameters
        ----------
        cas_number

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.CasNumber, reference_value=cas_number)

    @staticmethod
    def create_definition_by_ec_number(ec_number: str) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided EC number.

        Parameters
        ----------
        ec_number

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.EcNumber, reference_value=ec_number)


@AbstractBomFactory.register(
    [
        models.GetComplianceForBom1711Request,
        models.GetImpactedSubstancesForBom1711Request,
    ]
)
class BomFactory:
    """Creates bom definition objects."""

    @staticmethod
    def create_definition(bom: str) -> BoM1711Definition:
        """Instantiate and return a `Bom1711Definition` object based on the provided bom.

        Parameters
        ----------
        bom

        Returns
        -------
        Bom1711Definition
        """

        return BoM1711Definition(bom=bom)
