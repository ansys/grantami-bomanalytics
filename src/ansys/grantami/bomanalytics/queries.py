"""BoM Analytics query builders.

Describes and implements the main interface for the Bom Analytics API. The builder objects here define
the creation, validation, and execution of queries for impacted substances and compliance. One separate
static class outside the main hierarchy implements the Yaml API endpoint.

Attributes
----------
Query_Builder
    Generic type for builder configuration methods. Ensures that the specific sub-class of the
    object to which the method is bound is hinted as the return type. For example, if ``.with_record_guid()``
    is called on a ``SpecificationCompliance`` object, the return type is correctly identified as
    ``SpecificationCompliance``.
Query_Result
    Type of the result object, which can be any type that inherits from either ``ComplianceBaseClass`` or
    ``ImpactedSubstancesBaseClass``.
"""

from abc import ABC, abstractmethod
from typing import (
    Union,
    List,
    Dict,
    Tuple,
    TypeVar,
    Callable,
    Generator,
    Optional,
    Type,
)
import warnings
from numbers import Number

from ansys.grantami.bomanalytics_openapi import models, api  # type: ignore[import]

from ._item_definitions import AbstractBomFactory, RecordDefinition, PartDefinition  # noqa: F401
from ._allowed_types import validate_argument_type
from ._query_results import (
    QueryResultFactory,
    ComplianceBaseClass,
    ImpactedSubstancesBaseClass,
)
from .indicators import _Indicator, WatchListIndicator, RoHSIndicator
from ._connection import Connection  # noqa: F401
from ._exceptions import GrantaMIException
from ._logger import logger

Query_Builder = TypeVar("Query_Builder", covariant=True, bound=Union["_BaseQueryBuilder", "_ApiMixin"])
Query_Result = TypeVar("Query_Result", covariant=True, bound=Union[ComplianceBaseClass, ImpactedSubstancesBaseClass])

EXCEPTION_MAP = {
    "critical-error": logger.critical,
    "error": logger.error,
    "warning": logger.warning,
    "information": logger.info,
}
"""Map between log severity strings returned by the Granta MI server and Python logger methods."""


class _BaseQueryDataManager(ABC):
    """Outlines an interface for managing 'items' to be provided to the query. For example, the record
    or BoM-based dimension to a query.

    This class doesn't specify how the objects are added to the ``_item_definitions`` attribute or how
    they are converted to attributes.
    """

    _item_definitions: list
    """List of BoM items to pass to the low-level API. """

    _item_results: list
    """List of results to be returned by the low-level API."""

    def __init__(self) -> None:
        self._messages: List[models.CommonLogEntry] = []

    @property
    def populated_inputs(self) -> bool:
        """Whether this ArgumentManager is populated. For example, can a query be performed on the items in this object.

        Returns
        -------
            Boolean cast of the ``_item_definitions`` attribute.
        """

        return bool(self._item_definitions)

    def initialize_results(self) -> None:
        """Reset the result properties of the object."""

        self._item_results = []
        self._messages = []

    @property
    def item_results(self) -> List[models.ModelBase]:
        """List of result items returned by the low-level API for the items in ``_item_definitions``.

        Returns
        -------
            Results of the query.
        """
        return self._item_results

    def append_response(self, response: models.ModelBase) -> None:
        """Append a response from the low-level API to this object.

        This method extracts the results and server messages from the response object and appends
        them to the respective lists.

        Parameters
        ----------
        response
           Response returned by the low-level API.
        """

        self._emit_log_messages(response.log_messages)
        self._messages.extend(response.log_messages)
        results = self._extract_results_from_response(response)
        self._item_results.extend(results)

    @staticmethod
    def _emit_log_messages(log_messages: List[models.CommonLogEntry]) -> None:
        """Emit log entries for all messages using the appropriate method based on their severity. Raise an exception
        for any critical errors.

        Parameters
        ----------
        log_messages : list
            Messages returned by the server when executing the query.

        Raises
        ------
        GrantaMIException
            A message with severity ``critical`` was returned by the server.
        """

        exception_messages = []
        for log_msg in log_messages:
            log_method = EXCEPTION_MAP.get(log_msg.severity, logger.warning)
            log_method(log_msg.message)
            if log_method == logger.critical:
                exception_messages.append(log_msg.message)
        if exception_messages:
            error_text = "\n".join(exception_messages)
            raise GrantaMIException(error_text)

    @abstractmethod
    def _extract_results_from_response(self, response: models.ModelBase) -> List[models.ModelBase]:
        pass

    @property
    def messages(self) -> List[models.CommonLogEntry]:
        """Messages returned by the server when processing all items in ``_item_definitions``"""
        return self._messages


