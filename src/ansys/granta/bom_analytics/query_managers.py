from abc import ABC, abstractmethod
from typing import Union, List, Dict, Callable, Tuple
import warnings

from ansys.granta.bomanalytics import models

from .bom_item_definitions import AbstractBomFactory
from .query_results import QueryResultFactory

# Required for type hinting
from .connection import Connection
from .query_results import (
    MaterialImpactedSubstancesResult,
    MaterialComplianceResult,
    PartImpactedSubstancesResult,
    PartComplianceResult,
    SpecificationImpactedSubstancesResult,
    SpecificationComplianceResult,
    SubstanceComplianceResult,
    BoMImpactedSubstancesResult,
    BoMComplianceResult,
)
from .bom_indicators import IndicatorDefinition


class BaseQueryBuilder(ABC):
    _item_type_name = None
    _result_type: Union[Callable, None] = None

    def __init__(self, connection):
        self._connection = connection
        self._items = []
        self._batch_size = None

    def _validate_items(self):
        if not self._items:
            warnings.warn(
                f"No {self._item_type_name} have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )

    @property
    def batch_size(self) -> int:
        return self._batch_size

    def set_batch_size(self, value: int):
        if int(value) < 0:
            raise ValueError("Batch must be a positive integer")
        self._batch_size = int(value)
        return self

    @property
    def _content(self) -> List[List[models.Model]]:
        for i in range(0, len(self._items), self.batch_size):
            yield [i.definition for i in self._items][
                i : i + self.batch_size
            ]  # noqa: E203 E501


class RecordBasedQueryManager(BaseQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._definition_factory = None

    def add_record_history_ids(self, values: List[int]):
        for value in values:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_identity=value
            )
            self._items.append(item_reference)
        return self

    def add_record_history_guids(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_guid=value
            )
            self._items.append(item_reference)
        return self

    def add_record_guids(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_guid=value
            )
            self._items.append(item_reference)
        return self

    def add_stk_records(self, stk_records: List[Dict[str, str]]):
        record_guids = [r["record_guid"] for r in stk_records]
        self.add_record_guids(record_guids)
        return self


class ApiMixin(ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._result_type = None

    def _run_query(self) -> List:
        result = []
        for batch in self._content:
            args = {**self._arguments, self._item_type_name: batch}
            request = self._request_type(**args)
            response = self._api(body=request)
            result.extend([r for r in getattr(response, self._item_type_name)])
        return result

    @abstractmethod
    def _validate_parameters(self):
        pass

    @property
    @abstractmethod
    def _arguments(self) -> Dict:
        pass


class ComplianceMixin(ApiMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._indicators = []

    def add_indicators(self, values: List[IndicatorDefinition]):
        for value in values:
            self._indicators.append(value)
        return self

    def execute(self):
        self._validate_parameters()
        self._validate_items()
        result_raw = self._run_query()
        result = QueryResultFactory.create_result(
            response_type=self._result_type,
            results=result_raw,
            indicator_definitions=self._indicators,
        )
        return result

    def _validate_parameters(self):
        if not self._indicators:
            warnings.warn(
                "No indicators have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )

    @property
    def _arguments(self):
        return {
            "database_key": self._connection.dbkey,
            "indicators": [i.definition for i in self._indicators],
            "config": self._connection.query_config,
        }


class ImpactedSubstanceMixin(ApiMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._legislations: List[str] = []

    def add_legislations(self, legislation_names: List[str]):
        self._legislations.extend(legislation_names)
        return self

    def execute(self):
        self._validate_parameters()
        self._validate_items()
        result_raw = self._run_query()
        result = QueryResultFactory.create_result(
            response_type=self._result_type, results=result_raw
        )
        return result

    def _validate_parameters(self):
        if not self._legislations:
            warnings.warn(
                "No legislations have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )

    @property
    def _arguments(self):
        return {
            "database_key": self._connection.dbkey,
            "legislation_names": self._legislations,
            "config": self._connection.query_config,
        }


class MaterialQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 100
        self._item_type_name = "materials"
        self._definition_factory = None

    def add_material_ids(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_definition_by_material_id(
                value
            )
            self._items.append(item_reference)
        return self


class MaterialComplianceQuery(ComplianceMixin, MaterialQueryManager):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance
        )
        self._api = (
            self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_materials  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> MaterialComplianceResult:
        return super().execute()


class MaterialImpactedSubstanceQuery(ImpactedSubstanceMixin, MaterialQueryManager):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest  # noqa: E501
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial
        )
        self._api = (
            self._connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> MaterialImpactedSubstancesResult:
        return super().execute()


class PartQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 10
        self._item_type_name = "parts"
        self._definition_factory = None

    def add_part_numbers(self, values: List[str]):
        for value in values:
            item_reference = self._definition_factory.create_definition_by_part_number(
                value
            )
            self._items.append(item_reference)
        return self


class PartComplianceQuery(ComplianceMixin, PartQueryManager):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance
        )
        self._api = (
            self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_parts  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> PartComplianceResult:
        return super().execute()


class PartImpactedSubstanceQuery(ImpactedSubstanceMixin, PartQueryManager):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest  # noqa: E501
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart
        )
        self._api = (
            self._connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> PartImpactedSubstancesResult:
        return super().execute()


class SpecificationQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 10
        self._item_type_name = "specifications"
        self._definition_factory = None

    def add_specification_ids(self, values: List[str]):
        for value in values:
            item_reference = (
                self._definition_factory.create_definition_by_specification_id(value)
            )
            self._items.append(item_reference)
        return self


class SpecificationComplianceQuery(ComplianceMixin, SpecificationQueryManager):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest  # noqa: E501
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance
        )
        self._api = (
            self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_specifications  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> SpecificationComplianceResult:
        return super().execute()


class SpecificationImpactedSubstanceQuery(
    ImpactedSubstanceMixin, SpecificationQueryManager
):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest  # noqa: E501
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification
        )
        self._api = (
            self._connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> SpecificationImpactedSubstancesResult:
        return super().execute()


class SubstanceQueryManager(RecordBasedQueryManager, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 500
        self._item_type_name = "substances"
        self._definition_factory = None

    def add_cas_numbers(self, values: List[str]):
        for cas_number in values:
            item_reference = self._definition_factory.create_definition_by_cas_number(
                cas_number
            )
            self._items.append(item_reference)
        return self

    def add_ec_numbers(self, values: List[str]):
        for ec_number in values:
            item_reference = self._definition_factory.create_definition_by_ec_number(
                ec_number
            )
            self._items.append(item_reference)
        return self

    def add_chemical_names(self, values: List[str]):
        for chemical_name in values:
            item_reference = (
                self._definition_factory.create_definition_by_chemical_name(
                    chemical_name
                )
            )
            self._items.append(item_reference)
        return self

    def add_record_history_ids_with_amounts(self, values: List[Tuple[int, float]]):
        for record_history_id, amount in values:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_identity=record_history_id
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_record_history_guids_with_amounts(self, values: List[Tuple[str, float]]):
        for record_history_guid, amount in values:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_guid=record_history_guid
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_record_guids_with_amounts(self, values: List[Tuple[str, float]]):
        for record_guid, amount in values:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_guid=record_guid
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_cas_numbers_with_amounts(self, values: List[Tuple[str, float]]):
        for cas_number, amount in values:
            item_reference = self._definition_factory.create_definition_by_cas_number(
                cas_number
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_ec_numbers_with_amounts(self, values: List[Tuple[str, float]]):
        for ec_number, amount in values:
            item_reference = self._definition_factory.create_definition_by_ec_number(
                ec_number
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    def add_chemical_names_with_amounts(self, values: List[Tuple[str, float]]):
        for chemical_name, amount in values:
            item_reference = (
                self._definition_factory.create_definition_by_chemical_name(
                    chemical_name
                )
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self


class SubstanceComplianceQuery(ComplianceMixin, SubstanceQueryManager):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
        )
        self._api = (
            self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_substances  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> SubstanceComplianceResult:
        return super().execute()


class BoM1711QueryManager(BaseQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 1
        self._item_type_name = "bom_xml1711"
        self._definition_factory = None

    def set_bom(self, bom: str):
        self._items = [self._definition_factory.create_definition(bom=bom)]
        return self


class BoMQueryOverride:
    def _run_query(self) -> List:
        args = {**self._arguments, self._item_type_name: list(self._content)[0][0]}
        request = self._request_type(**args)
        response = self._api(body=request)
        return response


class BoMComplianceQuery(BoMQueryOverride, ComplianceMixin, BoM1711QueryManager):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response
        )
        self._api = (
            self._connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_bom1711  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> BoMComplianceResult:
        return super().execute()


class BoMImpactedSubstancesQuery(
    BoMQueryOverride, ImpactedSubstanceMixin, BoM1711QueryManager
):
    def __init__(self, connection: Connection):
        super().__init__(connection=connection)
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request  # noqa: E501
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response
        )
        self._api = (
            self._connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_bom1711  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(
            self._request_type
        )

    def execute(self) -> BoMImpactedSubstancesResult:
        return super().execute()
