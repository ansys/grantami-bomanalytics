"""Bom Analytics Bom item definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are added to queries.
These are sub-classed in _bom_item_results.py to include the results of the queries.
"""


from abc import ABC, abstractmethod
from typing import Callable, Type, Union, List, SupportsFloat
from enum import Enum, auto

from ansys.granta.bomanalytics import models


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


class RecordDefinition(ABC):
    """Base class for all record-based item definitions.

    Records are always instantiated with two parameters; the type of the reference, and the value of the reference.
    This follows the way the low-level API is structured.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value. This class only supports 'generic' record properties.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.

    Attributes
    ----------
    record_history_identity : int, optional
    record_guid : str, optional
    record_history_guid : str, optional
    _model : Type[models.Model]
        The low-level API class that defines this definition object. Is set for concrete subclasses.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
    ):
        self.record_history_identity: Union[int, None] = None
        self.record_guid: Union[str, None] = None
        self.record_history_guid: Union[str, None] = None
        if reference_type == ReferenceType.MiRecordHistoryIdentity:
            self.record_history_identity = reference_value
        elif reference_type == ReferenceType.MiRecordGuid:
            self.record_guid = reference_value
        elif reference_type == ReferenceType.MiRecordHistoryGuid:
            self.record_history_guid = reference_value

        self._model = None

    def _create_definition(self) -> models.Model:
        """Instantiate the specific low-level API model class for this record.

        Returns
        -------
        models.Model, optional
            If one of the reference attributes defined in this class is populated, then an instantiated model is
            returned. Otheriwse, `None` is returned.
        """

        if self.record_guid:
            return self._model(reference_type=ReferenceType.MiRecordGuid.name, reference_value=self.record_guid)
        if self.record_history_guid:
            return self._model(
                reference_type=ReferenceType.MiRecordHistoryGuid.name,
                reference_value=self.record_history_guid,
            )
        if self.record_history_identity:
            return self._model(
                reference_type=ReferenceType.MiRecordHistoryIdentity.name,
                reference_value=self.record_history_identity,
            )

    @property
    @abstractmethod
    def definition(self):
        pass


class PartDefinition(RecordDefinition):
    """Concrete `RecordDefinition` subclass which represents a part record.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value. This class extends the base constructor to also support part numbers.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.

    Attributes
    ----------
    part_number : str, optional
    _model : Type[models.Model]
        The low-level API class that defines this definition object.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.part_number: Union[str, None] = None
        if reference_type == ReferenceType.PartNumber:
            self.part_number = reference_value

        self._model = models.GrantaBomAnalyticsServicesInterfaceCommonPartReference

    @property
    def definition(self) -> models.GrantaBomAnalyticsServicesInterfaceCommonPartReference:
        """The low-level API material definition.

        Returns
        -------
        models.GrantaBomAnalyticsServicesInterfaceCommonPartReference
        """

        definition = super()._create_definition() or self._model(
            reference_type=ReferenceType.PartNumber.name, reference_value=self.part_number
        )
        return definition


class MaterialDefinition(RecordDefinition):
    """Concrete `RecordDefinition` subclass which represents a material record.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value. This class extends the base constructor to also support material ids.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.

    Attributes
    ----------
    material_id : str, optional
    _model : Type[models.Model]
        The low-level API class that defines this definition object.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.material_id: Union[str, None] = None
        if reference_type == ReferenceType.MaterialId:
            self.material_id = reference_value
        self._model = models.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference

    @property
    def definition(self) -> models.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference:
        """The low-level API part definition.

        Returns
        -------
        models.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference
        """

        definition = super()._create_definition() or self._model(
            reference_type=ReferenceType.MaterialId.name, reference_value=self.material_id
        )
        return definition


class SpecificationDefinition(RecordDefinition):
    """Concrete `RecordDefinition` subclass which represents a specification record.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value. This class extends the base constructor to also support specification
         ids.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.

    Attributes
    ----------
    specification_id : str, optional
    _model : Type[models.Model]
        The low-level API class that defines this definition object.
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.specification_id: Union[str, None] = None
        if reference_type == ReferenceType.SpecificationId:
            self.specification_id = reference_value
        self._model = models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference

    @property
    def definition(self) -> models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference:
        """The low-level API specification definition.

        Returns
        -------
        models.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference
        """

        definition = super()._create_definition() or self._model(
            reference_type=ReferenceType.SpecificationId.name, reference_value=self.specification_id
        )
        return definition