class _RecordQueryDataManager(_BaseQueryDataManager):
    """Stores records for use in queries and generates the list of models to send to the server.

    Parameters
    ----------
    item_type_name : str, optional
        Name of the items as defined by the low-level API. For example, ``materials`` or ``parts``.
    batch_size : int
        Number of items to include in a single request.
    """

    def __init__(self, item_type_name: str = "", batch_size: Optional[int] = None) -> None:
        super().__init__()
        self._item_definitions = []
        self._item_results = []

        self.item_type_name = item_type_name
        """ Name of the item collection as defined by the low-level API. For example, ``materials`` or ``parts``. """

        self.batch_size: Optional[int] = batch_size

    def __str__(self) -> str:
        if not self.item_type_name:
            return "Uninitialized"
        else:
            return f"{len(self._item_definitions)} {self.item_type_name}, batch size = {self.batch_size}"

    def __repr__(self) -> str:
        if not self.item_type_name:
            item_text = "record_type_name: None"
        else:
            item_text = f'record_type_name: "{self.item_type_name}"'
        if not self.batch_size:
            batch_text = "batch_size: None"
        else:
            batch_text = f"batch_size: {self.batch_size}"
        return f"<{self.__class__.__name__} {{{item_text}, {batch_text}}}, length = {len(self._item_definitions)}>"

    def append_record_definition(self, item: RecordDefinition) -> None:
        """Append a specific record definition to the argument manager.

        Parameters
        ----------
        item
            Definition to add to this list of record definitions.

        Examples
        --------
        >>> part_definition = PartDefinition(...)
        >>> items = _RecordQueryDataManager(item_type_name = "parts", batch_size = 100)
        >>> items.append_record_definition(part_definition)
        """
        if not all(item.record_reference.values()):
            raise TypeError(
                "Attempted to add a RecordDefinition-derived object with a null record reference to a"
                " query. This is not supported; RecordDefinition-derived objects without record references"
                " can only be used as result objects for BoM queries."
            )
        self._item_definitions.append(item)

    @property
    def batched_arguments(self) -> Generator[Dict[str, List[Union[models.ModelBase, str]]], None, None]:
        """A generator that produces lists of instances of models to be supplied to a query request. Each list
        of dictionaries will have at most ``_batch_size`` long.

        Each individual dictionary can be passed to the request constructor as a kwarg.

        Yields
        ------
            Batched **kwargs.

        Raises
        ------
        RuntimeError
            If the ``item_type_name`` has not been set before the arguments are generated.

        Examples
        --------
        >>> items = _RecordQueryDataManager(item_type_name = "materials", batch_size = 100)
        >>> items.batched_arguments
        {"materials": [{"reference_type": "material_id", "reference_value": "ABS"}, ...]  # Up to 100 items
        """

        if not self.item_type_name:
            raise RuntimeError('"item_type_name" must be populated before record arguments can be generated.')
        if self.batch_size is None:
            raise RuntimeError('"batch_size" must be populated before record arguments can be generated.')

        for batch_number, i in enumerate(range(0, len(self._item_definitions), self.batch_size)):
            batch = [i._definition for i in self._item_definitions][i : i + self.batch_size]  # noqa: E203 E501
            batch_str = ", ".join([f'"{item.reference_type}": "{item.reference_value}"' for item in batch])
            logger.debug(f"Batch {batch_number + 1}, Items: {batch_str}")
            yield {self.item_type_name: batch}

    def _extract_results_from_response(self, response: models.ModelBase) -> List[models.ModelBase]:
        """Extract the individual results from a response object.

        Returns
        -------
            Attribute containing the list of results identified by ``self.record_type_name``.
        """

        results: List[models.ModelBase] = getattr(response, self.item_type_name)
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

        if not self._data.populated_inputs:  # type: ignore[attr-defined]
            warnings.warn(
                f"No {self._data.item_type_name} have been added to the "  # type: ignore[attr-defined]
                "query. Server response will be empty.",
                RuntimeWarning,
            )


