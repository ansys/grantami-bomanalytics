"""BoM Analytics query builders.

Describes and implements the main interface for the Bom Analytics API. The builder objects here define
the creation, validation, and execution of Impacted Substances and Compliance queries. One separate
static class outside the main hierarchy implements the Yaml API endpoint.

Attributes
----------
Query_Builder
    Generic type for builder configuration methods. Ensures that the specific sub-class of the
    object to which the method is bound is hinted as the return type, e.g. that if `.with_record_guid()`
    is called on a `SpecificationCompliance` object, then the return type is correctly identified as
    `SpecificationCompliance`.
Query_Result
    The type of the result object. Can be any type that inherits from either a `ComplianceBaseClass` or
    `ImpactedSubstancesBaseClass`, i.e. all result types.
"""

from abc import ABC, abstractmethod
from typing import Union, List, Dict, Tuple, TypeVar, TYPE_CHECKING, Callable, Generator, Optional, Type
import warnings
from numbers import Number
import logging

from ansys.grantami.bomanalytics_openapi import models, api  # type: ignore[import]

from ._item_definitions import AbstractBomFactory, RecordDefinition, PartDefinition  # noqa: F401
from ._allowed_types import allowed_types
from ._query_results import (
    QueryResultFactory,
    ComplianceBaseClass,
    ImpactedSubstancesBaseClass,
)
from .indicators import _Indicator, WatchListIndicator, RoHSIndicator
from ._connection import Connection  # noqa: F401

Query_Builder = TypeVar("Query_Builder", covariant=True, bound=Union["_BaseQueryBuilder", "_ApiMixin"])
Query_Result = TypeVar("Query_Result", covariant=True, bound=Union[ComplianceBaseClass, ImpactedSubstancesBaseClass])

logger = logging.getLogger(__name__)


class _BaseArgumentManager(ABC):
    """Outlines an interface for managing 'items' to be provided to the query, i.e. the record or BoM-based dimension
    to a query.

    Doesn't specify how the objects are added to the `_items` attribute, or how they are converted to attributes.
    """

    _items: List
    """ Describes the bom items to be passed to the low-level API. The type is determined in the concrete class. """

    @property
    def is_populated(self) -> bool:
        """Is this ArgumentManager populated, i.e. can a query be performed on the items in this object.

        Returns
        -------
            The boolean cast of the `_items` attribute.
        """

        return bool(self._items)

    @abstractmethod
    def extract_results_from_response(self, response: models.Model) -> List[models.Model]:
        pass


class _RecordArgumentManager(_BaseArgumentManager):
    """Store records for use in queries and generate the list of models to be sent to the server.

    Implements the `_items` attribute as a list, allowing for multiple records to be added to a single query.

    Parameters
    ----------
    item_type_name
        The name of the items as defined by the low-level API, e.g. "materials", "parts".
    batch_size
        The number of items to be included in a single request.
    """

    def __init__(self, item_type_name: str = "", batch_size: Optional[int] = None) -> None:
        super().__init__()
        self._items = []
        """ The name of the item collection as defined by the low-level API, e.g. 'materials', 'parts'. """
        self.item_type_name = item_type_name
        self.batch_size: Optional[int] = batch_size

    def __str__(self) -> str:
        if not self.item_type_name:
            return "Uninitialized"
        else:
            return f"{len(self._items)} {self.item_type_name}, batch size = {self.batch_size}"

    def __repr__(self) -> str:
        if not self.item_type_name:
            item_text = "record_type_name: None"
        else:
            item_text = f'record_type_name: "{self.item_type_name}"'
        if not self.batch_size:
            batch_text = "batch_size: None"
        else:
            batch_text = f"batch_size: {self.batch_size}"
        return f"<{self.__class__.__name__} {{{item_text}, {batch_text}}}, length = {len(self._items)}>"

    def append_record_definition(self, item: RecordDefinition) -> None:
        """Append a specific record definition to the argument manager.

        Parameters
        ----------
        item
            The definition to be added to this list of record definitions.

        Examples
        --------
        >>> part_definition = PartDefinition(...)
        >>> items = _RecordArgumentManager(item_type_name = "parts", batch_size = 100)
        >>> items.append_record_definition(part_definition)
        """
        if not all(item.record_reference.values()):
            raise TypeError(
                "Attempted to add a RecordDefinition-derived object with a null record reference to a"
                " query. This is not supported; RecordDefinition-derived objects without record references"
                " can only be used as result objects for BoM queries."
            )
        self._items.append(item)

    @property
    def batched_arguments(self) -> Generator[Dict[str, List[Union[models.Model, str]]], None, None]:
        """A generator producing item request arguments as a list of instances of the appropriate Model. Each list
        of dicts will be at most `_batch_size` long.

        Each individual dict can be passed to the request constructor as a kwarg.

        Yields
        ------
            Batched **kwargs.

        Raises
        ------
        RuntimeError
            If the `item_type_name` has not been set before the arguments are generated.

        Examples
        --------
        >>> items = _RecordArgumentManager(item_type_name = "materials", batch_size = 100)
        >>> items.batched_arguments
        {"materials": [{"reference_type": "material_id", "reference_value": "ABS"}, ...]  # Up to 100 items
        """

        if not self.item_type_name:
            raise RuntimeError('"item_type_name" must be populated before record arguments can be generated.')
        if self.batch_size is None:
            raise RuntimeError('"batch_size" must be populated before record arguments can be generated.')

        for batch_number, i in enumerate(range(0, len(self._items), self.batch_size)):
            batch = [i._definition for i in self._items][i : i + self.batch_size]  # noqa: E203 E501
            batch_str = ", ".join([f'"{item.reference_type}": "{item.reference_value}"' for item in batch])
            logger.debug(f"[TECHDOCS] Batch {batch_number + 1}, Items: {batch_str}")
            yield {self.item_type_name: batch}

    def extract_results_from_response(self, response: models.Model) -> List[models.Model]:
        """Extracts the individual results from a response object.

        Returns
        -------
            The attribute containing the list of results identified by `self.record_type_name`.
        """

        results: List[models.Model] = getattr(response, self.item_type_name)
        return results