class BaseSubstanceDefinition(RecordDefinition, ABC):
    """Abstract `RecordDefinition` subclass which represents a generic substance record.

    Substance references come in multiple flavors, inputs, compliance results and impacted substance results quantify
    substances in slightly different ways. This class implements the reference aspects of the substance record only;
    the quantification are implemented in the sub-classes.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value. This class extends the base constructor to also support cas numbers,
        ec numbers, and chemical names.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.

    Attributes
    ----------
    chemical_name : str, optional
    cas_number : str, optional
    ec_number : str, optional
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.chemical_name: Union[str, None] = None
        self.cas_number: Union[str, None] = None
        self.ec_number: Union[str, None] = None
        if reference_type == ReferenceType.ChemicalName:
            self.chemical_name = reference_value
        elif reference_type == ReferenceType.CasNumber:
            self.cas_number = reference_value
        elif reference_type == ReferenceType.EcNumber:
            self.ec_number = reference_value


class SubstanceDefinition(BaseSubstanceDefinition):
    """Concrete substance subclass which represents the definition of a substance as supplied to a compliance query.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value. This class extends the base constructor to also support cas numbers,
        ec numbers, and chemical names.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    percentage_amount : float, optional
        The amount of the substance that appears in the parent Bom item. Should be greater than 0 and less than or
        equal to 100.

    Attributes
    ----------
    _model : Type[models.Model]
        The low-level API class that defines this definition object.
    """

    _default_percentage_amount = 100  # Default to worst case scenario

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
        percentage_amount: Union[float, None] = None,
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self._percentage_amount = None
        if percentage_amount:
            self.percentage_amount = percentage_amount
        self._model = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount  # noqa: E501
        )

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
        float
            Defaults to 100 if not set.
        """

        return self._percentage_amount or self.__class__._default_percentage_amount

    @percentage_amount.setter
    def percentage_amount(self, value: SupportsFloat):
        if not isinstance(value, SupportsFloat):
            raise TypeError(f'percentage_amount must be a number. Specified type was "{type(value)}"')
        value = float(value)
        if not 0.0 < value <= 100.0:
            raise ValueError(f'percentage_amount must be between 0 and 100. Specified value was "{value}"')
        self._percentage_amount = value

    @property
    def definition(self) -> models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount:
        """The low-level API substance definition.

        Returns
        -------
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount
        """

        definition = super()._create_definition()
        if not definition:
            if self.chemical_name:
                definition = self._model(
                    reference_type=ReferenceType.ChemicalName.name, reference_value=self.chemical_name
                )
            elif self.cas_number:
                definition = self._model(reference_type=ReferenceType.CasNumber.name, reference_value=self.cas_number)
            elif self.ec_number:
                definition = self._model(reference_type=ReferenceType.EcNumber.name, reference_value=self.ec_number)
        definition.percentage_amount = self.percentage_amount
        return definition


class BoM1711Definition:
    """Represents a Bom that is supplied as part of a Bom query.

    The XML contains record references within it, so there are no explicit references to records in this object.

    Parameters
    ----------
    bom : str
        The bill of materials in XML 1711 format.
    """

    def __init__(self, bom: Union[str, None] = None):
        super().__init__()
        self._bom = bom

    @property
    def definition(self) -> str:
        """The low-level API Bom definition. This is just a str.

        Returns
        -------
        str
        """
        return self._bom


