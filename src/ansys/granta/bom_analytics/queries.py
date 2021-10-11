from abc import ABC, abstractmethod
from typing import Union, List, Dict, Tuple, Any, TypeVar, Generic, TYPE_CHECKING, Callable, Generator
import warnings
from numbers import Number
import logging

from ansys.granta.bomanalytics import models, api

from ._bom_item_definitions import AbstractBomFactory, RecordDefinition
from ._allowed_types import allowed_types
from ._connection import Connection
from ._query_results import (
    QueryResultFactory,
    ComplianceBaseClass,
    ImpactedSubstancesBaseClass,
)
from .indicators import _Indicator

T = TypeVar("T", bound="BaseQueryBuilder")
Query_Result = TypeVar(
    "Query_Result",
    covariant=True,
    bound=Union[ComplianceBaseClass, ImpactedSubstancesBaseClass],
)


logger = logging.getLogger(__name__)


class _RecordArgumentManager:
    """Store Bom items for use in queries and generate the list of models to be sent to the server.

    Parameters
    ----------
    record_type_name : str
        The name of the items, e.g. materials, parts. Used in the `batched_bom_arguments` property as the keyword for
        the list of items in the request constructor.
    batch_size : int
        Number of items included in a single request.

    Attributes
    ----------
    _items : list of `RecordDefinition`
        The definition objects added to this object to be used in a query

    Examples
    --------
    >>> items = _RecordDefinitionList(item_type_name = "materials", batch_size = 100)
    >>> items.batched_bom_arguments
    {"materials": [{"reference_type": "material_id", "reference_value": "ABS"}, ...]  # Up to 100 items
    """

    def __init__(self, record_type_name: Union[str, None] = None, batch_size: Union[int, None] = None):
        super().__init__()
        self._items = []
        self.batch_size: Union[int, None] = batch_size
        self.record_type_name: Union[str, None] = record_type_name

    def __repr__(self):
        if not self.record_type_name:
            item_text = "record_type_name: None"
        else:
            item_text = f'record_type_name: "{self.record_type_name}"'
        if not self.batch_size:
            batch_text = "batch_size: None"
        else:
            batch_text = f"batch_size: {self.batch_size}"
        return f"<{self.__class__.__name__} {{{item_text}, {batch_text}}}, length = {len(self._items)}>"

    def append_record_definition(self, item: RecordDefinition):
        """Append a specific record definition to the argument manager.

        Parameters
        ----------
        item : `RecordDefinition`
            The definition to be added to this list of record definitions.

        Examples
        --------
        >>> part_definition = PartDefinition(...)
        >>> items = _RecordDefinitionList(item_type_name = "materials", batch_size = 100)
        >>> items.append(part_definition)
        """

        self._items.append(item)

    @property
    def is_populated(self):
        return self._items is None

    @property
    def batched_record_arguments(self) -> Generator[Dict[str, List[Union[models.Model, str]]], None, None]:
        """A generator producing item request arguments as a list of instances of the appropriate Model. Each list
        of dicts will be at most `_batch_size` long.

        Each individual dict can be passed to the request constructor as a kwarg.

        Yields
        ------
        Generator(dict(str, list(models.Model)))

        Raises
        ------
        RuntimeError
            If the `item_type_name` has not been set before the arguments are generated.
        """

        if self.record_type_name is None:
            raise RuntimeError('"record_type_name" must be populated before record arguments can be generated.')
        if self.batch_size is None:
            raise RuntimeError('"batch_size" must be populated before record arguments can be generated.')

        for batch_number, i in enumerate(range(0, len(self._items), self.batch_size)):
            batch = [i.definition for i in self._items][i : i + self.batch_size]  # noqa: E203 E501
            batch_str = ", ".join([f'"{item.reference_type}": "{item.reference_value}"' for item in batch])
            logger.debug(f"[TECHDOCS] Batch {batch_number + 1}, Items: {batch_str}")
            yield {self.record_type_name: batch}

    def extract_results_from_response(self, response):
        return [r for r in getattr(response, self.record_type_name)]