class _BaseQueryBuilder(ABC):
    """Base class for all queries."""

    def _validate_items(self) -> None:
        """Perform pre-flight checks on the items that have been added to the query.

        Warns
        -----
        RuntimeWarning
            If no items have been added to the query, warn that the response will be empty.
        """

        if not self._item_argument_manager.is_populated:  # type: ignore[attr-defined]
            warnings.warn(
                f"No {self._item_argument_manager.item_type_name} have been added to the "  # type: ignore[attr-defined]
                "query. Server response will be empty.",
                RuntimeWarning,
            )


class _RecordBasedQueryBuilder(_BaseQueryBuilder, ABC):
    """Base class for all record-based query types.

    The properties and methods here primarily represent generic record identifiers. `.with_batch_size()` is implemented
    here, since record-based queries are the only queries which can operate on multiple items.
    """

    def __init__(self) -> None:
        self._item_argument_manager = _RecordArgumentManager()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._item_argument_manager}>"

    @allowed_types(object, int)
    def with_batch_size(self: Query_Builder, batch_size: int) -> Query_Builder:
        """Set the number of records included in a single request for this query.

        Default values are set based on typical usage of the Restricted Substances database. This value can be changed
        to optimize performance if required on a query-by-query basis if it is known that certain records contain
        particcularly large or small numbers of associated records.

        Parameters
        ----------
        batch_size
            The number of records included in a single request.

        Returns
        -------
            The current query builder.

        Raises
        ------
        ValueError
            If a number less than 1 is set as the batch size.

        Notes
        -----
        The Restricted Substances database makes extensive use of tabular data and associated records to store the
        complex hierarchical relationships that define compliance of products, assemblies, parts, specifications,
        and materials. As a result, it is impossible to determine the complexity of a particular query without knowing
        precisely how many records are related to the record included in the query.

        The default batch sizes are set for each record type and represent appropriate numbers of those records to be
        included in the same request assuming typical numbers of associated records.

        Even if the records are queried in multiple batches, the results will be assembled into a single result object.

        Examples
        --------
        >>> MaterialComplianceQuery().with_batch_size(50)
        <MaterialCompliance: 0 materials, batch size = 50, 0 indicators>
        """

        if batch_size < 1:
            raise ValueError("Batch must be a positive integer")
        self._item_argument_manager.batch_size = batch_size
        return self

    @allowed_types(object, [int])
    def with_record_history_ids(self: Query_Builder, record_history_identities: List[int]) -> Query_Builder:
        """Add a list of record history identities to a query.

        Parameters
        ----------
        record_history_identities
            List of record history identities to be added to the query

        Returns
        -------
            The current query builder.

        Examples
        --------
        >>> MaterialComplianceQuery().with_record_history_ids([15321, 17542, 942])
        <MaterialCompliance: 3 materials, batch size = 50, 0 indicators>
        """

        for value in record_history_identities:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=value
            )
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [str])
    def with_record_history_guids(self: Query_Builder, record_history_guids: List[str]) -> Query_Builder:
        """Add a list of record history guids to a query.

        Parameters
        ----------
        record_history_guids
            List of record history guids to be added to the query

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.with_record_history_guids(['41e20a88-d496-4735-a177-6266fac9b4e2',
        >>>                                  'd117d9ad-e6a9-4ba9-8ad8-9a20b6d0b5e2'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for value in record_history_guids:
            item_reference = self._definition_factory.create_definition_by_record_history_guid(
                record_history_guid=value
            )
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [str])
    def with_record_guids(self: Query_Builder, record_guids: List[str]) -> Query_Builder:
        """Add a list of record guids to a query.

        Parameters
        ----------
        record_guids
            List of record guids to be added to the query

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query = query.with_record_guids(['bdb0b880-e6ee-4f1a-bebd-af76959ae3c8',
        >>>                                  'a98cf4b3-f96a-4714-9f79-afe443982c69'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for value in record_guids:
            item_reference = self._definition_factory.create_definition_by_record_guid(record_guid=value)
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [{str: str}])
    def with_stk_records(self: Query_Builder, stk_records: List[Dict[str, str]]) -> Query_Builder:
        """Add a list of records generated by the Scripting Toolkit.

        Parameters
        ----------
        stk_records
            List of record definitions

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> MaterialComplianceQuery().with_stk_records(stk_records)
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        record_guids: List[str] = [r["record_guid"] for r in stk_records]  # TODO Handle database key
        query_builder: Query_Builder = self.with_record_guids(record_guids)
        return query_builder


if TYPE_CHECKING:
    api_base_class = _BaseQueryBuilder
else:
    api_base_class = object


class _ApiMixin(api_base_class):
    """Base class for API-specific mixins.

    Describes generic properties of a call to an API (e.g. calling the API, processing results). Also defines abstract
    concepts related to the parameter dimension of a query, including validation.
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type: Type[models.Model]
        """The type of object to be sent to the Granta MI server. The actual value is set in the concrete class
         definition."""

    def _call_api(self, api_method: Callable[[models.Model], models.Model], arguments: Dict) -> List[models.Model]:
        """Perform the actual call against the Granta MI database.

        Finalizes the arguments by appending each batch of 'item' arguments to the passed in dict,
        and uses them to instantiate the request object. Passes the request object to the low-level API. Returns
        the response as a list.

        Parameters
        ----------
        api_method
            The method bound to the `api.ComplianceApi` or `api.ImpactedSubstanceApi` instance.
        arguments
            The state of the query as a set of low-level API kwargs. Includes everything except the batched items.

        Returns
        -------
            The results from the low-level API. The type varies depending on the specific query, but is a sub-type of
            `models.Model`.
        """

        self._validate_parameters()
        self._validate_items()
        result = []
        for batch in self._item_argument_manager.batched_arguments:  # type: ignore[attr-defined]
            args = {**arguments, **batch}
            request = self._request_type(**args)
            response = api_method(request)
            result.extend(
                self._item_argument_manager.extract_results_from_response(response)  # type: ignore[attr-defined]
            )
        return result

    @abstractmethod
    def _run_query(
        self, api_instance: Union[api.ComplianceApi, api.ImpactedSubstancesApi], static_arguments: Dict
    ) -> Query_Result:
        pass

    @abstractmethod
    def _validate_parameters(self) -> None:
        pass


class _ComplianceMixin(_ApiMixin, ABC):
    """Implements the compliance aspects of a query.

    Includes adding indicator parameters to the query, generating the indicator-specific argument to be sent to Granta
    MI, and creating the compliance result objects.
    """

    def __init__(self) -> None:
        super().__init__()
        self._indicators: Dict[str, _Indicator] = {}
        """The indicators added to the query."""

        self._api_method: str = ""
        """The name of the method in the `api` class. Specified in the concrete class. Retrieved dynamically because the
        `api` instance doesn't exist until runtime."""

        self.api_class: Type[api.ComplianceApi] = api.ComplianceApi
        """The class in the low-level API for this query type. Requires instantiation with the client object, and so
        only the reference to the class is stored here, not the instance itself."""

    def __repr__(self) -> str:
        result = (
            f"<{self.__class__.__name__}: {self._item_argument_manager},"  # type: ignore[attr-defined]
            f" {len(self._indicators)} indicators>"
        )
        return result

    @allowed_types(object, [_Indicator])
    def with_indicators(
        self: Query_Builder, indicators: List[Union[WatchListIndicator, RoHSIndicator]]
    ) -> Query_Builder:
        """Add a list of indicators against which to evaluate compliance.

        Parameters
        ----------
        indicators
            List of Indicator definitions to be included in this query.

        Returns
        -------
            The current query builder.

        Examples
        --------
        >>> indicator = WatchListIndicator(
        ...     name="Prop 65",
        ...     legislation_names=["California Proposition 65 List"]
        ... )
        >>> MaterialComplianceQuery().with_indicators([indicator])
        <MaterialCompliance: 0 materials, batch size = 100, 1 indicators>
        """

        for value in indicators:
            self._indicators[value.name] = value
        return self

    def _run_query(self, api_instance: api.ComplianceApi, static_arguments: Dict) -> Query_Result:
        """Passes the current state of the query as arguments to Granta MI and returns the results.

        This method should not be used by an end-user, use the `BomAnalyticsClient.run()` method instead.

        Parameters
        ----------
        api_instance
            The instance of the low-level ComplianceApi class.
        static_arguments
            The arguments set at the connection level, which includes the database key and any custom table names.

        Returns
        -------
            The exact type of the result depends on the query.

        Notes
        -----
        Gets the bound method for this particular query from `api_instance` and passes it to `self._call_api()` which
        performs the actual call. Passes the result to the `QueryResultFactory` to build the corresponding result
        object.

        The `indicator_definitions` are used to create the QueryResult object, since only the indicator names
        and results are returned from the low-level API.
        """

        api_method = getattr(api_instance, self._api_method)
        arguments = {**static_arguments, "indicators": [i._definition for i in self._indicators.values()]}

        indicators_text = ", ".join(self._indicators)
        logger.debug(f"[TECHDOCS] Indicators: {indicators_text}")

        result_raw = self._call_api(api_method, arguments)
        result: Query_Result = QueryResultFactory.create_result(
            results=result_raw, indicator_definitions=self._indicators
        )
        return result

    def _validate_parameters(self) -> None:
        """Perform pre-flight checks on the indicators that have been added to the query.

        Warns
        -----
        RuntimeWarning
            If no indicators have been added to the query, warn that the response will be empty.
        """

        if not self._indicators:
            warnings.warn(
                "No indicators have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )


class _ImpactedSubstanceMixin(_ApiMixin, ABC):
    """Implements the impacted substances aspects of a query.

    Includes adding legislation parameters to the query, generating the legislation-specific argument to be sent to
    Granta MI, and creating the impacted substance result objects.
    """

    def __init__(self) -> None:
        super().__init__()
        self._legislations: List[str] = []
        """The legislation names added to the query."""

        self._api_method: str = ""
        """The name of the method in the `api` class. Specified in the concrete class. Retrieved dynamically because the
        `api` instance doesn't exist until runtime."""

        self.api_class: Type[api.ImpactedSubstancesApi] = api.ImpactedSubstancesApi
        """The class in the low-level API for this query type. Requires instantiation with the client object, and so
        only the reference to the class is stored here, not the instance itself."""

    def __repr__(self) -> str:
        result = (
            f"<{self.__class__.__name__}: {self._item_argument_manager}, "  # type: ignore[attr-defined]
            f"{len(self._legislations)} legislations>"
        )
        return result

    @allowed_types(object, [str])
    def with_legislations(self: Query_Builder, legislation_names: List[str]) -> Query_Builder:
        """Add a list of legislations to retrieve the impacted substances for.

        Parameters
        ----------
        legislation_names
            List of legislation names to be added to the query.

        Returns
        -------
            The current query builder.

        Examples
        --------
        >>> query = MaterialImpactedSubstancesQuery()
        >>> query = query.with_legislations(["California Proposition 65 List",
        >>>                                  "REACH - The Candidate List"])
        <MaterialImpactedSubstances: 0 materials, batch size = 100, 2 legislations>
        """

        self._legislations.extend(legislation_names)
        return self

    def _run_query(self, api_instance: api.ImpactedSubstancesApi, static_arguments: Dict) -> Query_Result:
        """Passes the current state of the query as arguments to Granta MI and returns the results.

        Gets the bound method for this particular query from `api_instance` and passes it to `self._call_api()` which
        performs the actual call. Passes the result to the `QueryResultFactory` to build the corresponding result
        object.

        Parameters
        ----------
        api_instance
            The instance of the low-level ImpactedSubstancesApi class.
        static_arguments
            The arguments set at the connection level, which includes the database key and any custom table names.

        Returns
        -------
            The result of the query. The exact type of the result depends on the query that was run.
        """

        api_method = getattr(api_instance, self._api_method)
        arguments = {"legislation_names": self._legislations, **static_arguments}

        legislations_text = ", ".join(['"' + leg + '"' for leg in self._legislations])
        logger.debug(f"[TECHDOCS] Legislation names: {legislations_text}")

        result_raw = self._call_api(api_method, arguments)
        result: Query_Result = QueryResultFactory.create_result(results=result_raw)
        return result

    def _validate_parameters(self) -> None:
        """Perform pre-flight checks on the legislations that have been added to the query.

        Warns
        -----
        RuntimeWarning
            If no legislations have been added to the query, warn that the response will be empty.
        """

        if not self._legislations:
            warnings.warn(
                "No legislations have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )


class _MaterialQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are direct references to material records."""

    def __init__(self) -> None:
        super().__init__()
        self._item_argument_manager.item_type_name = "materials"
        self._item_argument_manager.batch_size = 100

    @allowed_types(object, [str])
    def with_material_ids(self: Query_Builder, material_ids: List[str]) -> Query_Builder:
        """Add a list of materials referenced by Material ID attribute value to a material query.

        Material IDs are valid for both *MaterialUnvierse* and *Materials - in house* records.

        Parameters
        ----------
        material_ids
            List of Material ID values to be added to the query

        Returns
        -------
            The current query builder.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for material_id in material_ids:
            item_reference = self._definition_factory.create_definition_by_material_id(material_id=material_id)
            self._item_argument_manager.append_record_definition(item_reference)
        return self


class MaterialComplianceQuery(_ComplianceMixin, _MaterialQueryBuilder):
    """Evaluate compliance for Granta MI material records against a number of indicators. If the materials are
    associated with substances, these are also evaluated and returned.

    All methods used to add materials and indicators to this query return the query itself, so they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    type :class:`ansys.granta.bom_analytics._query_results.MaterialComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_names=["California Proposition 65 List"]
    ... )
    >>> query = (
    ...     MaterialComplianceQuery()
    ...     .with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
    ...     .with_indicators([indicator])
    ... )
    >>> cxn.run(query)
    <MaterialComplianceQueryResult: 2 MaterialWithCompliance results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = models.GetComplianceForMaterialsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_compliance_materials"


class MaterialImpactedSubstancesQuery(_ImpactedSubstanceMixin, _MaterialQueryBuilder):
    """Get the substances impacted by a list of legislations for Granta MI material records.

    All methods used to add materials and legislations to this query return the query itself, so they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    type :class:`ansys.granta.bom_analytics._query_results.MaterialImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> query = (
    ...     MaterialImpactedSubstancesQuery()
    ...     .with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
    ...     .with_legislations(["REACH - The Candidate List"])
    ... )
    >>> cxn.run(query)
    <MaterialImpactedSubstancesQueryResult: 2 MaterialWithImpactedSubstances results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = (
            models.GetImpactedSubstancesForMaterialsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_impactedsubstances_materials"


class _PartQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are direct references to part records."""

    def __init__(self) -> None:
        super().__init__()
        self._item_argument_manager.item_type_name = "parts"
        self._item_argument_manager.batch_size = 10

    @allowed_types(object, [str])
    def with_part_numbers(self: Query_Builder, part_numbers: List[str]) -> Query_Builder:
        """Add a list of part numbers to a part query.

        Parameters
        ----------
        part_numbers
            List of part numbers to be added to the query

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = PartComplianceQuery().with_part_numbers(['DRILL', 'FLRY34'])
        <PartCompliance: 2 parts, batch size = 10, 0 indicators>
        """

        for value in part_numbers:
            item_reference = self._definition_factory.create_definition_by_part_number(part_number=value)
            self._item_argument_manager.append_record_definition(item_reference)
        return self


class PartComplianceQuery(_ComplianceMixin, _PartQueryBuilder):
    """Evaluate compliance for Granta MI part records against a number of indicators. If the parts are
    associated with materials, parts, specifications, or substances, these are also evaluated and returned.

    All methods used to add parts and indicators to this query return the query itself, so they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    type :class:`ansys.granta.bom_analytics._query_results.PartComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_names=["California Proposition 65 List"]
    ... )
    >>> query = (
    ...     PartComplianceQuery()
    ...     .with_part_numbers(['DRILL', 'FLRY34'])
    ...     .with_indicators([indicator])
    ... )
    >>> cxn.run(query)
    <PartComplianceQueryResult: 2 PartWithCompliance results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = models.GetComplianceForPartsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_compliance_parts"


class PartImpactedSubstancesQuery(_ImpactedSubstanceMixin, _PartQueryBuilder):
    """Get the substances impacted by a list of legislations for Granta MI part records.

    All methods used to add parts and legislations to this query return the query itself, so they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    type :class:`ansys.granta.bom_analytics._query_results.PartImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> query = (
    ...     PartImpactedSubstancesQuery()
    ...     .with_part_numbers(['DRILL', 'FLRY34'])
    ...     .with_legislations(["REACH - The Candidate List"])
    ... )
    >>> cxn.run(query)
    <PartImpactedSubstancesQueryResult: 2 PartWithImpactedSubstances results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = (
            models.GetImpactedSubstancesForPartsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_impactedsubstances_parts"


class _SpecificationQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are direct references to specification records."""

    def __init__(self) -> None:
        super().__init__()
        self._item_argument_manager.item_type_name = "specifications"
        self._item_argument_manager.batch_size = 10

    @allowed_types(object, [str])
    def with_specification_ids(self: Query_Builder, specification_ids: List[str]) -> Query_Builder:
        """Add a list of specification IDs to a specification query.

        Parameters
        ----------
        specification_ids
            List of specification IDs to be added to the query

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SpecificationComplianceQuery()
        >>> query.with_specification_ids(['MIL-A-8625', 'PSP101'])
        <SpecificationComplianceQuery: 2 specifications, batch size = 10, 0 indicators>
        """

        for specification_id in specification_ids:
            item_reference = self._definition_factory.create_definition_by_specification_id(
                specification_id=specification_id
            )
            self._item_argument_manager.append_record_definition(item_reference)
        return self


class SpecificationComplianceQuery(_ComplianceMixin, _SpecificationQueryBuilder):
    """Evaluate compliance for Granta MI specification records against a number of indicators. If the
    specifications are associated with materials, specifications, or substances, these are also evaluated and returned.

    All methods used to add specifications and indicators to this query return the query itself, so they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    type :class:`ansys.granta.bom_analytics._query_results.SpecificationComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_names=["California Proposition 65 List"]
    ... )
    >>> query = (
    ...     SpecificationComplianceQuery()
    ...     .with_specification_ids(['MIL-A-8625', 'PSP101'])
    ...     .with_indicators([indicator])
    ... )
    >>> cxn.run(query)
    <SpecificationComplianceQueryResult: 2 SpecificationWithCompliance results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = (
            models.GetComplianceForSpecificationsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_compliance_specifications"


class SpecificationImpactedSubstancesQuery(_ImpactedSubstanceMixin, _SpecificationQueryBuilder):
    """Get the substances impacted by a list of legislations for Granta MI specification records.

    All methods used to add specifications and legislations to this query return the query itself, so they can be
    chained together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    type :class:`ansys.granta.bom_analytics._query_results.SpecificationImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> query = (
    ...     SpecificationImpactedSubstancesQuery()
    ...     .with_specification_ids(['MIL-A-8625', 'PSP101'])
    ...     .with_legislations(["REACH - The Candidate List"])
    ... )
    >>> cxn.run(query)
    <SpecificationImpactedSubstancesQueryResult:
                    2 SpecificationWithImpactedSubstances results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = (
            models.GetImpactedSubstancesForSpecificationsRequest  # noqa: E501
        )
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_impactedsubstances_specifications"


class _SubstanceQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are direct references to substance records."""

    def __init__(self) -> None:
        super().__init__()
        self._item_argument_manager.item_type_name = "substances"
        self._item_argument_manager.batch_size = 500

    @allowed_types(object, [str])
    def with_cas_numbers(self: Query_Builder, cas_numbers: List[str]) -> Query_Builder:
        """Add a list of CAS numbers to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        cas_numbers
            List of CAS numbers to be added to the query

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_cas_numbers(['50-00-0', '57-24-9'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for cas_number in cas_numbers:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [str])
    def with_ec_numbers(self: Query_Builder, ec_numbers: List[str]) -> Query_Builder:
        """Add a list of EC numbers to a substance query. The amount of substance in the material will be set to 100%.

        Parameters
        ----------
        ec_numbers
            List of EC numbers to be added to the query

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_ec_numbers(['200-001-8', '200-319-7'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for ec_number in ec_numbers:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number=ec_number)
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [str])
    def with_chemical_names(self: Query_Builder, chemical_names: List[str]) -> Query_Builder:
        """Add a list of chemical names to a substance query. The amount of substance in the material will be set to
        100%.

        Parameters
        ----------
        chemical_names
            List of chemical names to be added to the query

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_chemical_names(['Formaldehyde', 'Strychnine'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for chemical_name in chemical_names:
            item_reference = self._definition_factory.create_definition_by_chemical_name(chemical_name=chemical_name)
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [(int, Number)])
    def with_record_history_ids_and_amounts(
        self: Query_Builder, record_history_identities_and_amounts: List[Tuple[int, float]]
    ) -> Query_Builder:
        """Add a list of record history identities and amounts to a substance query.

        Parameters
        ----------
        record_history_identities_and_amounts
            List of tuples containing the record history identity and its wt % amount in the material/part

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_record_history_ids_and_amounts([(15321, 25), (17542, 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for record_history_id, amount in record_history_identities_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=record_history_id
            )
            item_reference.percentage_amount = amount
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [(str, Number)])
    def with_record_history_guids_and_amounts(
        self: Query_Builder, record_history_guids_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list of record history guids and amounts to a substance query.

        Parameters
        ----------
        record_history_guids_and_amounts
            List of tuples containing the record history guid and its wt % amount in the material/part

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_record_history_guids_and_amounts(
        ...     [('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        ...      ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)]
        ... )
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>

        """
        for record_history_guid, amount in record_history_guids_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_history_guid(
                record_history_guid=record_history_guid
            )
            item_reference.percentage_amount = amount
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [(str, Number)])
    def with_record_guids_and_amounts(
        self: Query_Builder, record_guids_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list of record guids and amounts to a substance query.

        Parameters
        ----------
        record_guids_and_amounts
            List of tuples containing the record guid and its wt % amount in the material/part

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_record_guids_and_amounts(
        ...     [('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        ...      ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)]
        ... )
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for record_guid, amount in record_guids_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_guid(record_guid=record_guid)
            item_reference.percentage_amount = amount
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [(str, Number)])
    def with_cas_numbers_and_amounts(
        self: Query_Builder, cas_numbers_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list of CAS numbers and amounts to a substance query.

        Parameters
        ----------
        cas_numbers_and_amounts
            List of tuples containing the CAS number and its wt % amount in the material/part

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_cas_numbers_and_amounts([('50-00-0', 25), ('57-24-9', 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for cas_number, amount in cas_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            item_reference.percentage_amount = amount
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [(str, Number)])
    def with_ec_numbers_and_amounts(
        self: Query_Builder, ec_numbers_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list of EC numbers and amounts to a substance query.

        Parameters
        ----------
        ec_numbers_and_amounts
            List of tuples containing the EC number and its wt % amount in the material/part

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_ec_numbers_and_amounts([('200-001-8', 25),
        ...                                            ('200-319-7', 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for ec_number, amount in ec_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number=ec_number)
            item_reference.percentage_amount = amount
            self._item_argument_manager.append_record_definition(item_reference)
        return self

    @allowed_types(object, [(str, Number)])
    def with_chemical_names_and_amounts(
        self: Query_Builder, chemical_names_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list of chemical names and amounts to a substance query.

        Parameters
        ----------
        chemical_names_and_amounts
            List of tuples containing the chemical name and its wt % amount in the material/part

        Returns
        -------
        The current query builder.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_chemical_names_and_amounts([('Formaldehyde', 25),
        ...                                                ('Strychnine', 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for chemical_name, amount in chemical_names_and_amounts:
            item_reference = self._definition_factory.create_definition_by_chemical_name(chemical_name=chemical_name)
            item_reference.percentage_amount = amount
            self._item_argument_manager.append_record_definition(item_reference)
        return self


class SubstanceComplianceQuery(_ComplianceMixin, _SubstanceQueryBuilder):
    """Evaluate compliance for Granta MI substance records against a number of indicators.

    All methods used to add substances and indicators to this query return the query itself, so they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    :class:`ansys.granta.bom_analytics._query_results.SubstanceComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_names=["California Proposition 65 List"]
    ... )
    >>> query = (
    ...     SubstanceComplianceQuery()
    ...     .with_cas_numbers(['50-00-0', '57-24-9'])
    ...     .with_indicators([indicator])
    ... )
    >>> cxn.run(query)
    <SubstanceComplianceQueryResult: 2 SubstanceWithCompliance results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = models.GetComplianceForSubstancesRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_compliance_substances"


class _BomArgumentManager(_BaseArgumentManager):
    """Store a bom for use in queries and generate the kwarg to be sent to the server.

    `_items` must be a list because of the base class, but only ever contains a single string since only one Bom can be
     sent to the server in a single query.
    """

    def __init__(self) -> None:
        self.item_type_name = "bom_xml1711"
        self._items = [""]

    def __repr__(self) -> str:
        return f'<_BomArgumentManager {{bom: "{self._items[0][:100]}"}}>'

    @property
    def bom(self) -> str:
        """Since only one Bom is used per query, this property enforces the fact that only one Bom can be stored per
         instance of `_BomArgumentManager`.

        Returns
        -------
        bom
            The Bom that will be used for the query.
        """
        bom: str = self._items[0]
        return bom

    @bom.setter
    def bom(self, value: str) -> None:
        self._items = [value]

    @property
    def batched_arguments(self) -> List[Dict[str, str]]:
        """Return the bom in a dictionary with a key allowing it to be passed as a kwarg to the request constructor.

        Returns
        -------
            Bom with the appropriate keyword argument.

        Examples
        --------
        >>> bom_item = _BomArgumentManager(bom = "<PartsEco xmlns...")
        >>> bom_item.batched_arguments
        {"bom_xml1711": "<PartsEco xmlns..."}
        """

        return [{self.item_type_name: self._items[0]}]

    def extract_results_from_response(self, response: models.Model) -> List[models.Model]:
        """Extracts the individual results from a response object.

        For Bom queries, the result isn't contained within a larger response object, it's already the object we want.

        Returns
        -------
            The response wrapped in a list.
        """
        return [response]


class _Bom1711QueryBuilder(_BaseQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are Boms."""

    def __init__(self) -> None:
        self._item_argument_manager = _BomArgumentManager()

    @allowed_types(object, str)
    def with_bom(self: Query_Builder, bom: str) -> Query_Builder:
        """Set the bom to be used for the query.

        The Bom must be in the Ansys Granta 17/11 XML format.

        Parameters
        ----------
        bom
            The BoM to be added to the query.

        Notes
        -----
        The XML schema is defined by the schema document
        :download:`BillOfMaterialsEco.xsd </_static/BillOfMaterialsEco.xsd>`, which in turn references
        :download:`grantarecord1205.xsd</_static/grantarecord1205.xsd>`. Together, these XSD files can be used to
        validate that the BoM is both valid XML and adheres to the 17/11 BoM XML schema.

        Examples
        --------
        >>> my_bom = "<PartsEco xmlns..."
        >>> query = BomComplianceQuery().with_bom(my_bom)
        """

        self._item_argument_manager.bom = bom
        return self


class BomComplianceQuery(_ComplianceMixin, _Bom1711QueryBuilder):
    """Evaluate compliance for a Bill of Materials in the Ansys Granta 17/11 XML format against a number of indicators.

    All Bom-based queuries can only operate on a single Bom. As a result, the `.with_batch_size()` method is not
    implemented for Bom-based queries.

    The methods used to add the Bom and indicators to this query return the query itself, so they can be
    chained together as required.

    Once the query is fully constructed, use the :meth:`BomAnalyticsClient.run` method to return a result of
    :class:`ansys.granta.bom_analytics._query_results.PartComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> bom = "<PartsEco xmlns..."
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_names=["California Proposition 65 List"]
    ... )
    >>> query = (
    ...     BomComplianceQuery()
    ...     .with_bom(bom)
    ...     .with_indicators([indicator])
    ... )
    >>> cxn.run(query)
    <BomComplianceQueryResult: 1 PartWithCompliance results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = models.GetComplianceForBom1711Request
        self._api_method = "post_compliance_bom1711"


class BomImpactedSubstancesQuery(_ImpactedSubstanceMixin, _Bom1711QueryBuilder):
    """Get the substances impacted by a list of legislations for a Bill of Materials in the Ansys Granta 17/11 XML
     format.

    All Bom-based queuries can only operate on a single Bom. As a result, the `.with_batch_size()` method is not
    implemented for Bom-based queries.

    All methods used to add the Bom and legislations to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> bom = "<PartsEco xmlns..."
    >>> query = (
    ...     BomImpactedSubstancesQuery()
    ...     .with_bom("<PartsEco xmlns...")
    ...     .with_legislations(["REACH - The Candidate List"])
    ... )
    >>> cxn.run(query)
    <BomImpactedSubstancesQueryResult: 1 Bom1711WithImpactedSubstances results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = (
            models.GetImpactedSubstancesForBom1711Request  # noqa: E501
        )
        self._api_method = "post_impactedsubstances_bom1711"


class Yaml:
    """Gets the yaml description of the underlying REST API.

    The API is fully implemented in this package, so the description is unlikely to be useful to end users. It is
    provided for completeness only.

    This class only contains static methods and class attributes, so can be used without instantiation.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().build()
    >>> cxn.run(Yaml)
    openapi: 3.0.1
    info:
      title: Granta.BomAnalyticsServices
    ...
    """

    api_class = api.DocumentationApi

    @staticmethod
    def _run_query(api_instance: api.DocumentationApi, **kwargs: Dict) -> str:
        """Gets the yaml representation of the API from Granta MI.

        Parameters
        ----------
        api_instance
            The instance of the low-level DocumentationApi class.

        Returns
        -------
            The yaml definition of the Bom Analytics API.
        """

        result: str = api_instance.get_yaml()
        return result