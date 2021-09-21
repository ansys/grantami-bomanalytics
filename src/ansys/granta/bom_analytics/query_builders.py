from abc import ABC, abstractmethod
from typing import Union, List, Dict, Tuple, Any, TypeVar, Generic, Type, TYPE_CHECKING
import warnings
from numbers import Number

from ansys.granta.bomanalytics import models

from .bom_item_definitions import AbstractBomFactory
from .allowed_types import allowed_types
from .connection import Connection
from .query_results import (
    QueryResultFactory,
    ComplianceBaseClass,
    ImpactedSubstancesBaseClass,
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
from .bom_indicators import Indicator, WatchListIndicator

T = TypeVar("T", bound="BaseQueryBuilder")
result_T = TypeVar(
    "result_T",
    covariant=True,
    bound=Union[ComplianceBaseClass, ImpactedSubstancesBaseClass],
)


class BaseQueryBuilder(Generic[T], ABC):
    _item_type_name = None
    _result_type: Union[Type[models.Model], None] = None

    def __init__(self):
        self._items = []
        self._batch_size = None

    def _validate_items(self):
        if not self._items:
            warnings.warn(
                f"No {self._item_type_name} have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )

    @allowed_types(Any, int)
    def set_batch_size(self: T, batch_size: int) -> T:
        """
        Number of items included in a single request. Sensible values are set by default, but this value can be changed
        to optimize performance if required on a query-by-query basis.

        Parameters
        ----------
        batch_size : int

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.set_batch_size(batch_size=50)
        """

        if batch_size < 1:
            raise ValueError("Batch must be a positive integer")
        self._batch_size = batch_size
        return self

    @property
    def _content(self) -> List[List[models.Model]]:
        for i in range(0, len(self._items), self._batch_size):
            yield [i.definition for i in self._items][i : i + self._batch_size]  # noqa: E203 E501


class RecordBasedQueryBuilder(BaseQueryBuilder, ABC):
    def __init__(self):
        super().__init__()
        self._definition_factory = None

    @allowed_types(Any, [int])
    def add_record_history_ids(self: T, record_history_identities: List[int]) -> T:
        """
        Add a list of record history identities to a query.

        Parameters
        ----------
        record_history_identities : list(int)
            List of integer record history identities to be added to the query

        Returns
        -------
        RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.add_record_history_ids([15321, 17542, 942])
        """

        for value in record_history_identities:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=value
            )
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [str])
    def add_record_history_guids(self: T, record_history_guids: List[str]) -> T:
        """
        Add a list of record history guids to a query.

        Parameters
        ----------
        record_history_guids : list(str)
            List of record history guids to be added to the query

        Returns
        -------
        RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.add_record_history_guids(['41e20a88-d496-4735-a177-6266fac9b4e2',
        ...                               'd117d9ad-e6a9-4ba9-8ad8-9a20b6d0b5e2'])
        """

        for value in record_history_guids:
            item_reference = self._definition_factory.create_definition_by_record_history_guid(
                record_history_guid=value
            )
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [str])
    def add_record_guids(self: T, record_guids: List[str]) -> T:
        """
        Add a list of record guids to a query.

        Parameters
        ----------
        record_guids : list(str)
            List of record guids to be added to the query

        Returns
        -------
        RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.add_record_guids(['bdb0b880-e6ee-4f1a-bebd-af76959ae3c8',
        ...                         'a98cf4b3-f96a-4714-9f79-afe443982c69'])
        """

        for value in record_guids:
            item_reference = self._definition_factory.create_definition_by_record_guid(record_guid=value)
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [{str: str}])
    def add_stk_records(self: T, stk_records: List[Dict[str, str]]) -> T:
        """
        Add a list of records generated by the Scripting Toolkit.

        Parameters
        ----------
        stk_records : list
            List of record definitions

        Returns
        -------
        RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.add_stk_records(stk_records)
        """

        record_guids = [r["record_guid"] for r in stk_records]
        self.add_record_guids(record_guids)

        return self