class _BaseQueryBuilder(Generic[T], ABC):
    """Base class for all query types. The properties and methods here primarily represent the things on which the API is
    acting, i.e. records or bills of materials (BoMs).

    Attributes
    ----------
    _record_argument_manager : _RecordArgumentManager
        The list of 'things' on which the API gets compliance for.
    """

    def __init__(self):
        self._record_argument_manager = _RecordArgumentManager()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._record_argument_manager}>"

    def _validate_items(self):
        """Perform pre-flight checks on the items that have been added to the query.

        Warns
        -----
        RuntimeWarning
            If no items have been added to the query, warn that the response will be empty.
        """

        if not self._record_argument_manager.is_populated:
            warnings.warn(
                f"No {self._record_argument_manager.record_type_name} have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )

    @allowed_types(Any, int)
    def with_batch_size(self: T, batch_size: int) -> T:
        """
        Number of items included in a single request. Sensible values are set by default, but this value can be changed
        to optimize performance if required on a query-by-query basis.

        Parameters
        ----------
        batch_size : int

        Examples
        --------
        >>> query = MaterialCompliance().with_batch_size(50)...
        """

        if batch_size < 1:
            raise ValueError("Batch must be a positive integer")
        self._record_argument_manager.batch_size = batch_size
        return self


class _RecordBasedQueryBuilder(_BaseQueryBuilder, ABC):
    """
    Sub-class for all queries where the items added to the query are direct references to records.
    """

    @allowed_types(_BaseQueryBuilder, [int])
    def with_record_history_ids(self: T, record_history_identities: List[int]) -> T:
        """
        Add a list of record history identities to a query.

        Parameters
        ----------
        record_history_identities : list(int)
            List of integer record history identities to be added to the query

        Returns
        -------
        _RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialCompliance() \
        ...         .with_record_history_ids([15321, 17542, 942])...
        """

        for value in record_history_identities:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=value
            )
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [str])
    def with_record_history_guids(self: T, record_history_guids: List[str]) -> T:
        """
        Add a list of record history guids to a query.

        Parameters
        ----------
        record_history_guids : list(str)
            List of record history guids to be added to the query

        Returns
        -------
        _RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialCompliance() \
        ...         .with_record_history_guids(['41e20a88-d496-4735-a177-6266fac9b4e2',
        ...                                     'd117d9ad-e6a9-4ba9-8ad8-9a20b6d0b5e2'])...
        """

        for value in record_history_guids:
            item_reference = self._definition_factory.create_definition_by_record_history_guid(
                record_history_guid=value
            )
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [str])
    def with_record_guids(self: T, record_guids: List[str]) -> T:
        """
        Add a list of record guids to a query.

        Parameters
        ----------
        record_guids : list(str)
            List of record guids to be added to the query

        Returns
        -------
        _RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialCompliance() \
        ...         .with_record_guids(['bdb0b880-e6ee-4f1a-bebd-af76959ae3c8',
        ...                             'a98cf4b3-f96a-4714-9f79-afe443982c69'])...
        """

        for value in record_guids:
            item_reference = self._definition_factory.create_definition_by_record_guid(record_guid=value)
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [{str: str}])
    def with_stk_records(self: T, stk_records: List[Dict[str, str]]) -> T:
        """
        Add a list of records generated by the Scripting Toolkit.

        Parameters
        ----------
        stk_records : list
            List of record definitions

        Returns
        -------
        _RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialCompliance().with_stk_records(stk_records)...
        """

        record_guids = [r["record_guid"] for r in stk_records]  # TODO Handle database key
        return self.with_record_guids(record_guids)


if TYPE_CHECKING:
    api_base_class = _RecordBasedQueryBuilder
else:
    api_base_class = object


