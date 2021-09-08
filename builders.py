from abc import ABC
from typing import Union, List, Dict, Callable


class BaseQueryBuilder(ABC):
    def __init__(self, connection):
        super().__init__()
        self._connection = connection
        self._items = []
        self._item_type: Union[Callable, None] = None
        self._item_type_name = None

    def set_item_type(self, item_type, item_name):
        self._item_type = item_type
        self._item_type_name = item_name

    def add_record_history_identity(self, value):
        item_reference = self._item_type(record_history_identity=value)
        self._items.append(item_reference)

    def add_record_history_guid(self, value):
        item_reference = self._item_type(record_history_guid=value)
        self._items.append(item_reference)

    def add_record_guid(self, value):
        item_reference = self._item_type(record_guid=value)
        self._items.append(item_reference)

    def add_stk_record(self, stk_records: List[Dict[str, str]]):
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
    def items(self):
        return [i.definition for i in self._items]


class ComplianceMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._indicators = []
        self._compliance_request_type = None
        self._compliance_endpoint = None

    def set_compliance_endpoints(self, endpoint, request_type):
        self._compliance_request_type = endpoint
        self._compliance_endpoint = request_type

    def add_indicator(self, value):
        self._indicators.append(value)

    @property
    def _compliance_args(self):
        return {'database_key': self._connection.dbkey,
                self._item_type_name: [i.definition for i in self._items],
                'indicators': [i.definition for i in self._indicators],
                'config': self._connection.query_config}

    def get_compliance(self, batch_size: int = 100) -> Dict:
        assert self._compliance_endpoint and self._compliance_request_type

        # TODO: Batching
        request = self._compliance_request_type(**self._compliance_args)
        response = self._compliance_endpoint(body=request)

        # TODO: Result objects
        return response.to_dict()


class ImpactedSubstanceMixin:
    def __init__(self, **kwargs):
        super().__init__()
        self._legislations = []
        self._impacted_substances_request_type = None
        self._impacted_substances_endpoint = None

    def set_impacted_substances_endpoints(self, endpoint, request_type):
        self._impacted_substances_request_type = endpoint
        self._impacted_substances_endpoint = request_type

    def add_legislation(self, legislation_name):
        self._legislations.append(legislation_name)

    @property
    def _impacted_substances_args(self):
        return {'database_key': self._connection.dbkey,
                self._item_type_name: [i.definition for i in self._items],
                'legislation_names': self._legislations,
                'config': self._connection.query_config}

    def get_impacted_substances(self, batch_size: int = 100) -> Dict:
        # TODO: Batching
        request = self._impacted_substances_request_type(**self._impacted_substances_args)
        response = self._impacted_substances_endpoint(body=request)

        # TODO: Result objects
        return response.to_dict()


class MaterialQueryBuilder(BaseQueryBuilder, ImpactedSubstanceMixin, ComplianceMixin):
    def add_material_id(self, value) -> None:
        material_reference = self._item_type(material_id=value)
        self._items.append(material_reference)


class PartQueryBuilder(BaseQueryBuilder, ImpactedSubstanceMixin, ComplianceMixin):
    def add_part_id(self, value) -> None:
        part_reference = self._item_type(part_id=value)
        self._items.append(part_reference)


class SpecificationQueryBuilder(BaseQueryBuilder, ImpactedSubstanceMixin, ComplianceMixin):
    def add_specification_id(self, value) -> None:
        spec_reference = self._item_type(specification_id=value)
        self._items.append(spec_reference)


class BoM1711QueryBuilder(BaseQueryBuilder, ImpactedSubstanceMixin, ComplianceMixin):
    def add_specification_id(self, value: str) -> None:
        bom = self._item_type(bom=value)
        self._items.append(bom)


class SubstanceQueryBuilder(BaseQueryBuilder, ComplianceMixin):
    def add_substance_name(self, substance_name, percentage_threshold) -> None:
        substance_reference = self._item_type(substance_name=substance_name)
        if percentage_threshold:
            substance_reference.percentage_threshold = percentage_threshold
        self._items.append(substance_reference)

    def add_cas_number(self, cas_number, percentage_threshold) -> None:
        substance_reference = self._item_type(cas_number=cas_number)
        if percentage_threshold:
            substance_reference.percentage_threshold = percentage_threshold
        self._items.append(substance_reference)

    def add_ec_number(self, ec_number, percentage_threshold) -> None:
        substance_reference = self._item_type(ec_number=ec_number)
        if percentage_threshold:
            substance_reference.percentage_threshold = percentage_threshold
        self._items.append(substance_reference)
