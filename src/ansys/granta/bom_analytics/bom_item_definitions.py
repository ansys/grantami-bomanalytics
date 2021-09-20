from abc import ABC, abstractmethod
from typing import Callable, Type, Union, List, Dict

from ansys.granta.bomanalytics import models


class RecordDefinition(ABC):
    def __init__(
        self,
        record_history_identity: Union[int, None] = None,
        record_guid: Union[str, None] = None,
        record_history_guid: Union[str, None] = None,
        **kwargs,
    ):
        self.record_history_identity: int = record_history_identity
        self.record_guid: str = record_guid
        self.record_history_guid: str = record_history_guid
        self._model = None

    @classmethod
    def add_stk_records(
        cls, stk_records: List[Dict[str, str]]
    ):  # TODO: Finalize the stk interop format
        item_references = []
        for record in stk_records:
            assert "db_key" in record
            assert "record_guid" in record

            item_references.append(cls(record_guid=record["record_guid"]))
        return item_references

    def _create_definition(self):
        if self.record_guid:
            return self._model(
                reference_type="MiRecordGuid", reference_value=self.record_guid
            )
        if self.record_history_guid:
            return self._model(
                reference_type="MiRecordHistoryGuid",
                reference_value=self.record_history_guid,
            )
        if self.record_history_identity:
            return self._model(
                reference_type="MiRecordHistoryIdentity",
                reference_value=self.record_history_identity,
            )

    @property
    @abstractmethod
    def definition(self):
        pass


class PartDefinition(RecordDefinition):
    def __init__(
        self,
        record_history_identity: Union[str, None] = None,
        record_guid: Union[str, None] = None,
        record_history_guid: Union[str, None] = None,
        part_number: Union[str, None] = None,
        **kwargs,
    ):
        super().__init__(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
            **kwargs,
        )
        self.part_number: str = part_number
        self._model = models.GrantaBomAnalyticsServicesInterfaceCommonPartReference

    @property
    def definition(self) -> models.Model:
        definition = super()._create_definition() or self._model(
            reference_type="PartNumber", reference_value=self.part_number
        )
        return definition


class MaterialDefinition(RecordDefinition):
    def __init__(
        self,
        material_id: Union[str, None] = None,
        record_history_identity: Union[int, None] = None,
        record_guid: Union[str, None] = None,
        record_history_guid: Union[str, None] = None,
        **kwargs,
    ):
        super().__init__(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
            **kwargs,
        )
        self.material_id: str = material_id
        self._model = models.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference

    @property
    def definition(self) -> models.Model:
        definition = super()._create_definition() or self._model(
            reference_type="MaterialId", reference_value=self.material_id
        )
        return definition


class SpecificationDefinition(RecordDefinition):
    def __init__(
        self,
        specification_id: Union[str, None] = None,
        record_history_identity: Union[int, None] = None,
        record_guid: Union[str, None] = None,
        record_history_guid: Union[str, None] = None,
        **kwargs,
    ):
        super().__init__(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
            **kwargs,
        )
        self.specification_id: str = specification_id
        self._model = (
            models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference
        )

    @property
    def definition(self) -> models.Model:
        definition = super()._create_definition() or self._model(
            reference_type="SpecificationId", reference_value=self.specification_id
        )
        return definition


class BaseSubstanceDefinition(RecordDefinition, ABC):
    def __init__(
        self,
        chemical_name=None,
        cas_number=None,
        ec_number=None,
        record_history_identity=None,
        record_guid=None,
        record_history_guid=None,
    ):
        super().__init__(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
        )
        self.chemical_name: str = chemical_name
        self.cas_number: str = cas_number
        self.ec_number: str = ec_number

    @property
    def definition(self) -> models.Model:
        return models.Model()


class SubstanceDefinition(BaseSubstanceDefinition):
    _default_percentage_amount = 100  # Default to worst case scenario

    def __init__(
        self,
        chemical_name=None,
        cas_number=None,
        ec_number=None,
        record_history_identity=None,
        record_guid=None,
        record_history_guid=None,
        percentage_amount=None,
        **kwargs,
    ):
        super().__init__(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
            **kwargs,
        )
        self.chemical_name = chemical_name
        self.cas_number = cas_number
        self.ec_number = ec_number
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
            raise ValueError(
                'percentage_amount must be between 0 and 100. Specified value was "{value}"'
            )
        self._percentage_amount = value

    @property
    def definition(self) -> models.Model:
        definition = super()._create_definition()
        if not definition:
            if self.chemical_name:
                definition = self._model(
                    reference_type="ChemicalName", reference_value=self.chemical_name
                )
            elif self.cas_number:
                definition = self._model(
                    reference_type="CasNumber", reference_value=self.cas_number
                )
            elif self.ec_number:
                definition = self._model(
                    reference_type="EcNumber", reference_value=self.ec_number
                )
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
    def create_factory_for_request_type(
        cls, request_type: Type[models.Model], **kwargs
    ):
        try:
            item_factory_class = cls.registry[request_type]
        except KeyError as e:
            raise RuntimeError(
                f'Unregistered request type "{request_type}"'
            ).with_traceback(e.__traceback__)
        item_factory = item_factory_class(**kwargs)
        return item_factory


class BomItemDefinitionFactory(ABC):
    @abstractmethod
    def create_bom_item_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ):
        pass


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest,
    ]
)
class MaterialDefinitionFactory(BomItemDefinitionFactory, ABC):
    def create_bom_item_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> MaterialDefinition:
        return MaterialDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
        )

    @staticmethod
    def create_definition_by_material_id(material_id) -> MaterialDefinition:
        return MaterialDefinition(material_id=material_id)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest,
    ]
)
class PartDefinitionFactory(BomItemDefinitionFactory, ABC):
    def create_bom_item_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> PartDefinition:
        return PartDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
        )

    @staticmethod
    def create_definition_by_part_number(part_number) -> PartDefinition:
        return PartDefinition(part_number=part_number)


@AbstractBomFactory.register(
    [
        models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest,
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest,
    ]
)
class SpecificationDefinitionFactory(BomItemDefinitionFactory, ABC):
    def create_bom_item_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> SpecificationDefinition:
        return SpecificationDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
        )

    @staticmethod
    def create_definition_by_specification_id(
        specification_id,
    ) -> SpecificationDefinition:
        return SpecificationDefinition(specification_id=specification_id)


@AbstractBomFactory.register(
    [models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest]
)
class SubstanceComplianceDefinitionFactory(BomItemDefinitionFactory):
    def create_bom_item_definition(
        self, record_history_identity=None, record_history_guid=None, record_guid=None
    ) -> SubstanceDefinition:
        return SubstanceDefinition(
            record_history_identity=record_history_identity,
            record_guid=record_guid,
            record_history_guid=record_history_guid,
            percentage_amount=100,
        )

    @staticmethod
    def create_definition_by_chemical_name(value) -> SubstanceDefinition:
        return SubstanceDefinition(chemical_name=value)

    @staticmethod
    def create_definition_by_cas_number(value) -> SubstanceDefinition:
        return SubstanceDefinition(cas_number=value)

    @staticmethod
    def create_definition_by_ec_number(value) -> SubstanceDefinition:
        return SubstanceDefinition(ec_number=value)


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