class _RecordBasedQueryBuilder(_BaseQueryBuilder, ABC):
    """Provides all record-based query types.

    The properties and methods for this base class primarily represent generic record identifiers. The method
    ``.with_batch_size()`` is implemented here because record-based queries are the only queries that can
    operate on multiple items.
    """

    def __init__(self) -> None:
        self._data = _RecordQueryDataManager()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._data}>"

    @validate_argument_type(int)
    def with_batch_size(self: Query_Builder, batch_size: int) -> Query_Builder:
        """Set the number of records to include in a single request for this query.

        Default values are set based on typical usage of the Restricted Substances database. This value can be changed
        to optimize performance on a query-by-query basis if required. For example, you can change it if certain
        records contain particularly large or small numbers of associated records.

        Parameters
        ----------
        batch_size : int
            Number of records to include in a single request to Granta MI.

        Returns
        -------
        Query
           Current query object.

        Raises
        ------
        ValueError
            If the batch size is set to a number less than 1.
        TypeError
            If a value of any type other than :class:`int` is specified.

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
            raise ValueError("Batch size must be a positive integer")
        self._data.batch_size = batch_size
        return self

    @validate_argument_type([int], {int})
    def with_record_history_ids(self: Query_Builder, record_history_identities: List[int]) -> Query_Builder:
        """Add a list or set of record history identities to a query.

        Parameters
        ----------
        record_history_identities : list[int] | set[int]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> MaterialComplianceQuery().with_record_history_ids([15321, 17542, 942])
        <MaterialCompliance: 3 materials, batch size = 50, 0 indicators>
        """

        for value in record_history_identities:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=value
            )
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([str], {str})
    def with_record_history_guids(self: Query_Builder, record_history_guids: List[str]) -> Query_Builder:
        """Add a list or set of record history GUIDs to a query.

        Parameters
        ----------
        record_history_guids : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([str], {str})
    def with_record_guids(self: Query_Builder, record_guids: List[str]) -> Query_Builder:
        """Add a list or set of record GUIDs to a query.

        Parameters
        ----------
        record_guids : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query = query.with_record_guids(['bdb0b880-e6ee-4f1a-bebd-af76959ae3c8',
        >>>                                  'a98cf4b3-f96a-4714-9f79-afe443982c69'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for value in record_guids:
            item_reference = self._definition_factory.create_definition_by_record_guid(record_guid=value)
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([{str: str}])
    def with_stk_records(self: Query_Builder, stk_records: List[Dict[str, str]]) -> Query_Builder:
        """Add a list of records generated by the Granta MI Scripting Toolkit for Python.

        This should only be used with the corresponding method in the MI Scripting Toolkit that generates a
        :class:`dict` of the appropriate shape. This method will be introduced in the next version of the MI Scripting
        Toolkit.

        If the MI Scripting Toolkit method is not available, we recommend using the :meth:`with_record_history_ids`
        method instead.

        Parameters
        ----------
        stk_records : list[dict[str, str]]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Notes
        -----
        Common scenarios in performing compliance would be to get the compliance status of all records with a certain
        attribute value or all records created in a certain period of time. These types of complex browsing and
        searching operations are provided by the MI Scripting Toolkit. A Python script would first use the MI Scripting
        Toolkit to find the records of interest and would then pass those record references into the BoM Analytics
        package.

        This method is intended to streamline the communication between the Granta MI Scripting Toolkit and BoM
        Analytics packages.

        Examples
        --------
        >>> MaterialComplianceQuery().with_stk_records(stk_records)
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        record_guids: List[str] = [r["record_guid"] for r in stk_records]
        query_builder: Query_Builder = self.with_record_guids(record_guids)
        return query_builder


