from abc import ABC, abstractmethod
from typing import Union

from ansys.granta import bomanalytics


class ItemReference(ABC):
    def __init__(self,
                 record_history_identity: Union[int, None],
                 record_guid: Union[str, None],
                 record_history_guid: Union[str, None]):
        self._record_history_identity = record_history_identity
        self._record_guid = record_guid
        self._record_history_guid = record_history_guid
        self._model = None

    def _create_definition(self):
        if self._record_history_identity:
            return self._model(reference_type="MiRecordHistoryIdentity", reference_value=self._record_history_identity)
        if self._record_guid:
            return self._model(reference_type="MiRecordGuid", reference_value=self._record_guid)
        if self._record_history_guid:
            return self._model(reference_type="MiRecordHistoryGuid", reference_value=self._record_history_guid)

    @property
    @abstractmethod
    def definition(self):
        pass


class BoM1711Reference(ItemReference):
    def __init__(self, bom: Union[str, None] = None):
        super().__init__(None, None, None)
        self._bom = bom

    @property
    def definition(self):
        return self._bom


class PartReference(ItemReference):
    def __init__(self,
                 part_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._part_id = part_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonPartReference

    @property
    def definition(self):
        definition = super()._create_definition() or self._model(reference_type="PartId", reference_value=self._part_id)
        return definition


class MaterialReference(ItemReference):
    def __init__(self,
                 material_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._material_id = material_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference

    @property
    def definition(self):
        definition = super()._create_definition() or \
                     self._model(reference_type="MaterialId", reference_value=self._material_id)
        return definition


class SpecificationReference(ItemReference):
    def __init__(self,
                 specification_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._specification_id = specification_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference

    @property
    def definition(self):
        definition = super()._create_definition() or \
                     self._model(reference_type="SpecificationId", reference_value=self._specification_id)
        return definition


class SubstanceReference(ItemReference):
    def __init__(self,
                 substance_name=None,
                 cas_number=None,
                 ec_number=None,
                 record_history_identity=None,
                 record_guid=None,
                 record_history_guid=None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self._substance_name = substance_name
        self._cas_number = cas_number
        self._ec_number = ec_number
        self._percentage_threshold = None
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount

    @property
    def percentage_threshold(self) -> float:
        return self._percentage_threshold

    @percentage_threshold.setter
    def percentage_threshold(self, value: float):
        assert 0 < value < 100
        self._percentage_threshold = value

    @property
    def definition(self):
        if self._record_history_identity:
            return self._model(reference_type="MiRecordHistoryIdentity", reference_value=self._record_history_identity,
                               percentage_amount=self._percentage_threshold)
        if self._record_guid:
            return self._model(reference_type="MiRecordGuid", reference_value=self._record_guid,
                               percentage_amount=self._percentage_threshold)
        if self._record_history_guid:
            return self._model(reference_type="MiRecordHistoryGuid", reference_value=self._record_history_guid,
                               percentage_amount=self._percentage_threshold)
        if self._substance_name:
            return self._model(reference_type="SubstanceName", reference_value=self._substance_name,
                               percentage_amount=self._percentage_threshold)
        if self._cas_number:
            return self._model(reference_type="CasNumber", reference_value=self._cas_number,
                               percentage_amount=self._percentage_threshold)
        if self._ec_number:
            return self._model(reference_type="EcNumber", reference_value=self._ec_number,
                               percentage_amount=self._percentage_threshold)