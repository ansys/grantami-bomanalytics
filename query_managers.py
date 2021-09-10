from abc import ABC, abstractmethod
from typing import Union, List, Dict, Callable
from enum import Enum

from ansys.granta.bomanalytics import models
from item_references import RecordDefinition, MaterialDefinition, PartDefinition, SpecificationDefinition, \
    SubstanceDefinition, BoM1711Definition, LegislationDefinition
from item_references import PartResult, MaterialResult, SpecificationResult, SubstanceResult, LegislationResult

register_dict = {
    'materials': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest,
                  'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest},
    'parts': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest,
              'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest},
    'specifications': {
        'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest,
        'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest},
    'substances': {
        'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest},
    'bom_xml1711': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request,
                    'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request}
}


class ReferenceTypes(Enum):
    record_history_identity = 0
    MiRecordHistoryIdentity = 0
    record_history_guid = 1
    MiRecordHistoryGuid = 1
    record_guid = 2
    MiRecordGuid = 2
    material_id = 10
    MaterialId = 10
    part_number = 20
    PartNumber = 20
    specification_id = 30
    SpecificationId = 30
    substance_name = 40
    ChemicalName = 40
    cas_number = 41
    CasNumber = 41
    ec_number = 42
    EcNumber = 42


class BaseQueryBuilder(ABC):
    _item_type_name = None
    _item_type: Union[Callable, None] = None
    _result_type: Union[Callable, None] = None

    def __init__(self, connection):
        super().__init__()
        self._connection = connection
        self._is_result_current = False

    @property
    @abstractmethod
    def _content(self) -> List[List[models.Model]]:
        for i in range(0, len(self._items), self._batch_size):
            yield [i.definition for i in self._items][i:i + self._batch_size]


class RecordBasedQueryManager(BaseQueryBuilder, ABC):
    _default_batch_size: int = None
    _item_type: RecordDefinition = None

    def __init__(self, connection):
        super().__init__(connection)
        self._items: List[RecordDefinition] = []
        self._batch_size = self.__class__._default_batch_size

    def _create_definition(self, key: ReferenceTypes, value: Union[str, int]):
        return self._create_definition_or_result(key, value, self._item_type)

    def _create_result(self, key: ReferenceTypes, value: Union[str, int]):
        return self._create_definition_or_result(key, value, self._result_type)

    @abstractmethod
    def _create_definition_or_result(self, key: ReferenceTypes, value: Union[str, int], item_type):
        if key == ReferenceTypes.record_history_identity:
            item_reference = item_type.add_record_by_record_history_identity(value)
        elif key == ReferenceTypes.record_history_guid:
            item_reference = item_type.add_record_by_record_history_guid(value)
        elif key == ReferenceTypes.record_guid:
            item_reference = item_type.add_record_by_record_guid(value)
        else:
            raise RecordInstantiationException
        return item_reference

    def add_record(self, key: ReferenceTypes, value: Union[str, int]):
        item_reference = self._create_definition(key, value)
        self._items.append(item_reference)

    def add_stk_records(self, stk_records: List[Dict[str, str]]):
        for record in stk_records:
            assert 'dbkey' in record
            assert 'record_guid' in record

            if not self._connection.dbkey:
                self._connection.dbkey = record['dbkey']
            else:
                assert record['dbkey'] == self._connection.dbkey
            item_reference = self._item_type.add_record_by_record_guid(record['record_guid'])
            self._items.append(item_reference)

    @property
    def batch_size(self):
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: int):
        assert value > 0
        self._batch_size = value

    @property
    def _content(self) -> List[List[models.Model]]:
        for i in range(0, len(self._items), self._batch_size):
            yield [i.definition for i in self._items][i:i + self._batch_size]


class RecordInstantiationException(Exception):
    pass


class ComplianceMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._indicators = []
        self._compliance_api = None
        self._compliance_request_type = register_dict[self._item_type_name]['compliance_request_type']
        self._compliance = None

    def set_compliance_api(self, api):
        self._compliance_api = api

    def add_indicator(self, value):
        self._indicators.append(value)

    @property
    def _compliance_args(self):
        return {'database_key': self._connection.dbkey,
                'indicators': [i.definition for i in self._indicators],
                'config': self._connection.query_config}

    @property
    def compliance(self):
        if not self._is_result_current:
            self.get_compliance()
        return self._compliance

    def get_compliance(self) -> None:
        assert self._compliance_api
        if not self._indicators:
            return

        self._compliance = []

        for batch in self._content:
            args = {**self._compliance_args, self._item_type_name: batch}
            request = self._compliance_request_type(**args)
            response = self._compliance_api(body=request)
            self.__build_result_object(response)
        self._is_result_current = True

    def __build_result_object(self, response):
        for resp in getattr(response, self._item_type_name):
            obj = self._create_result(key=ReferenceTypes[resp.reference_type], value=resp.reference_value)
            try:
                obj.add_compliance(substances=resp.substances,
                                   indicators=resp.indicators,
                                   indicator_definitions=self._indicators)
            except AttributeError:
                obj.add_compliance(indicators=resp.indicators, indicator_definitions=self._indicators)
            self._compliance.append(obj)


class ImpactedSubstanceMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._legislations = []
        self._impacted_substances_api = None
        self._impacted_substances_request_type = register_dict[self._item_type_name]['impacted_substances_request_type']
        self._impacted_substances = None

    def set_impacted_substance_api(self, api):
        self._impacted_substances_api = api

    def add_legislation(self, legislation_name):
        self._legislations.append(LegislationDefinition(legislation_name))

    @property
    def impacted_substances(self):
        if not self._is_result_current:
            self.get_impacted_substances()
        return self._impacted_substances

    @property
    def _impacted_substances_args(self):
        return {'database_key': self._connection.dbkey,
                'legislation_names': [legislation.definition for legislation in self._legislations],
                'config': self._connection.query_config}

    def get_impacted_substances(self) -> None:
        assert self._impacted_substances_api
        if not self._legislations:
            return

        self._impacted_substances = []

        for batch in self._content:
            args = {**self._impacted_substances_args, self._item_type_name: batch}
            request = self._impacted_substances_request_type(**args)
            response = self._impacted_substances_api(body=request)
            self.__build_result_object(response)
        self._is_result_current = True

    def __build_result_object(self, response):
        for resp in getattr(response, self._item_type_name):
            obj = self._create_result(key=ReferenceTypes[resp.reference_type], value=resp.reference_value)
            obj.add_substances(resp.legislations)
            self._impacted_substances.append(obj)


class MaterialQueryManager(RecordBasedQueryManager, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'materials'
    _item_type = MaterialDefinition
    _result_type = MaterialResult
    _default_batch_size = 1

    def _create_definition_or_result(self, key: ReferenceTypes, value: Union[str, int], item_type):
        if key == ReferenceTypes.material_id:
            item_reference = item_type.add_record_by_material_id(value)
        else:
            item_reference = super()._create_definition_or_result(key, value, item_type)
        return item_reference


class PartQueryManager(RecordBasedQueryManager, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'parts'
    _item_type = PartDefinition
    _result_type = PartResult
    _default_batch_size = 1

    def _create_definition_or_result(self, key: ReferenceTypes, value: Union[str, int], item_type):
        if key == ReferenceTypes.part_number:
            item_reference = item_type.add_record_by_part_number(value)
        else:
            item_reference = super()._create_definition_or_result(key, value, item_type)
        return item_reference

    def add_record_by_part_number(self, value) -> None:
        part_reference = self._item_type(part_number=value)
        self._items.append(part_reference)


class SpecificationQueryManager(RecordBasedQueryManager, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'specifications'
    _item_type = SpecificationDefinition
    _result_type = SpecificationResult
    _default_batch_size = 1

    def _create_definition_or_result(self, key: ReferenceTypes, value: Union[str, int], item_type):
        if key == ReferenceTypes.specification_id:
            item_reference = item_type.add_record_by_specification_id(value)
        else:
            item_reference = super()._create_definition_or_result(key, value, item_type)
        return item_reference

    def add_record_by_specification_id(self, value) -> None:
        spec_reference = self._item_type(specification_id=value)
        self._items.append(spec_reference)


class SubstanceQueryManager(RecordBasedQueryManager, ComplianceMixin):
    _item_type_name = 'substances'
    _item_type = SubstanceDefinition
    _result_type = SubstanceResult
    _default_batch_size = 1

    def add_record(self, key: ReferenceTypes, value: Union[str, int]):  # TODO Re-evaluate this decision
        item_reference = self._create_definition(key, value)
        item_reference.percentage_amount = 100
        self._items.append(item_reference)

    def add_substance_with_amount(self, key: ReferenceTypes, value: Union[str, int], percentage_amount: [float]):
        item_reference = self._create_definition(key, value)
        item_reference.percentage_amount = percentage_amount
        self._items.append(item_reference)

    def _create_definition_or_result(self, key: ReferenceTypes, value: Union[str, int], item_type):
        if key == ReferenceTypes.substance_name:
            item_reference = item_type.add_record_by_substance_name(value)
        elif key == ReferenceTypes.cas_number:
            item_reference = item_type.add_record_by_cas_number(value)
        elif key == ReferenceTypes.ec_number:
            item_reference = item_type.add_record_by_ec_number(value)
        else:
            item_reference = super()._create_definition_or_result(key, value, item_type)
        return item_reference


class BoM1711QueryManager(BaseQueryBuilder, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'bom_xml1711'
    _item_type = BoM1711Definition
    _default_batch_size = 1

    def __init__(self, connection):
        super().__init__(connection)
        self._bom: Union[RecordDefinition, None] = None

    @property
    def _content(self) -> str:
        return self._bom.definition

    @property
    def bom(self) -> None:
        return self._bom

    @bom.setter
    def bom(self, value: str) -> None:
        bom = self._item_type(bom=value)
        self._bom = bom

    def get_compliance(self) -> None:
        assert self._compliance_api
        if not self._indicators:
            return

        args = {**self._compliance_args, self._item_type_name: self._content}
        request = self._compliance_request_type(**args)
        response = self._compliance_api(body=request)
        self._compliance = response.parts
        self._is_result_current = True

    def get_impacted_substances(self) -> None:
        assert self._impacted_substances_api
        if not self._legislations:
            return

        args = {**self._impacted_substances_args, self._item_type_name: self._content}
        request = self._impacted_substances_request_type(**args)
        response = self._impacted_substances_api(body=request)
        self._impacted_substances = {legislation.legislation_name: LegislationResult(legislation.legislation_name,
                                                                                     legislation.impacted_substances)
                                     for legislation in response.legislations}
        self._is_result_current = True
