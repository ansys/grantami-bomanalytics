from abc import ABC, abstractmethod
from typing import Callable, Type, Union, List, Dict
from enum import Enum, auto

from ansys.granta.bomanalytics import models


class ReferenceType(Enum):
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

    @classmethod
    def add_stk_records(cls, stk_records: List[Dict[str, str]]):  # TODO: Finalize the stk interop format
        item_references = []
        for record in stk_records:
            assert "db_key" in record
            assert "record_guid" in record

            item_references.append(
                cls(reference_type=ReferenceType.MiRecordGuid, reference_value=record["record_guid"])
            )
        return item_references

    def _create_definition(self):
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
    def definition(self) -> models.Model:
        definition = super()._create_definition() or self._model(
            reference_type=ReferenceType.PartNumber.name, reference_value=self.part_number
        )
        return definition


class MaterialDefinition(RecordDefinition):
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
    def definition(self) -> models.Model:
        definition = super()._create_definition() or self._model(
            reference_type=ReferenceType.MaterialId.name, reference_value=self.material_id
        )
        return definition


class SpecificationDefinition(RecordDefinition):
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
    def definition(self) -> models.Model:
        definition = super()._create_definition() or self._model(
            reference_type=ReferenceType.SpecificationId.name, reference_value=self.specification_id
        )
        return definition


class BaseSubstanceDefinition(RecordDefinition, ABC):
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

    @property
    def definition(self) -> models.Model:
        return models.Model()


class SubstanceDefinition(BaseSubstanceDefinition):
    _default_percentage_amount = 100  # Default to worst case scenario

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
        percentage_amount=None,
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
        return self._percentage_amount or self.__class__._default_percentage_amount

    @percentage_amount.setter
    def percentage_amount(self, value: float):
        if not 0 <= value <= 100:
            raise ValueError('percentage_amount must be between 0 and 100. Specified value was "{value}"')
        self._percentage_amount = value

    @property
    def definition(self) -> models.Model:
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
    def __init__(self, bom: Union[str, None] = None):
        super().__init__()
        self._bom = bom

    @property
    def definition(self) -> str:
        return self._bom


class AbstractBomFactory:
    registry = {}

    @classmethod
    def register(cls, request_types: List[Type[models.Model]]) -> Callable:
        def inner(item_factory: BomItemDefinitionFactory) -> BomItemDefinitionFactory:
            for request_type in request_types:
                cls.registry[request_type] = item_factory
            return item_factory

        return inner

    @classmethod
    def create_factory_for_request_type(cls, request_type: Type[models.Model], **kwargs):
        try:
            item_factory_class = cls.registry[request_type]
        except KeyError as e:
            raise RuntimeError(f'Unregistered request type "{request_type}"').with_traceback(e.__traceback__)
        item_factory = item_factory_class(**kwargs)
        return item_factory


class BomItemDefinitionFactory(ABC):
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
class MaterialDefinitionFactory(BomItemDefinitionFactory, ABC):
    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> MaterialDefinition:
        return MaterialDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> MaterialDefinition:
        return MaterialDefinition(reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid)

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> MaterialDefinition:
        return MaterialDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_material_id(material_id) -> MaterialDefinition:
        return MaterialDefinition(reference_type=ReferenceType.MaterialId, reference_value=material_id)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest,
    ]
)
class PartDefinitionFactory(BomItemDefinitionFactory, ABC):
    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> PartDefinition:
        return PartDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> PartDefinition:
        return PartDefinition(reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid)

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> PartDefinition:
        return PartDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_part_number(part_number) -> PartDefinition:
        return PartDefinition(reference_type=ReferenceType.PartNumber, reference_value=part_number)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest,
    ]
)
class SpecificationDefinitionFactory(BomItemDefinitionFactory, ABC):
    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> SpecificationDefinition:
        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> SpecificationDefinition:
        return SpecificationDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> SpecificationDefinition:
        return SpecificationDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_specification_id(specification_id) -> SpecificationDefinition:
        return SpecificationDefinition(reference_type=ReferenceType.SpecificationId, reference_value=specification_id)


@AbstractBomFactory.register([models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest])
class SubstanceComplianceDefinitionFactory(BomItemDefinitionFactory):
    @staticmethod
    def create_definition_by_record_history_identity(record_history_identity: int) -> SubstanceDefinition:
        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryIdentity, reference_value=record_history_identity
        )

    @staticmethod
    def create_definition_by_record_history_guid(record_history_guid: str) -> SubstanceDefinition:
        return SubstanceDefinition(
            reference_type=ReferenceType.MiRecordHistoryGuid, reference_value=record_history_guid
        )

    @staticmethod
    def create_definition_by_record_guid(record_guid: str) -> SubstanceDefinition:
        return SubstanceDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value=record_guid)

    @staticmethod
    def create_definition_by_chemical_name(chemical_name: str) -> SubstanceDefinition:
        return SubstanceDefinition(reference_type=ReferenceType.ChemicalName, reference_value=chemical_name)

    @staticmethod
    def create_definition_by_cas_number(cas_number: str) -> SubstanceDefinition:
        return SubstanceDefinition(reference_type=ReferenceType.CasNumber, reference_value=cas_number)

    @staticmethod
    def create_definition_by_ec_number(ec_number: str) -> SubstanceDefinition:
        return SubstanceDefinition(reference_type=ReferenceType.EcNumber, reference_value=ec_number)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request,
    ]
)
class BomFactory:
    @staticmethod
    def create_definition(bom) -> BoM1711Definition:
        return BoM1711Definition(bom=bom)
