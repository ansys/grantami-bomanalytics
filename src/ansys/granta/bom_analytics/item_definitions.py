from abc import ABC, abstractmethod
from typing import Union, List, Dict

from ansys.granta import bomanalytics
from ansys.granta.bomanalytics.models import Model


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
            assert "dbkey" in record
            assert "record_guid" in record

            item_references.append(cls(record_guid=record["record_guid"]))
        return item_references

    def _create_definition(self):
        if self.record_history_identity:
            return self._model(
                reference_type="MiRecordHistoryIdentity",
                reference_value=self.record_history_identity,
            )
        if self.record_guid:
            return self._model(
                reference_type="MiRecordGuid", reference_value=self.record_guid
            )
        if self.record_history_guid:
            return self._model(
                reference_type="MiRecordHistoryGuid",
                reference_value=self.record_history_guid,
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
            record_history_identity, record_guid, record_history_guid, **kwargs
        )
        self.part_number: str = part_number
        self._model = (
            bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonPartReference
        )

    @property
    def definition(self) -> Model:
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
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.material_id: str = material_id
        self._model = (
            bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference
        )

    @property
    def definition(self) -> Model:
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
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.specification_id: str = specification_id
        self._model = (
            bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference
        )

    @property
    def definition(self) -> Model:
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
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.chemical_name: str = chemical_name
        self.cas_number: str = cas_number
        self.ec_number: str = ec_number

    @property
    def definition(self) -> Model:
        return Model()


class SubstanceDefinition(BaseSubstanceDefinition):
    default_percentage_amount = 100  # Default to worst case scenario

    def __init__(
        self,
        chemical_name=None,
        cas_number=None,
        ec_number=None,
        record_history_identity=None,
        record_guid=None,
        record_history_guid=None,
        percentage_amount=None,
    ):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.chemical_name = chemical_name
        self.cas_number = cas_number
        self.ec_number = ec_number
        self._percentage_amount = None
        if percentage_amount:
            self.percentage_amount = percentage_amount
        self._model = (
            bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount  # noqa: E501
        )

    @property
    def percentage_amount(self) -> float:
        if self._percentage_amount:
            return self._percentage_amount
        else:
            return self.__class__.default_percentage_amount

    @percentage_amount.setter
    def percentage_amount(self, value: float):
        assert 0 <= value <= 100
        self._percentage_amount = value

    @property
    def definition(self) -> Model:
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