class AbstractBomFactory:
    """Creates factories for a given type of API query. The key to control which definition is created is the
    request object in the low-level API.

    Class Attributes
    ----------------
    registry : dict
        Mapping between a factory class and the definition object it can create
    """

    registry = {}

    @classmethod
    def register(cls, request_types: List[Type[models.Model]]) -> Callable:
        """Decorator function to register a specific factory class with a low-level API request type.

        Parameters
        ----------
        request_types : list of Type[models.Model]

        Returns
        -------
        Callable
            The function that's being decorated.
        """

        def inner(item_factory: BomItemDefinitionFactory) -> BomItemDefinitionFactory:
            for request_type in request_types:
                cls.registry[request_type] = item_factory
            return item_factory

        return inner

    @classmethod
    def create_factory_for_request_type(cls, request_type: Type[models.Model]):
        """Factory method to instantiate and return a specific item definition factory.

        Parameters
        ----------
        request_type : Type[models.Model]
            The request type for which a definition is needed

        Returns
        -------
        BomItemDefinitionFactory
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

    These factories intentionally abstract away the concept of `ReferenceType` and expose separate static methods to
    create definitions based on a specific reference type, which more closely relates to the structure in the
    `queries.py` builder.
    """

    @staticmethod
    @abstractmethod
    def create_definition_by_record_history_identity(record_history_identity: int):
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_guid(record_guid: str):
        pass

    @staticmethod
    @abstractmethod
    def create_definition_by_record_history_guid(record_history_guid: str):
        pass


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest,
    ]
)
class MaterialDefinitionFactory(BomItemDefinitionFactory):
    """Creates material definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> MaterialDefinition:
        """Instantiate and return a `MaterialDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity : int

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
        record_history_guid : str

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
        record_guid : str

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_material_id(material_id) -> MaterialDefinition:
        """Instantiate and return a `MaterialDefinition` object based on the provided material ID.

        Parameters
        ----------
        material_id : str

        Returns
        -------
        MaterialDefinition
        """

        return MaterialDefinition(reference_type=ReferenceType.MaterialId, reference_value=material_id)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest,
    ]
)
class PartDefinitionFactory(BomItemDefinitionFactory):
    """Creates parat definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> PartDefinition:
        """Instantiate and return a `PartDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity : int

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
        record_history_guid : str

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
        record_guid : str

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_part_number(part_number) -> PartDefinition:
        """Instantiate and return a `PartDefinition` object based on the provided part number.

        Parameters
        ----------
        part_number : str

        Returns
        -------
        PartDefinition
        """

        return PartDefinition(reference_type=ReferenceType.PartNumber, reference_value=part_number)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest,
    ]
)
class SpecificationDefinitionFactory(BomItemDefinitionFactory):
    """Creates specification definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> SpecificationDefinition:
        """Instantiate and return a `SpecificationDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity : int

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
        record_history_guid : str

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
        record_guid : str

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_specification_id(specification_id) -> SpecificationDefinition:
        """Instantiate and return a `SpecificationDefinition` object based on the provided specification id.

        Parameters
        ----------
        specification_id : str

        Returns
        -------
        SpecificationDefinition
        """

        return SpecificationDefinition(reference_type=ReferenceType.SpecificationId, reference_value=specification_id)


@AbstractBomFactory.register([models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest])
class SubstanceComplianceDefinitionFactory(BomItemDefinitionFactory):
    """Creates substance compliance definition objects."""

    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided record history identity.

        Parameters
        ----------
        record_history_identity : int

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
        record_history_guid : str

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
        record_guid : str

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
        chemical_name : str

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.ChemicalName, reference_value=chemical_name)

    @staticmethod
    def create_definition_by_cas_number(cas_number: str) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided cas number.

        Parameters
        ----------
        cas_number : str

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.CasNumber, reference_value=cas_number)

    @staticmethod
    def create_definition_by_ec_number(ec_number: str) -> SubstanceDefinition:
        """Instantiate and return a `SubstanceDefinition` object based on the provided ec number.

        Parameters
        ----------
        ec_number : str

        Returns
        -------
        SubstanceDefinition
        """

        return SubstanceDefinition(reference_type=ReferenceType.EcNumber, reference_value=ec_number)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request,
    ]
)
class BomFactory:
    """Creates bom definition objects."""

    @staticmethod
    def create_definition(bom) -> BoM1711Definition:
        """Instantiate and return a `Bom1711Definition` object based on the provided bom.

        Parameters
        ----------
        bom : str

        Returns
        -------
        Bom1711Definition
        """

        return BoM1711Definition(bom=bom)