class _ApiMixin:
    """Provides API-specific mixins.

    This base class describes generic properties of a call to an API. such as calling the API and processing results.
    It also defines abstract concepts related to the parameter dimension of a query, including validation.
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type: Type[models.ModelBase]
        """Type of object to send to the Granta MI server. The actual value is set in the concrete class
         definition."""

    def _call_api(self, api_method: Callable[[models.ModelBase], models.ModelBase], arguments: Dict) -> None:
        """Perform the actual call against the Granta MI database.

        This method finalizes the arguments by appending each batch of `'item'` arguments to the passed in
        dictionary and uses them to instantiate the request object. It passes the request object to the
        low-level API and returns the response as a list.

        Parameters
        ----------
        api_method
            Method bound to the ``api.ComplianceApi`` or ``api.ImpactedSubstanceApi`` instance.
        arguments
            State of the query as a set of low-level API kwargs. Arguments include everything except the batched items.
        """

        self._validate_parameters()
        self._validate_items()  # type: ignore[attr-defined]
        self._data.initialize_results()  # type: ignore[attr-defined]
        for batch in self._data.batched_arguments:  # type: ignore[attr-defined]
            args = {**arguments, **batch}
            request = self._request_type(**args)
            response = api_method(request)
            self._data.append_response(response)  # type: ignore[attr-defined]

    @abstractmethod
    def _run_query(
        self,
        api_instance: Union[api.ComplianceApi, api.ImpactedSubstancesApi],
        static_arguments: Dict,
    ) -> Query_Result:
        pass

    @abstractmethod
    def _validate_parameters(self) -> None:
        pass


class _ComplianceMixin(_ApiMixin, ABC):
    """Implements the compliance aspects of a query.

    This class adds indicator parameters to the query, generates the indicator-specific argument to send to Granta
    MI, and creates the compliance result objects.
    """

    def __init__(self) -> None:
        super().__init__()
        self._indicators: Dict[str, _Indicator] = {}
        """Indicators added to the query."""

        self._api_method: str = ""
        """Name of the method in the `api` class. Specified in the concrete class. Retrieved dynamically because the
        `api` instance doesn't exist until runtime."""

        self.api_class: Type[api.ComplianceApi] = api.ComplianceApi
        """Class in the low-level API for this query type. Requires instantiation with the client object, and so
        only the reference to the class is stored here, not the instance itself."""

    def __repr__(self) -> str:
        result = (
            f"<{self.__class__.__name__}: {self._data},"  # type: ignore[attr-defined]
            f" {len(self._indicators)} indicators>"
        )
        return result

    @validate_argument_type([_Indicator], {_Indicator})
    def with_indicators(
        self: Query_Builder, indicators: List[Union[WatchListIndicator, RoHSIndicator]]
    ) -> Query_Builder:
        """Add a list or set of :class:`~ansys.grantami.bomanalytics.indicators.WatchListIndicator` or
        :class:`~ansys.grantami.bomanalytics.indicators.RoHSIndicator` objects to evaluate compliance against.

        Parameters
        ----------
        indicators : list[|WatchListIndicator| | |RoHSIndicator|]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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

        This method should not be used by an end-user. The ``BomAnalyticsClient.run()`` method should
        be used instead.

        Parameters
        ----------
        api_instance
            Instance of the low-level ``ComplianceApi`` class.
        static_arguments
            Arguments set at the connection level, including the database key and any custom table names.

        Returns
        -------
            Result, with the type depending on the query.

        Notes
        -----
        This method gets the bound method for this particular query from ``api_instance`` and passes
        it to ``self._call_api()``, which performs the actual call. It then passes the result to ``QueryResultFactory``
        to build the corresponding result object.

        The ``indicator_definitions`` are used to create the ``QueryResult`` object because the low-level API returns
        only the indicator names and results.
        """

        api_method = getattr(api_instance, self._api_method)
        arguments = {
            **static_arguments,
            "indicators": [i._definition for i in self._indicators.values()],
        }

        indicators_text = ", ".join(self._indicators)
        logger.debug(f"Indicators: {indicators_text}")

        self._call_api(api_method, arguments)
        result: Query_Result = QueryResultFactory.create_result(
            results=self._data.item_results,  # type: ignore[attr-defined]
            messages=self._data.messages,  # type: ignore[attr-defined]
            indicator_definitions=self._indicators,
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

    This class adds legislation parameters to the query, generates the legislation-specific argument to send to
    Granta MI, and creates the impacted substance result objects.
    """

    def __init__(self) -> None:
        super().__init__()
        self._legislations: List[str] = []
        """Legislation names added to the query."""

        self._api_method: str = ""
        """Name of the method in the ``api`` class. Specified in the concrete class. Retrieved dynamically because the
        `api` instance doesn't exist until runtime."""

        self.api_class: Type[api.ImpactedSubstancesApi] = api.ImpactedSubstancesApi
        """Class in the low-level API for this query type. Requires instantiation with the client object, and so
        only the reference to the class is stored here, not the instance itself."""

    def __repr__(self) -> str:
        result = (
            f"<{self.__class__.__name__}: {self._data}, "  # type: ignore[attr-defined]
            f"{len(self._legislations)} legislations>"
        )
        return result

    @validate_argument_type([str], {str})
    def with_legislations(self: Query_Builder, legislation_names: List[str]) -> Query_Builder:
        """Add a list or set of legislations to retrieve the impacted substances for. The legislation records are
        referenced by legislation name.

        Parameters
        ----------
        legislation_names : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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

        Gets the bound method for this particular query from ``api_instance`` and passes it to
        ``self._call_api()``, which performs the actual call. Passes the result to  ``QueryResultFactory``
        to build the corresponding result object.

        Parameters
        ----------
        api_instance
            Instance of the low-level ``ImpactedSubstancesApi`` class.
        static_arguments
            Arguments set at the connection level, including the database key and any custom table names.

        Returns
        -------
            Result of the query. The exact type of the result depends on the query that was run.
        """

        api_method = getattr(api_instance, self._api_method)
        arguments = {"legislation_names": self._legislations, **static_arguments}

        legislations_text = ", ".join(['"' + leg + '"' for leg in self._legislations])
        logger.debug(f"Legislation names: {legislations_text}")

        self._call_api(api_method, arguments)
        result: Query_Result = QueryResultFactory.create_result(
            results=self._data.item_results,  # type: ignore[attr-defined]
            messages=self._data.messages,  # type: ignore[attr-defined]
        )
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
        self._data.item_type_name = "materials"
        self._data.batch_size = 100

    @validate_argument_type([str], {str})
    def with_material_ids(self: Query_Builder, material_ids: List[str]) -> Query_Builder:
        """Add a list or set of materials to a material query, referenced by the material ID attribute value.

        Material IDs are valid for both ``MaterialUniverse`` and ``Materials - in house`` records.

        Parameters
        ----------
        material_ids : list[str] | set[set]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for material_id in material_ids:
            item_reference = self._definition_factory.create_definition_by_material_id(material_id=material_id)
            self._data.append_record_definition(item_reference)
        return self


class MaterialComplianceQuery(_ComplianceMixin, _MaterialQueryBuilder):
    """Evaluates compliance for Granta MI material records against a number of indicators. If the materials are
    associated with substances, these are also evaluated and returned.

    All methods used to add materials and indicators to this query return the query itself so that they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.MaterialComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
    """Gets the substances impacted by a list of legislations for Granta MI material records.

    All methods used to add materials and legislations to this query return the query itself so that they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.MaterialImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
        self._request_type = models.GetImpactedSubstancesForMaterialsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_impactedsubstances_materials"


class _PartQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are direct references to part records."""

    def __init__(self) -> None:
        super().__init__()
        self._data.item_type_name = "parts"
        self._data.batch_size = 10

    @validate_argument_type([str], {str})
    def with_part_numbers(self: Query_Builder, part_numbers: List[str]) -> Query_Builder:
        """Add a list or set of parts to a part query, referenced by part number.

        Parameters
        ----------
        part_numbers : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> query = PartComplianceQuery().with_part_numbers(['DRILL', 'FLRY34'])
        <PartCompliance: 2 parts, batch size = 10, 0 indicators>
        """

        for value in part_numbers:
            item_reference = self._definition_factory.create_definition_by_part_number(part_number=value)
            self._data.append_record_definition(item_reference)
        return self


class PartComplianceQuery(_ComplianceMixin, _PartQueryBuilder):
    """Evaluates compliance for Granta MI part records against a number of indicators. If the parts are
    associated with materials, parts, specifications, or substances, these are also evaluated and returned.

    All methods used to add parts and indicators to this query return the query itself so that they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.PartComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
    """Gets the substances impacted by a list of legislations for Granta MI part records.

    All methods used to add parts and legislations to this query return the query itself so that they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.PartImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
        self._request_type = models.GetImpactedSubstancesForPartsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_impactedsubstances_parts"


class _SpecificationQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are direct references to specification records."""

    def __init__(self) -> None:
        super().__init__()
        self._data.item_type_name = "specifications"
        self._data.batch_size = 10

    @validate_argument_type([str], {str})
    def with_specification_ids(self: Query_Builder, specification_ids: List[str]) -> Query_Builder:
        """Add a list or set of specifications to a specification query, referenced by specification ID.

        Parameters
        ----------
        specification_ids : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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
            self._data.append_record_definition(item_reference)
        return self


class SpecificationComplianceQuery(_ComplianceMixin, _SpecificationQueryBuilder):
    """Evaluates compliance for Granta MI specification records against a number of indicators. If the
    specifications are associated with specifications, materials, coatings, or substances, these are
    also evaluated and returned.

    All methods used to add specifications and indicators to this query return the query itself so that
    they can be chained together as required. Records can be added using a combination of any of the
    available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.SpecificationComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
        self._request_type = models.GetComplianceForSpecificationsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_compliance_specifications"


class SpecificationImpactedSubstancesQuery(_ImpactedSubstanceMixin, _SpecificationQueryBuilder):
    """Gets the substances impacted by a list of legislations for Granta MI specification records.

    All methods used to add specifications and legislations to this query return the query itself so that they can be
    chained together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.SpecificationImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
        self._request_type = models.GetImpactedSubstancesForSpecificationsRequest
        self._definition_factory = AbstractBomFactory.create_factory_for_request_type(self._request_type)
        self._api_method = "post_impactedsubstances_specifications"


class _SubstanceQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are direct references to substance records."""

    def __init__(self) -> None:
        super().__init__()
        self._data.item_type_name = "substances"
        self._data.batch_size = 500

    @validate_argument_type([str], {str})
    def with_cas_numbers(self: Query_Builder, cas_numbers: List[str]) -> Query_Builder:
        """Add a list or set of CAS numbers to a substance query. The amount of substance in the material
        will be set to 100%.

        Parameters
        ----------
        cas_numbers : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_cas_numbers(['50-00-0', '57-24-9'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for cas_number in cas_numbers:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([str], {str})
    def with_ec_numbers(self: Query_Builder, ec_numbers: List[str]) -> Query_Builder:
        """Add a list or set of EC numbers to a substance query. The amount of substance in the material will
        be set to 100%.

        Parameters
        ----------
        ec_numbers : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_ec_numbers(['200-001-8', '200-319-7'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for ec_number in ec_numbers:
            item_reference = self._definition_factory.create_definition_by_ec_number(ec_number=ec_number)
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([str], {str})
    def with_chemical_names(self: Query_Builder, chemical_names: List[str]) -> Query_Builder:
        """Add a list or set of chemical names to a substance query. The amount of substance in the material
        will be set to 100%.

        Parameters
        ----------
        chemical_names : list[str] | set[str]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_chemical_names(['Formaldehyde', 'Strychnine'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for chemical_name in chemical_names:
            item_reference = self._definition_factory.create_definition_by_chemical_name(chemical_name=chemical_name)
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([(int, Number)], {(int, Number)})
    def with_record_history_ids_and_amounts(
        self: Query_Builder, record_history_identities_and_amounts: List[Tuple[int, float]]
    ) -> Query_Builder:
        """Add a list or set of record history identities and amounts to a substance query. The identity and
        quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        Parameters
        ----------
        record_history_identities_and_amounts : list[tuple[int, float]] | set[tuple[int, float]]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([(str, Number)], {(str, Number)})
    def with_record_history_guids_and_amounts(
        self: Query_Builder, record_history_guids_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list or set of record history GUID and amounts to a substance query. The GUID and quantity
        pairs are expressed as a tuple, with the quantity in units of wt. %.

        Parameters
        ----------
        record_history_guids_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([(str, Number)], {(str, Number)})
    def with_record_guids_and_amounts(
        self: Query_Builder, record_guids_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list or set of record GUIDs and amounts to a substance query. The GUID and quantity pairs are
        expressed as a tuple, with the quantity in units of wt. %.

        Parameters
        ----------
        record_guids_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([(str, Number)], {(str, Number)})
    def with_cas_numbers_and_amounts(
        self: Query_Builder, cas_numbers_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list or set of CAS numbers and amounts to a substance query. The CAS numbers and quantity
        pairs are expressed as a tuple, with the quantity in units of wt. %.

        Parameters
        ----------
        cas_numbers_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_cas_numbers_and_amounts([('50-00-0', 25), ('57-24-9', 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for cas_number, amount in cas_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_cas_number(cas_number=cas_number)
            item_reference.percentage_amount = amount
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([(str, Number)], {(str, Number)})
    def with_ec_numbers_and_amounts(
        self: Query_Builder, ec_numbers_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list or set of EC numbers and amounts to a substance query. The EC numbers and quantity
        pairs are expressed as a tuple, with the quantity in units of wt. %.

        Parameters
        ----------
        ec_numbers_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type([(str, Number)], {(str, Number)})
    def with_chemical_names_and_amounts(
        self: Query_Builder, chemical_names_and_amounts: List[Tuple[str, float]]
    ) -> Query_Builder:
        """Add a list or set of chemical names and amounts to a substance query. The chemical names and
        quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        Parameters
        ----------
        chemical_names_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

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
            self._data.append_record_definition(item_reference)
        return self


class SubstanceComplianceQuery(_ComplianceMixin, _SubstanceQueryBuilder):
    """Evaluate compliance for Granta MI substance records against a number of indicators.

    All methods used to add substances and indicators to this query return the query itself so that they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.SubstanceComplianceQueryResult`.

    Notes
    -----
    The amount of a substance is a critical factor when determining if it is compliant or non-compliant with a
    legislation. For the other compliance queries in this API, the amount of substance is determined by the value set
    in the declaration stored in Granta MI. However, when performing a query for substance compliance, there is no
    declaration because the substances are being examined directly.

    As a result, a set of extra methods are defined that allow the amount of each substance to be defined along with the
    reference to the record in Granta MI. These methods have the name ``_with_xxxxxx_and_amounts()`` and take a list of
    tuples as the argument.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_names=["California Proposition 65 List"]
    ... )
    >>> query = (
    ...     SubstanceComplianceQuery()
    ...     .with_cas_numbers_and_amounts([('50-00-0', 25), ('57-24-9', 0.5)])
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


class _BomQueryDataManager(_BaseQueryDataManager):
    """Stores a BoM for use in queries and generates the kwarg to send to the server.

    Because of the base class, ``_item_definitions`` must be a list. However, this list only ever contains a
    single string because only one BoM can be sent to the server in a single query.
    """

    def __init__(self) -> None:
        super().__init__()
        self.item_type_name = "bom_xml1711"
        self._item_definitions = [""]
        self._item_results = []

    def __repr__(self) -> str:
        return f'<_BomQueryDataManager {{bom: "{self._item_definitions[0][:100]}"}}>'

    @property
    def bom(self) -> str:
        """BoM to use for the query. Because only one BoM is used per query, this property
        enforces storing only one BoM per instance of ``_BomQueryDataManager``.

        Returns
        -------
        bom : str
            BoM to use for the query.
        """
        bom: str = self._item_definitions[0]
        return bom

    @bom.setter
    def bom(self, value: str) -> None:
        self._item_definitions = [value]

    @property
    def batched_arguments(self) -> List[Dict[str, str]]:
        """Dictionary with a key that passes the BoM as a kwarg to the request constructor.

        Returns
        -------
            BoM with the appropriate keyword argument.

        Examples
        --------
        >>> bom_item = _BomQueryDataManager(bom = "<PartsEco xmlns...")
        >>> bom_item.batched_arguments
        {"bom_xml1711": "<PartsEco xmlns..."}
        """

        return [{self.item_type_name: self._item_definitions[0]}]

    def _extract_results_from_response(self, response: models.ModelBase) -> List[models.ModelBase]:
        """Extracts the individual results from a response object.

        For BoM queries, the result isn't contained within a larger response object. It is already the object we want.

        Returns
        -------
            Response wrapped in a list.
        """
        return [response]


class _Bom1711QueryBuilder(_BaseQueryBuilder, ABC):
    """Sub-class for all queries where the items added to the query are Boms."""

    def __init__(self) -> None:
        self._data = _BomQueryDataManager()

    @validate_argument_type(str)
    def with_bom(self: Query_Builder, bom: str) -> Query_Builder:
        """Set the BoM to use for the query.

        The BoM must be in the Ansys Granta 1711 XML BoM format.

        Parameters
        ----------
        bom : str
            BoM to use for the query.

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            If the method is called with values that do not match the types described above.

        Notes
        -----
        The XML schema is defined by the schema document
        :download:`BillOfMaterialsEco.xsd </_static/xml_schemas/BillOfMaterialsEco.xsd>`, which in turn references
        :download:`grantarecord1205.xsd</_static/xml_schemas/grantarecord1205.xsd>`. Together, these XSD files can be
        used to validate that the BoM is both valid XML and adheres to the Ansys Granta 1711 XML BoM schema.

        Examples
        --------
        >>> my_bom = "<PartsEco xmlns..."
        >>> query = BomComplianceQuery().with_bom(my_bom)
        """

        self._data.bom = bom
        return self


class BomComplianceQuery(_ComplianceMixin, _Bom1711QueryBuilder):
    """Evaluates compliance for a BoM in the Ansys Granta 1711 XML BoM format against a number of
    indicators.

    All BoM-based queries only operate on a single BoM. As a result, the ``.with_batch_size()`` method is not
    implemented for BoM-based queries.

    The methods used to add the BoM and Indicators to this query return the query itself so that they can be
    chained together as required.

    Once the query is fully constructed, use the `cxn.`
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.PartComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
    """Gets the substances impacted by a list of legislations for a BoM in the Ansys Granta
    1711 XML BoM format.

    All BoM-based queries only operate on a single BoM. As a result, the ``.with_batch_size()`` method is not
    implemented for BoM-based queries.

    Once the query is fully constructed, use the `cxn.`
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
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
        self._request_type = models.GetImpactedSubstancesForBom1711Request
        self._api_method = "post_impactedsubstances_bom1711"


class Yaml:
    """Gets the yaml description of the underlying REST API.

    Because the API is fully implemented in this package, the description is unlikely to be
    useful to end users. It is provided for completeness only.

    This class only contains static methods and class attributes so that it can be used without instantiation.

    Examples
    --------
    >>> cxn = Connection("http://localhost/mi_servicelayer").with_autologon().connect()
    >>> cxn.run(Yaml)
    openapi: 3.0.1
    info:
      title: Granta.BomAnalyticsServices
    ...
    """

    api_class = api.DocumentationApi

    @staticmethod
    def _run_query(api_instance: api.DocumentationApi, **kwargs: Dict) -> str:
        """Get the yaml representation of the API from Granta MI.

        Parameters
        ----------
        api_instance : api.DocumentationApi
            Instance of the low-level ``DocumentationApi`` class.

        Returns
        -------
        yaml : str
            Yaml definition of the BoM Analytics API.
        """

        result: str = api_instance.get_yaml()
        return result