class _ApiMixin(api_base_class):
    """
    Base class for API-specific mixins.

    Describes generic properties of a call to an API (e.g. calling the API, processing results) and defines abstract
    concepts about validating parameters (i.e. the axes over which the items will be evaluated).

    Attributes
    ----------
    _request_type : models.Model
        The type of object to be sent to the Granta MI server. The actual value is set in the concrete class definition.
    """

    def __init__(self):
        super().__init__()
        self._request_type = None

    def _call_api(self, api_method: Callable, arguments: Dict) -> List:
        self._validate_parameters()
        self._validate_items()
        result = []
        for idx, batch in enumerate(self._record_argument_manager.batched_record_arguments):
            args = {**arguments, **batch}
            request = self._request_type(**args)
            response = api_method(body=request)
            result.extend(self._record_argument_manager.extract_results_from_response(response))
        return result

    @abstractmethod
    def run_query(
        self, api_instance: Union[api.ComplianceApi, api.ImpactedSubstancesApi], static_arguments: Dict
    ) -> Query_Result:
        pass

    @abstractmethod
    def _validate_parameters(self):
        pass


class _ComplianceMixin(_ApiMixin, ABC):
    """
    Handles the compliance aspects of a query.

    Includes adding indicator parameters to the query, generating the indicator-specific argument to be sent to Granta
    MI, and creating the compliance result objects.

    Attributes
    ----------
    _indicators : dict
        The indicators added to the query.
    api : object
        The class in the low-level API for this query type. Requires instantiation with the client object, and so only
        the reference to the class is stored here, not the instance itself.
    api_method : str
        The name of the method in the `api` class.
    """

    def __init__(self):
        super().__init__()
        self._indicators = {}
        self.api = api.ComplianceApi
        self.api_method = ""

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._record_argument_manager}, {len(self._indicators)} indicators>"

    @allowed_types(_BaseQueryBuilder, [_Indicator])
    def with_indicators(self: T, indicators: List[_Indicator]) -> T:
        """
        Add a list of indicators to evaluate compliance against.

        Parameters
        ----------
        indicators : list
            List of Indicator definitions

        Returns
        -------
        _RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialCompliance().with_indicators([WatchListIndicator(...)])...
        """

        for value in indicators:
            self._indicators[value.name] = value
        return self

    def run_query(
        self, api_instance: Union[api.ComplianceApi, api.ImpactedSubstancesApi], static_arguments: Dict
    ) -> Query_Result:
        api_method = getattr(api_instance, self.api_method)
        arguments = {**static_arguments, "indicators": [i.definition for i in self._indicators.values()]}

        indicators_text = ", ".join(self._indicators)
        logger.debug(f"[TECHDOCS] Indicators: {indicators_text}")

        result_raw = self._call_api(api_method, arguments)
        result = QueryResultFactory.create_result(results=result_raw, indicator_definitions=self._indicators)
        return result

    def _validate_parameters(self):
        if not self._indicators:
            warnings.warn(
                "No indicators have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )


class _ImpactedSubstanceMixin(_ApiMixin, ABC):
    """
    Handles the impacted substances aspects of a query.

    Includes adding legislation parameters to the query, generating the legislation-specific argument to be sent to
    Granta MI, and creating the impacted substance result objects.

    Attributes
    ----------
    _legislations : list
        The legislation names added to the query.
    api : object
        The class in the low-level API for this query type. Requires instantiation with the client object, and so only
        the reference to the class is stored here, not the instance itself.
    api_method : str
        The name of the method in the `api` class.
    """

    def __init__(self):
        super().__init__()
        self._legislations: List[str] = []
        self.api = api.ImpactedSubstancesApi
        self.api_method = ""

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._record_argument_manager}, {len(self._legislations)} legislations>"

    @allowed_types(_BaseQueryBuilder, [str])
    def with_legislations(self: T, legislation_names: List[str]) -> T:
        """
        Add a list of legislations to retrieve the impacted substances for.

        Parameters
        ----------
        legislation_names : str
            List of legislation names

        Returns
        -------
        _RecordBasedQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialImpactedSubstances() \
        ...         .with_legislations(["California Proposition 65 List",
                                        "REACH - The Candidate List"])...
        """

        self._legislations.extend(legislation_names)
        return self

    def run_query(
        self, api_instance: Union[api.ComplianceApi, api.ImpactedSubstancesApi], static_arguments: Dict
    ) -> Query_Result:
        api_method = getattr(api_instance, self.api_method)
        arguments = {"legislation_names": self._legislations, **static_arguments}

        legislations_text = ", ".join(['"' + leg + '"' for leg in self._legislations])
        logger.debug(f"[TECHDOCS] Legislation names: {legislations_text}")

        result_raw = self._call_api(api_method, arguments)
        if not result_raw:
            return []
        result = QueryResultFactory.create_result(results=result_raw)
        return result

    def _validate_parameters(self):
        if not self._legislations:
            warnings.warn(
                "No legislations have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )

    def _generate_arguments(self, db_key, query_config):
        return {
            "database_key": db_key,
            "legislation_names": self._legislations,
            "config": query_config,
        }


class _MaterialQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """
    Sub-class for all queries where the items added to the query are direct references to material records.
    """

    def __init__(self):
        super().__init__()
        self._record_argument_manager.record_type_name = "materials"
        self._record_argument_manager.batch_size = 100

    @allowed_types(_BaseQueryBuilder, [str])
    def with_material_ids(self: T, material_ids: List[str]) -> T:
        """
        Add a list of material ids to a material query.

        Parameters
        ----------
        material_ids : list(str)
            List of material ids to be added to the query

        Returns
        -------
        _MaterialQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = MaterialCompliance() \
        ...         .with_material_ids(['elastomer-butadienerubber',
        ...                             'NBR-100'])...
        """
        for material_id in material_ids:
            item_reference = self._definition_factory.create_definition_by_material_id(material_id=material_id)
            self._record_argument_manager.append_record_definition(item_reference)
        return self


class MaterialCompliance(_ComplianceMixin, _MaterialQueryBuilder):
    """
    Evaluate compliance for Granta MI material records against a number of indicators. If the materials are
    associated with substances, these are also evaluated and returned.

    All methods used to add materials and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> query = (
    ...     MaterialCompliance()
    ...     .with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
    ...     .with_indicators([WatchListIndicator(...)])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForMaterialsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_compliance_materials"


class MaterialImpactedSubstances(_ImpactedSubstanceMixin, _MaterialQueryBuilder):
    """
    Get the substances impacted by a list of legislations for Granta MI material records.

    All methods used to add materials and legislations to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> query = (
    ...     MaterialImpactedSubstances()
    ...     .with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
    ...     .with_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_materials"


class _PartQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """
    Sub-class for all queries where the items added to the query are direct references to part records.
    """

    def __init__(self):
        super().__init__()
        self._record_argument_manager.record_type_name = "parts"
        self._record_argument_manager.batch_size = 10

    @allowed_types(_BaseQueryBuilder, [str])
    def with_part_numbers(self: T, part_numbers: List[str]) -> T:
        """
        Add a list of part numbers to a part query.

        Parameters
        ----------
        part_numbers : list(str)
            List of part numbers to be added to the query

        Returns
        -------
        _PartQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = PartComplianceQuery().with_part_numbers(['ABC12345', 'Q356AQ'])...
        """

        for value in part_numbers:
            item_reference = self._definition_factory.create_definition_by_part_number(part_number=value)
            self._record_argument_manager.append_record_definition(item_reference)
        return self


class PartCompliance(_ComplianceMixin, _PartQueryBuilder):
    """
    Evaluate compliance for Granta MI part records against a number of indicators. If the parts are
    associated with materials, parts, specifications, or substances, these are also evaluated and returned.

    All methods used to add parts and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> query = (
    ...     PartComplianceQuery()
    ...    .with_part_numbers(['ABC12345', 'Q356AQ'])
    ...    .with_indicators([WatchListIndicator(...)])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForPartsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_compliance_parts"


class PartImpactedSubstances(_ImpactedSubstanceMixin, _PartQueryBuilder):
    """
    Get the substances impacted by a list of legislations for Granta MI part records.

    All methods used to add parts and legislations to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> query = (
    ...     PartImpactedSubstanceQuery()
    ...     .with_part_numbers(['ABC12345', 'Q356AQ'])
    ...     .with_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_parts"


class _SpecificationQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """
    Sub-class for all queries where the items added to the query are direct references to specification records.
    """

    def __init__(self):
        super().__init__()
        self._record_argument_manager.record_type_name = "specifications"
        self._record_argument_manager.batch_size = 10

    @allowed_types(_BaseQueryBuilder, [str])
    def with_specification_ids(self: T, specification_ids: List[str]) -> T:
        """
        Add a list of specification IDs to a specification query.

        Parameters
        ----------
        specification_ids : list(str)
            List of specification IDs to be added to the query

        Returns
        -------
        _SpecificationQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SpecificationComplianceQuery() \
        ...         .with_specification_ids(['MIL-A-8625', 'PSP101'])...
        """
        for specification_id in specification_ids:
            item_reference = self._definition_factory.create_definition_by_specification_id(
                specification_id=specification_id
            )
            self._record_argument_manager.append_record_definition(item_reference)
        return self


class SpecificationCompliance(_ComplianceMixin, _SpecificationQueryBuilder):
    """
    Evaluate compliance for Granta MI specification records against a number of indicators. If the
    specifications are associated with materials, specifications, or substances, these are also evaluated and returned.

    All methods used to add specifications and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> query = (
    ...     SpecificationComplianceQuery()
    ...     .with_specification_ids(['MIL-A-8625', 'PSP101'])
    ...     .with_indicators([WatchListIndicator(...)])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSpecificationsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_compliance_specifications"


class SpecificationImpactedSubstances(_ImpactedSubstanceMixin, _SpecificationQueryBuilder):
    """
    Get the substances impacted by a list of legislations for Granta MI specification records.

    All methods used to add specifications and legislations to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> query = (
    ...     SpecificationImpactedSubstanceQuery()
    ...     .with_specification_ids(['MIL-A-8625', 'PSP101'])
    ...     .with_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_specifications"


class _SubstanceQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """
    Sub-class for all queries where the items added to the query are direct references to substance records.
    """

    def __init__(self):
        super().__init__()
        self._record_argument_manager.record_type_name = "substances"
        self._record_argument_manager.batch_size = 500

    @allowed_types(_BaseQueryBuilder, [str])
    def with_cas_numbers(self: T, cas_numbers: List[str]) -> T:
        """
        Add a list of CAS numbers to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        cas_numbers : list(str)
            List of CAS numbers to be added to the query

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_cas_numbers(['50-00-0', '57-24-9'])...
        """
        for cas_number in cas_numbers:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [str])
    def with_ec_numbers(self: T, ec_numbers: List[str]) -> T:
        """
        Add a list of EC numbers to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        ec_numbers : list(str)
            List of EC numbers to be added to the query

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_ec_numbers(['200-001-8', '200-319-7'])...
        """
        for ec_number in ec_numbers:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number=ec_number)
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [str])
    def with_chemical_names(self: T, chemical_names: List[str]) -> T:
        """
        Add a list of chemical names to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        chemical_names : list(str)
            List of chemical names to be added to the query

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_chemical_names(['Formaldehyde', 'Strychnine'])...
        """
        for chemical_name in chemical_names:
            item_reference = self._definition_factory.create_definition_by_chemical_name(chemical_name=chemical_name)
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [(int, Number)])
    def with_record_history_ids_and_amounts(
        self: T, record_history_identities_and_amounts: List[Tuple[int, float]]
    ) -> T:
        """
        Add a list of record history identities and amounts to a substance query.

        Parameters
        ----------
        record_history_identities_and_amounts : list(tuple(int, float))
            List of tuples containing the record history identity and its wt % amount in the material/part

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery() \
        ...         .with_record_history_ids_and_amounts([(15321, 25), (17542, 0.1)])...
        """

        for record_history_id, amount in record_history_identities_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=record_history_id
            )
            item_reference.percentage_amount = amount
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [(str, Number)])
    def with_record_history_guids_and_amounts(self: T, record_history_guids_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of record history guids and amounts to a substance query.

        Parameters
        ----------
        record_history_guids_and_amounts : list(tuple(str, float))
            List of tuples containing the record history guid and its wt % amount in the material/part

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery() \
        ...         .with_record_history_guids_and_amounts([('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        ...                                                 ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)])...
        """
        for record_history_guid, amount in record_history_guids_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_history_guid(
                record_history_guid=record_history_guid
            )
            item_reference.percentage_amount = amount
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [(str, Number)])
    def with_record_guids_with_amounts(self: T, record_guids_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of record guids and amounts to a substance query.

        Parameters
        ----------
        record_guids_and_amounts : list(tuple(str, float))
            List of tuples containing the record guid and its wt % amount in the material/part

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery() \
        ...         .with_record_guids_with_amounts([('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        ...                                          ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)])...
        """

        for record_guid, amount in record_guids_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_guid(record_guid=record_guid)
            item_reference.percentage_amount = amount
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [(str, Number)])
    def with_cas_numbers_and_amounts(self: T, cas_numbers_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of CAS numbers and amounts to a substance query.

        Parameters
        ----------
        cas_numbers_and_amounts : list(tuple(str, float))
            List of tuples containing the CAS number and its wt % amount in the material/part

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery() \
        ...         .with_cas_numbers_and_amounts([('50-00-0', 25), ('57-24-9', 0.1)])...
        """

        for cas_number, amount in cas_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            item_reference.percentage_amount = amount
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [(str, Number)])
    def with_ec_numbers_and_amounts(self: T, ec_numbers_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of EC numbers and amounts to a substance query.

        Parameters
        ----------
        ec_numbers_and_amounts : list(tuple(str, float))
            List of tuples containing the EC number and its wt % amount in the material/part

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery() \
        ...         .with_ec_numbers_and_amounts([('200-001-8', 25), ('200-319-7', 0.1)])...
        """

        for ec_number, amount in ec_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number=ec_number)
            item_reference.percentage_amount = amount
            self._record_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(_BaseQueryBuilder, [(str, Number)])
    def with_chemical_names_and_amounts(self: T, chemical_names_and_amounts: List[Tuple[str, float]]) -> T:
        """
        Add a list of chemical names and amounts to a substance query.

        Parameters
        ----------
        chemical_names_and_amounts : list(tuple(str, float))
            List of tuples containing the chemical name and its wt % amount in the material/part

        Returns
        -------
        _SubstanceQueryBuilder
            The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery() \
        ...         .with_chemical_names_and_amounts([('Formaldehyde', 25), ('Strychnine', 0.1)])...
        """

        for chemical_name, amount in chemical_names_and_amounts:
            item_reference = self._definition_factory.create_definition_by_chemical_name(chemical_name=chemical_name)
            item_reference.percentage_amount = amount
            self._record_argument_manager.append_record_definition(item_reference)
        return self


class SubstanceCompliance(_ComplianceMixin, _SubstanceQueryBuilder):
    """
    Evaluate compliance for Granta MI substance records against a number of indicators.

    All methods used to add substances and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> result = (
    ...     SubstanceComplianceQuery()
    ...     .add_cas_numbers(['50-00-0', '57-24-9'])
    ...     .add_indicators([WatchListIndicator(...)])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_compliance_substances"


class _BomArgumentManager:
    """
    Store a Bom in 1711 XML format for use in queries.

    Examples
    --------
    >>> bom_item = _BomItem(bom = "<PartsEco xmlns...")
    >>> bom_item.bom_argument
    {"bom_xml1711": "<PartsEco xmlns..."}
    """

    def __init__(self, bom: str = ""):
        self.bom = bom

    def __repr__(self):
        return f'_BomArgumentManager {{bom: "{self.bom[:100]}"}}'

    @property
    def bom_argument(self) -> Dict[str, str]:
        """
        Return the bom in a dictionary with a key allowing it to be passed as a kwarg to the request constructor.

        Returns
        -------
        Dict of str, str
        """
        return {"bom_xml1711": self.bom}


class _Bom1711QueryBuilder(_BaseQueryBuilder, ABC):
    """
    Sub-class for all queries where the items added to the query are Boms.
    """

    def __init__(self):
        super().__init__()
        self._bom_definition = _BomArgumentManager()

    @allowed_types(_BaseQueryBuilder, str)
    def with_bom(self: T, bom: str) -> T:
        """
        Set the bom to be used for the query. Must be in the Granta 17/11 XML format. This format can be saved from the
        BoM Analyzer.

        Parameters
        ----------
        bom : str

        Examples
        --------
        >>> bom = "<PartsEco xmlns..."
        >>> query = BomComplianceQuery().with_bom(bom)...
        """

        self._bom_definition.bom = bom  # TODO: Validate the bom against the 17/11 schema
        return self


if TYPE_CHECKING:
    bom_base_class = _RecordBasedQueryBuilder, _ApiMixin
else:
    bom_base_class = object


class _Bom1711QueryOverride(bom_base_class):
    """
    Overrides the `_call_api` method in the `_ApiMixin` class.

    This is needed because the Bom1711 endpoints accept a single bom as opposed to a list of items.
    """

    def _call_api(self, api_method, arguments) -> List:
        args = {**arguments, **self._bom_definition.bom_argument}
        request = self._request_type(**args)
        response = api_method(body=request)
        return response


class BomCompliance(_Bom1711QueryOverride, _ComplianceMixin, _Bom1711QueryBuilder):
    """
    Evaluate compliance for a Bill of Materials in 17/11 XML format against a number of indicators.

    All methods used to add the Bill of Materials and indicators to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> bom = "<PartsEco xmlns..."
    >>> query = (
    ...     BomComplianceQuery()
    ...     .set_bom(bom)
    ...     .add_indicators([WatchListIndicator(...)])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Request
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_compliance_bom1711"


class BomImpactedSubstances(_Bom1711QueryOverride, _ImpactedSubstanceMixin, _Bom1711QueryBuilder):
    """
    Get the substances impacted by a list of legislations for a Bill of Materials in 17/11 XML format.

    All methods used to add the bom and legislations to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Attributes
    ----------
    api_method
        The name of the method on the `self.api` class that is called to run the query.

    Examples
    --------
    >>> cxn = Connection(...)
    >>> bom = "<PartsEco xmlns..."
    >>> result = (
    ...     BomImpactedSubstanceQuery()
    ...     .set_bom("<PartsEco xmlns...")
    ...     .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
    ... )
    >>> result = cxn.run(query)
    """

    def __init__(self):
        super().__init__()
        self._request_type = (
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Request  # noqa: E501
        )
        self.api_method = "post_miservicelayer_bom_analytics_v1svc_impactedsubstances_bom1711"


class Yaml:
    @staticmethod
    def get_yaml(connection: Connection):
        return api.DocumentationApi(connection).get_miservicelayer_bom_analytics_v1svc_yaml()