if TYPE_CHECKING:
    api_base_class = RecordBasedQueryBuilder
else:
    api_base_class = object


class ApiMixin(api_base_class):
    def __init__(self, **kwargs):
        super().__init__()
        self._request_type = None
        self._result_type = None
        self._connection = None
        self._api = None

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
        self._indicators = {}

    @allowed_types(Any, [Indicator])
    def add_indicators(self: T, indicators: List[Indicator]) -> T:
        """
        Add a list of indicators to evaluate compliance against.

        Parameters
        ----------
        indicators : list
            List of Indicator definitions

        Returns
        -------
        RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.add_indicators([WatchListIndicator(...)])
        """

        for value in indicators:
            self._indicators[value.name] = value
        return self

    def execute(self, connection: Connection) -> result_T:
        self._connection = connection
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
            "database_key": self._connection.db_key,
            "indicators": [i.definition for i in self._indicators.values()],
            "config": self._connection.query_config,
        }


class ImpactedSubstanceMixin(Generic[T], ApiMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._legislations: List[str] = []

    @allowed_types(Any, [str])
    def add_legislations(self: T, legislation_names: List[str]) -> T:
        """
        Add a list of legislations to retreive the impacted substances for.

        Parameters
        ----------
        legislation_names : str
            List of legislation names

        Returns
        -------
        RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialImpactedSubstanceQuery()
        >>> query.add_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
        """

        self._legislations.extend(legislation_names)
        return self

    def execute(self, connection: Connection) -> result_T:
        self._connection = connection
        self._validate_parameters()
        self._validate_items()
        result_raw = self._run_query()
        result = QueryResultFactory.create_result(response_type=self._result_type, results=result_raw)
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
            "database_key": self._connection.db_key,
            "legislation_names": self._legislations,
            "config": self._connection.query_config,
        }


class MaterialQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self: T, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 100
        self._item_type_name = "materials"
        self._definition_factory = None

    @allowed_types(Any, [str])
    def add_material_ids(self: T, material_ids: List[str]) -> T:
        """
        Add a list of material ids to a material query.

        Parameters
        ----------
        material_ids : list(str)
            List of material ids to be added to the query

        Returns
        -------
        MaterialQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.add_material_ids(['elastomer-butadienerubber',
        ...                         'NBR-100'])
        """
        for material_id in material_ids:
            item_reference = self._definition_factory.create_definition_by_material_id(material_id=material_id)
            self._items.append(item_reference)
        return self


class MaterialComplianceQuery(ComplianceMixin, MaterialQueryBuilder):
    """
    A query to evaluate compliance for Granta MI material records against a number of indicators. If the materials are
    associated with substances, these are also evaluated and returned.

    All methods used to add materials and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    MaterialComplianceQuery
        The query containing the material records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     MaterialComplianceQuery()
    ...     .add_material_ids(['elastomer-butadienerubber', 'NBR-100'])
    ...     .add_indicators([WatchListIndicator(...)])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> MaterialComplianceResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        MaterialComplianceResult
            The result of the compliance query.

        """
        self._api = connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_materials  # noqa: E501
        return super().execute(connection)


class MaterialImpactedSubstanceQuery(ImpactedSubstanceMixin, MaterialQueryBuilder):
    """
    A query to determine the substances impacted by a list of legislations for Granta MI material records.

    All methods used to add materials and legislations to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    MaterialImpactedSubstancesQuery
        The query containing the material records and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     MaterialImpactedSubstanceQuery()
    ...     .add_material_ids(['elastomer-butadienerubber', 'NBR-100'])
    ...     .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest  # noqa: E501
        )
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> MaterialImpactedSubstancesResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        MaterialImpactedSubstancesResult
            The result of the impacted substances query.
        """
        self._api = (
            connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials  # noqa: E501
        )
        return super().execute(connection)


class PartQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 10
        self._item_type_name = "parts"
        self._definition_factory = None

    @allowed_types(Any, [str])
    def add_part_numbers(self: T, part_numbers: List[str]) -> T:
        """
        Add a list of part numbers to a part query.

        Parameters
        ----------
        part_numbers : list(str)
            List of part numbers to be added to the query

        Returns
        -------
        PartQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = PartComplianceQuery()
        >>> query.add_part_numbers(['ABC12345', 'Q356AQ'])
        """

        for value in part_numbers:
            item_reference = self._definition_factory.create_definition_by_part_number(part_number=value)
            self._items.append(item_reference)
        return self


class PartComplianceQuery(ComplianceMixin, PartQueryBuilder):
    """
    A query to evaluate compliance for Granta MI part records against a number of indicators. If the parts are
    associated with materials, parts, specifications, or substances, these are also evaluated and returned.

    All methods used to add parts and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    PartComplianceQuery
        The query containing the part records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     PartComplianceQuery()
    ...    .add_part_numbers(['ABC12345', 'Q356AQ'])
    ...    .add_indicators([WatchListIndicator(...)])
    ...    .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> PartComplianceResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        PartComplianceResult
            The result of the compliance query.
        """
        self._api = connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_parts  # noqa: E501
        return super().execute(connection)


class PartImpactedSubstanceQuery(ImpactedSubstanceMixin, PartQueryBuilder):
    """
    A query to determine the substances impacted by a list of legislations for Granta MI part records.

    All methods used to add parts and legislations to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    PartImpactedSubstancesQuery
        The query containing the part records and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     PartImpactedSubstanceQuery()
    ...     .add_part_numbers(['ABC12345', 'Q356AQ'])
    ...     .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest  # noqa: E501
        )
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> PartImpactedSubstancesResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        PartImpactedSubstancesResult
            The result of the impacted substances query.
        """
        self._api = (
            connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts  # noqa: E501
        )
        return super().execute(connection)


class SpecificationQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 10
        self._item_type_name = "specifications"
        self._definition_factory = None

    @allowed_types(Any, [str])
    def add_specification_ids(self: T, specification_ids: List[str]) -> T:
        """
        Add a list of specification IDs to a specification query.

        Parameters
        ----------
        specification_ids : list(str)
            List of specification IDs to be added to the query

        Returns
        -------
        SpecificationQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SpecificationComplianceQuery()
        >>> query.add_specification_ids(['MIL-A-8625', 'PSP101'])
        """
        for specification_id in specification_ids:
            item_reference = self._definition_factory.create_definition_by_specification_id(
                specification_id=specification_id
            )
            self._items.append(item_reference)
        return self


class SpecificationComplianceQuery(ComplianceMixin, SpecificationQueryBuilder):
    """
    A query to evaluate compliance for Granta MI specification records against a number of indicators. If the
    specifications are associated with materials, specifications, or substances, these are also evaluated and returned.

    All methods used to add specifcations and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    SpecificationComplianceQuery
        The query containing the specification records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     SpecificationComplianceQuery()
    ...     .add_specification_ids(['MIL-A-8625', 'PSP101'])
    ...     .add_indicators([WatchListIndicator(...)])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest  # noqa: E501
        )
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> SpecificationComplianceResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        SpecificationComplianceResult
            The result of the compliance query.
        """
        self._api = (
            connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_specifications  # noqa: E501
        )
        return super().execute(connection)


class SpecificationImpactedSubstanceQuery(ImpactedSubstanceMixin, SpecificationQueryBuilder):
    """
    A query to determine the substances impacted by a list of legislations for Granta MI specification records.

    All methods used to add specifications and legislations to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    SpecificationImpactedSubstancesQuery
        The query containing the specification records and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     SpecificationImpactedSubstanceQuery()
    ...     .add_specification_ids(['MIL-A-8625', 'PSP101'])
    ...     .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest  # noqa: E501
        )
        self._result_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> SpecificationImpactedSubstancesResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        SpecificationImpactedSubstancesResult
            The result of the impacted substances query.
        """
        self._api = (
            connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications  # noqa: E501
        )
        return super().execute(connection)


class SubstanceQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 500
        self._item_type_name = "substances"
        self._definition_factory = None

    @allowed_types(Any, [str])
    def add_cas_numbers(self: T, cas_numbers: List[str]) -> T:
        """
        Add a list of CAS numbers to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        cas_numbers : list(str)
            List of CAS numbers to be added to the query

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_cas_numbers(['50-00-0', '57-24-9'])
        """
        for cas_number in cas_numbers:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [str])
    def add_ec_numbers(self: T, ec_numbers: List[str]) -> T:
        """
        Add a list of EC numbers to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        ec_numbers : list(str)
            List of EC numbers to be added to the query

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_ec_numbers(['200-001-8', '200-319-7'])
        """
        for ec_number in ec_numbers:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number=ec_number)
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [str])
    def add_chemical_names(self: T, chemical_names: List[str]) -> T:
        """
        Add a list of chemical names to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        chemical_names : list(str)
            List of chemical names to be added to the query

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_chemical_names(['Formaldehyde', 'Strychnine'])
        """
        for chemical_name in chemical_names:
            item_reference = self._definition_factory.create_definition_by_chemical_name(chemical_name=chemical_name)
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [(int, Number)])
    def add_record_history_ids_with_amounts(
        self: T, record_history_identities_and_amounts: List[Tuple[int, float]]
    ) -> T:
        """
        Add a list of record history identities and amounts to a substance query.

        Parameters
        ----------
        record_history_identities_and_amounts : list(tuple(str, float))
            List of tuples containing the record history identity and its wt % amount in the material/part

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_record_history_ids_with_amounts([(15321, 25),
        ...                                            (17542, 0.1)])
        """

        for record_history_id, amount in record_history_identities_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=record_history_id
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [(str, Number)])
    def add_record_history_guids_with_amounts(self: T, record_history_guids_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of record history guids and amounts to a substance query.

        Parameters
        ----------
        record_history_guids_and_amounts : list(tuple(str, float))
            List of tuples containing the record history guid and its wt % amount in the material/part

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_record_history_guids_with_amounts([('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        ...                                              ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)])
        """
        for record_history_guid, amount in record_history_guids_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_history_guid(
                record_history_guid=record_history_guid
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [(str, Number)])
    def add_record_guids_with_amounts(self: T, record_guids_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of record guids and amounts to a substance query.

        Parameters
        ----------
        record_guids_and_amounts : list(tuple(str, float))
            List of tuples containing the record guid and its wt % amount in the material/part

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_record_guids_with_amounts([('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        ...                                      ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)])
        """

        for record_guid, amount in record_guids_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_guid(record_guid=record_guid)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [(str, Number)])
    def add_cas_numbers_with_amounts(self: T, cas_numbers_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of CAS numbers and amounts to a substance query.

        Parameters
        ----------
        cas_numbers_and_amounts : list(tuple(str, float))
            List of tuples containing the CAS number and its wt % amount in the material/part

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_cas_numbers_with_amounts([('50-00-0', 25), ('57-24-9', 0.1)])
        """

        for cas_number, amount in cas_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [(str, Number)])
    def add_ec_numbers_with_amounts(self: T, ec_numbers_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of EC numbers and amounts to a substance query.

        Parameters
        ----------
        ec_numbers_and_amounts : list(tuple(str, float))
            List of tuples containing the EC number and its wt % amount in the material/part

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_ec_numbers_with_amounts([('200-001-8', 25), ('200-319-7', 0.1)])
        """

        for ec_number, amount in ec_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number=ec_number)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @allowed_types(Any, [(str, Number)])
    def add_chemical_names_with_amounts(self: T, chemical_names_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of chemical names and amounts to a substance query.

        Parameters
        ----------
        chemical_names_and_amounts : list(tuple(str, float))
            List of tuples containing the chemical name and its wt % amount in the material/part

        Returns
        -------
        SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query.add_chemical_names_with_amounts([('Formaldehyde', 25), ('Strychnine', 0.1)])
        """

        for chemical_name, amount in chemical_names_and_amounts:
            item_reference = self._definition_factory.create_definition_by_chemical_name(chemical_name=chemical_name)
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self


class SubstanceComplianceQuery(ComplianceMixin, SubstanceQueryBuilder):
    """
    A query to evaluate compliance for Granta MI substance records against a number of indicators.

    All methods used to add substances and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    SubstanceComplianceQuery
        The query containing the substance records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     SubstanceComplianceQuery()
    ...     .add_cas_numbers(['50-00-0', '57-24-9'])
    ...     .add_indicators([WatchListIndicator(...)])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> SubstanceComplianceResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        SubstanceComplianceResult
            The result of the compliance query.
        """
        self._api = (
            connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_substances  # noqa: E501
        )
        return super().execute(connection)


class Bom1711QueryBuilder(BaseQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 1
        self._item_type_name = "bom_xml1711"
        self._definition_factory = None

    @allowed_types(Any, str)
    def set_bom(self: T, bom: str) -> T:
        """
        Set the bom to be used for the query. Must be in the Granta 17/11 XML format. This format can be saved from the
        BoM Analyzer.

        Parameters
        ----------
        bom : str

        Examples
        --------
        >>> query = BomComplianceQuery()
        >>> query.set_bom(bom)
        """

        self._items = [self._definition_factory.create_definition(bom=bom)]
        return self


if TYPE_CHECKING:
    bom_base_class = RecordBasedQueryBuilder, ApiMixin
else:
    bom_base_class = object


class Bom1711QueryOverride(bom_base_class):
    def _run_query(self) -> List:
        args = {**self._arguments, self._item_type_name: list(self._content)[0][0]}
        request = self._request_type(**args)
        response = self._api(body=request)
        return response


class BomComplianceQuery(Bom1711QueryOverride, ComplianceMixin, Bom1711QueryBuilder):
    """
    A query to evaluate compliance for a Bill of Maerials in 17/11 XML format against a number of indicators.

    All methods used to add the Bill of Materials and indicators to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    BomComplianceQuery
        The query containing the BoM and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> bom = "<PartsEco xmlns..."
    >>> result = (
    ...     BomComplianceQuery()
    ...     .set_bom(bom)
    ...     .add_indicators([WatchListIndicator(...)])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> BoMComplianceResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        BoMComplianceResult
            The result of the compliance query.
        """
        self._api = connection.compliance_api.post_miservicelayer_bom_analytics_v1svc_compliance_bom1711  # noqa: E501
        return super().execute(connection)


class BomImpactedSubstanceQuery(Bom1711QueryOverride, ImpactedSubstanceMixin, Bom1711QueryBuilder):
    """
    A query to determine the substances impacted by a list of legislations for a Bill of Maerials in 17/11 XML format.

    All methods used to add the bom and legislations to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Returns
    -------
    BomImpactedSubstanceQuery
        The query containing the bom and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = (
    ...     BomImpactedSubstanceQuery()
    ...     .set_bom("<PartsEco xmlns...")
    ...     .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ...     .execute(conn)
    ... )
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request  # noqa: E501
        )
        self._result_type = models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)

    def execute(self, connection: Connection) -> BoMImpactedSubstancesResult:
        """
        Run the query against the Granta MI database and return the results.

        Parameters
        ----------
        connection : Connection
            The connection to the Granta MI server.

        Returns
        -------
        BoMImpactedSubstancesResult
            The result of the impacted substances query.
        """
        self._api = (
            connection.impacted_substances_api.post_miservicelayer_bom_analytics_v1svc_impactedsubstances_bom1711  # noqa: E501
        )
        return super().execute(connection)
