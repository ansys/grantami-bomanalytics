from abc import ABC, abstractmethod
from typing import Union, List, Dict, Callable, Tuple

from ansys.granta.bomanalytics import models

from item_factories import (RecordFactory,
                            MaterialImpactedSubstancesFactory,
                            MaterialComplianceFactory,
                            PartComplianceFactory,
                            PartImpactedSubstancesFactory,
                            SpecificationComplianceFactory,
                            SpecificationImpactedSubstancesFactory,
                            SubstanceComplianceFactory,
                            BomImpactedSubstancesFactory,
                            BomComplianceFactory,
                            )
from item_definitions import Indicator


class BaseQueryBuilder(ABC):
    _item_type_name = None
    _result_type: Union[Callable, None] = None

    def __init__(self, connection):
        super().__init__()
        self._connection = connection


class RecordBasedQueryManager(BaseQueryBuilder, ABC):
    def __init__(self, connection):
        self._batch_size = None
        self._items = []
        self._definition_factory: Union[RecordFactory, None] = None
        super().__init__(connection)

    def add_record_history_ids(self, values: List[int]):
        for value in values:
            item_reference = self._definition_factory.create_definition(record_history_identity=value)
            self._items.append(item_reference)
        return self

    def add_record_history_guids(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_definition(record_history_guid=value)
            self._items.append(item_reference)
        return self

    def add_record_guids(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_definition(record_guid=value)
            self._items.append(item_reference)
        return self

    def add_stk_records(self, stk_records: List[Dict[str, str]]):
        record_guids = [r['record_guid'] for r in stk_records]
        self.add_record_guids(record_guids)
        return self

    @property
    def batch_size(self):
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: int):
        assert value > 0
        self._batch_size = value

    @property
    def _content(self) -> List[List[models.Model]]:
        for i in range(0, len(self._items), self.batch_size):
            yield [i.definition for i in self._items][i:i + self.batch_size]


class ApiMixin(ABC):
    _items = None  # Implemented by main class
    _content = None

    def __init__(self, **kwargs):
        self._api = None
        self._connection = None
        self._request_type = None
        self._item_type_name = None
        self._definition_factory = None

    def execute(self):
        self._validate_query()
        result = self._run_query()
        return self._definition_factory.create_result(result)

    @abstractmethod
    def _validate_query(self):
        assert self._connection

    def _run_query(self) -> List:
        result = []
        for batch in self._content:
            args = {**self._arguments, self._item_type_name: batch}
            request = self._request_type(**args)
            response = self._api(body=request)
            result.extend([r for r in getattr(response, self._item_type_name)])
        return result

    @property
    @abstractmethod
    def _arguments(self) -> Dict:
        pass


class ComplianceMixin(ApiMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._indicators = []

    def add_indicators(self, values: List[Indicator]):
        for value in values:
            self._indicators.append(value)
        return self

    def _validate_query(self):
        assert self._indicators
        super()._validate_query()

    @property
    def _arguments(self):
        return {'database_key': self._connection.dbkey,
                'indicators': [i.definition for i in self._indicators],
                'config': self._connection.query_config}


class ImpactedSubstanceMixin(ApiMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._legislations: List[str] = []

    def add_legislations(self, legislation_names: List[str]):
        self._legislations.extend(legislation_names)
        return self

    def _validate_query(self):
        assert self._legislations
        super()._validate_query()

    @property
    def _arguments(self):
        return {'database_key': self._connection.dbkey,
                'legislation_names': self._legislations,
                'config': self._connection.query_config}


class MaterialQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, connection):
        super().__init__(connection)
        self._batch_size = 1
        self._item_type_name = 'materials'
        self._definition_factory: Union[None, MaterialComplianceFactory, MaterialImpactedSubstancesFactory] = None

    def add_material_ids(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_definition_by_material_id(value)
            self._items.append(item_reference)
        return self


class MaterialComplianceQuery(MaterialQueryManager, ComplianceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest
        self._api = self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_materials
        self._definition_factory = MaterialComplianceFactory()


class MaterialImpactedSubstanceQuery(MaterialQueryManager, ImpactedSubstanceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest
        self._api = self._connection.impacted_substances_api.\
            post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials
        self._definition_factory = MaterialImpactedSubstancesFactory()


class PartQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, connection):
        super().__init__(connection)
        self._batch_size = 1
        self._item_type_name = 'parts'
        self._definition_factory: Union[None, PartComplianceFactory, PartImpactedSubstancesFactory] = None

    def add_part_numbers(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_definition_by_part_number(value)
            self._items.append(item_reference)
        return self


class PartComplianceQuery(PartQueryManager, ComplianceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest
        self._api = self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_parts
        self._definition_factory = PartComplianceFactory()


class PartImpactedSubstanceQuery(PartQueryManager, ImpactedSubstanceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest
        self._api = self._connection.impacted_substances_api.\
            post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts
        self._definition_factory = PartImpactedSubstancesFactory()


class SpecificationQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, connection):
        super().__init__(connection)
        self._batch_size = 1
        self._item_type_name = 'specifications'
        self._definition_factory: Union[None,
                                        SpecificationComplianceFactory,
                                        SpecificationImpactedSubstancesFactory] = None

    def add_specification_ids(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_definition_by_specification_id(value)
            self._items.append(item_reference)
        return self


class SpecificationComplianceQuery(SpecificationQueryManager, ComplianceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest
        self._api = self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_specifications
        self._definition_factory = SpecificationComplianceFactory()


class SpecificationImpactedSubstanceQuery(SpecificationQueryManager, ImpactedSubstanceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest
        self._api = self._connection.impacted_substances_api.\
            post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications
        self._definition_factory = SpecificationImpactedSubstancesFactory()


class SubstanceQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, connection):
        super().__init__(connection)
        self._batch_size = 1
        self._item_type_name = 'substances'
        self._definition_factory: Union[None, SubstanceComplianceFactory] = None

    def add_cas_numbers(self, values: List[str]):
        for cas_number in values:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number)
            self._items.append(item_reference)
        return self

    def add_ec_numbers(self, values: List[str]):
        for ec_number in values:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number)
            self._items.append(item_reference)
        return self

    def add_substance_names(self, values: List[str]):
        for substance_name in values:
            item_reference = self._definition_factory.create_definition_by_substance_name(substance_name)
            self._items.append(item_reference)
        return self

    def add_record_history_ids_with_amounts(self, values: List[Tuple[int, float]]):
        for record_history_id, amount in values:
            item_reference = self._definition_factory.create_definition(record_history_identity=record_history_id)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_record_history_guids_with_amounts(self, values: List[Tuple[str, float]]):
        for record_history_guid, amount in values:
            item_reference = self._definition_factory.create_definition(record_history_guid=record_history_guid)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_record_guids_with_amounts(self, values: List[Tuple[str, float]]):
        for record_guid, amount in values:
            item_reference = self._definition_factory.create_definition(record_guid=record_guid)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_cas_numbers_with_amounts(self, values: List[Tuple[str, float]]):
        for cas_number, amount in values:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_ec_numbers_with_amounts(self, values: List[Tuple[str, float]]):
        for ec_number, amount in values:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_substance_names_with_amounts(self, values: List[Tuple[str, float]]):
        for substance_name, amount in values:
            item_reference = self._definition_factory.create_definition_by_substance_name(substance_name)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self


class SubstanceComplianceQuery(SubstanceQueryManager, ComplianceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest
        self._api = self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_substances
        self._definition_factory = SubstanceComplianceFactory()


class BoM1711QueryManager(BaseQueryBuilder, ABC):
    def __init__(self, connection):
        super().__init__(connection)
        self._batch_size = 1
        self._item_type_name = 'bom_xml1711'
        self._definition_factory: Union[None, BomComplianceFactory, BomImpactedSubstancesFactory] = None
        self._bom = None

    @property
    def _content(self) -> str:
        return self._bom.definition

    def set_bom(self, value: str):
        self._bom = self._definition_factory.create_definition(bom=value)
        return self

    def _run_query(self) -> None:
        args = {**self._arguments, self._item_type_name: self._content}
        request = self._request_type(**args)
        response = self._api(body=request)
        return response


class BoMComplianceQuery(BoM1711QueryManager, ComplianceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request
        self._api = self._connection.compliance_api.\
            post_miservicelayer_bom_analytics_v1svc_compliance_bom1711
        self._definition_factory = BomComplianceFactory()


class BoMImpactedSubstancesQuery(BoM1711QueryManager, ImpactedSubstanceMixin):
    def __init__(self, connection):
        super().__init__(connection)
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request
        self._api = self._connection.impacted_substances_api.\
            post_miservicelayer_bom_analytics_v1svc_impactedsubstances_bom1711
        self._definition_factory = BomImpactedSubstancesFactory()
