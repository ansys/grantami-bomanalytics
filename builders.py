from abc import ABC
from typing import Union, List, Dict, Callable

from ansys.granta.bomanalytics import models
from item_references import ItemReference, MaterialReference, PartReference, SpecificationReference, \
    SubstanceReference, BoM1711Reference

register_dict = {'materials': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest,
                              'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest},
                 'parts': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest,
                          'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest},
                 'specifications': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest,
                                   'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest},
                 'substances': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest},
                 'bom_xml1711': {'compliance_request_type': models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request,
                             'impacted_substances_request_type': models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request}
                 }


class BaseQueryBuilder(ABC):
    _item_type_name = None
    _item_type: Union[Callable, None] = None

    def __init__(self, connection):
        super().__init__()
        self._connection = connection


class SingleItemMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._item: Union[ItemReference, None] = None

    @property
    def _content(self):
        return self._item.definition


class MultipleRecordItemMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._items: List[ItemReference] = []

    def add_record_by_record_history_identity(self, value):
        item_reference = self._item_type(record_history_identity=value)
        self._items.append(item_reference)

    def add_record_by_record_history_guid(self, value):
        item_reference = self._item_type(record_history_guid=value)
        self._items.append(item_reference)

    def add_record_by_record_guid(self, value):
        item_reference = self._item_type(record_guid=value)
        self._items.append(item_reference)

    def add_stk_records(self, stk_records: List[Dict[str, str]]):
        for record in stk_records:
            assert 'dbkey' in record
            assert 'record_guid' in record

            if not self._connection.dbkey:
                self._connection.dbkey = record['dbkey']
            else:
                assert record['dbkey'] == self._connection.dbkey
            item_reference = self._item_type(record_guid=record['record_guid'])
            self._items.append(item_reference)

    @property
    def _content(self):
        return [i.definition for i in self._items]


class ComplianceMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._indicators = []
        self._compliance_api = None
        self._compliance_request_type = register_dict[self._item_type_name]['compliance_request_type']

    def set_compliance_api(self, api):
        self._compliance_api = api

    def add_indicator(self, value):
        self._indicators.append(value)

    @property
    def _compliance_args(self):
        return {'database_key': self._connection.dbkey,
                self._item_type_name: self._content,
                'indicators': [i.definition for i in self._indicators],
                'config': self._connection.query_config}

    def get_compliance(self, batch_size: Union[int, None] = None) -> Dict:
        assert self._compliance_api

        if not batch_size:
            batch_size = self._default_batch_size

        # TODO: Batching
        request = self._compliance_request_type(**self._compliance_args)
        response = self._compliance_api(body=request)

        # TODO: Result objects
        return response.to_dict()


class ImpactedSubstanceMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._legislations = []
        self._impacted_substances_api = None
        self._impacted_substances_request_type = register_dict[self._item_type_name]['impacted_substances_request_type']

    def set_impacted_substance_api(self, api):
        self._impacted_substances_api = api

    def add_legislation(self, legislation_name):
        self._legislations.append(legislation_name)

    @property
    def _impacted_substances_args(self):
        return {'database_key': self._connection.dbkey,
                self._item_type_name: self._content,
                'legislation_names': self._legislations,
                'config': self._connection.query_config}

    def get_impacted_substances(self, batch_size: Union[int, None] = None) -> Dict:
        assert self._impacted_substances_api
        if not batch_size:
            batch_size = self._default_batch_size

        # TODO: Batching
        request = self._impacted_substances_request_type(**self._impacted_substances_args)
        response = self._impacted_substances_api(body=request)

        # TODO: Result objects
        return response.to_dict()


class MaterialQueryBuilder(BaseQueryBuilder, MultipleRecordItemMixin, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'materials'
    _item_type = MaterialReference
    _default_batch_size = 100

    def add_record_by_material_id(self, value) -> None:
        material_reference = self._item_type(material_id=value)
        self._items.append(material_reference)


class PartQueryBuilder(BaseQueryBuilder, MultipleRecordItemMixin, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'parts'
    _item_type = PartReference
    _default_batch_size = 10

    def add_record_by_part_id(self, value) -> None:
        part_reference = self._item_type(part_id=value)
        self._items.append(part_reference)


class SpecificationQueryBuilder(BaseQueryBuilder, MultipleRecordItemMixin, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'specifications'
    _item_type = SpecificationReference
    _default_batch_size = 10

    def add_record_by_specification_id(self, value) -> None:
        spec_reference = self._item_type(specification_id=value)
        self._items.append(spec_reference)


class SubstanceQueryBuilder(BaseQueryBuilder, MultipleRecordItemMixin, ComplianceMixin):
    _item_type_name = 'substances'
    _item_type = SubstanceReference
    _default_batch_size = 100

    def add_record_by_substance_name(self, substance_name, percentage_threshold) -> None:
        substance_reference = self._item_type(substance_name=substance_name)
        if percentage_threshold:
            substance_reference.percentage_threshold = percentage_threshold
        self._items.append(substance_reference)

    def add_record_by_cas_number(self, cas_number, percentage_threshold) -> None:
        substance_reference = self._item_type(cas_number=cas_number)
        if percentage_threshold:
            substance_reference.percentage_threshold = percentage_threshold
        self._items.append(substance_reference)

    def add_record_by_ec_number(self, ec_number, percentage_threshold) -> None:
        substance_reference = self._item_type(ec_number=ec_number)
        if percentage_threshold:
            substance_reference.percentage_threshold = percentage_threshold
        self._items.append(substance_reference)


class BoM1711QueryBuilder(BaseQueryBuilder, SingleItemMixin, ImpactedSubstanceMixin, ComplianceMixin):
    _item_type_name = 'bom_xml1711'
    _item_type = BoM1711Reference
    _default_batch_size = 1

    def set_bom(self, value: str) -> None:
        bom = self._item_type(bom=value)
        self._item = bom
