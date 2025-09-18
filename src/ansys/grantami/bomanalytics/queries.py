# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""BoM Analytics query builders.

Describes and implements the main interface for the Bom Analytics API. The builder objects define
the creation, validation, and execution of queries for impacted substances and compliance. One separate
static class outside the main hierarchy implements the YAML API endpoint.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from numbers import Number
from types import NoneType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
import warnings

from ansys.grantami.bomanalytics_openapi.v2 import api, models
from defusedxml import ElementTree

from ._allowed_types import validate_argument_type
from ._exceptions import GrantaMIException
from ._item_definitions import (
    BomItemDefinitionFactory,
    MaterialDefinitionFactory,
    PartDefinitionFactory,
    RecordDefinition,
    SpecificationDefinitionFactory,
    SubstanceComplianceDefinitionFactory,
)
from ._logger import logger
from ._query_results import QueryResultFactory, ResultBaseClass
from ._typing import _raise_if_empty
from .indicators import RoHSIndicator, WatchListIndicator, _Indicator

if TYPE_CHECKING:
    from ._connection import Connection  # noqa: F401


_ImpactedSubstanceQuery = TypeVar("_ImpactedSubstanceQuery", bound="_ImpactedSubstanceMixin")
_ComplianceQuery = TypeVar("_ComplianceQuery", bound="_ComplianceMixin")
_SustainabilityQuery = TypeVar("_SustainabilityQuery", bound="_SustainabilityMixin")

_RecordQuery = TypeVar("_RecordQuery", bound="_RecordBasedQueryBuilder")
_MaterialQuery = TypeVar("_MaterialQuery", bound="_MaterialQueryBuilder")
_PartQuery = TypeVar("_PartQuery", bound="_PartQueryBuilder")
_SpecificationQuery = TypeVar("_SpecificationQuery", bound="_SpecificationQueryBuilder")
_SubstanceQuery = TypeVar("_SubstanceQuery", bound="_SubstanceQueryBuilder")

_BomQuery = TypeVar("_BomQuery", bound="_BomQueryBuilder")

_Responses = Union[
    models.GetImpactedSubstancesForMaterialsResponse,
    models.GetImpactedSubstancesForSpecificationsResponse,
    models.GetImpactedSubstancesForPartsResponse,
    models.GetImpactedSubstancesForBomResponse,
    models.GetComplianceForSubstancesResponse,
    models.GetComplianceForMaterialsResponse,
    models.GetComplianceForSpecificationsResponse,
    models.GetComplianceForPartsResponse,
    models.GetComplianceForBomResponse,
    models.GetAvailableLicensesResponse,
    models.GetSustainabilityForBomResponse,
    models.GetSustainabilitySummaryForBomResponse,
]

EXCEPTION_MAP = {
    "critical-error": logger.critical,
    "error": logger.error,
    "warning": logger.warning,
    "information": logger.info,
}
"""Map between log severity strings returned by the Granta MI server and Python logger methods."""


class _BaseQuery(ABC):
    """Interface expected by the client."""

    api_class: Type[api.ApiBase]

    @abstractmethod
    def _run_query(self, api_instance: api.ApiBase, static_arguments: Dict) -> ResultBaseClass:
        raise NotImplementedError


class _BaseQueryDataManager(ABC):
    """Outlines an interface for managing *items* to provide to the query.

    For example, the items to provide to the query might be the records or BoM-based dimensions.

    This class doesn't specify how the objects are added to the ``_item_definitions`` attribute or how
    they are converted to attributes.
    """

    _item_definitions: list
    """List of BoM items to pass to the low-level API. """

    _item_results: list
    """List of results to be returned by the low-level API."""

    item_type_name: str
    """Name of the argument managed by this class and expected by the request object."""

    def __init__(self) -> None:
        self._messages: List[models.CommonLogEntry] = []

    @property
    def populated_inputs(self) -> bool:
        """Whether the argument manager is populated. For example, this property
        determines whether to perform a query on the items in the object.

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

    def append_response(self, response: _Responses) -> None:
        """Append a response from the low-level API to the object.

        This method extracts the results and server messages from the response object and appends
        them to the respective lists.

        Parameters
        ----------
        response
           Response returned by the low-level API.
        """

        messages = _raise_if_empty(response.log_messages)
        self._emit_log_messages(messages)
        self._messages.extend(messages)
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
            Error to raise when a severity of ``"critical"`` is returned by the server.
        """

        exception_messages = []
        for log_msg in log_messages:
            severity = _raise_if_empty(log_msg.severity)
            log_method = EXCEPTION_MAP.get(severity, logger.warning)
            log_method(log_msg.message)
            if log_method == logger.critical:
                message = _raise_if_empty(log_msg.message)
                exception_messages.append(message)
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

    @property
    @abstractmethod
    def batched_arguments(self) -> Any:
        raise NotImplementedError


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

        self.item_type_name: str = item_type_name
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
        """Append a record definition to the argument manager.

        Parameters
        ----------
        item
            Record definition to add to the list of record definitions.

        Examples
        --------
        >>> part_definition = PartDefinition(...)
        >>> items = _RecordQueryDataManager(item_type_name = "parts", batch_size = 100)
        >>> items.append_record_definition(part_definition)
        """
        if not all(item._record_reference.values()):
            raise TypeError(
                "Attempted to add a RecordDefinition-derived object with a null record reference to a"
                " query. This is not supported; RecordDefinition-derived objects without record references"
                " can only be used as result objects for BoM queries."
            )
        self._item_definitions.append(item)

    @property
    def batched_arguments(
        self,
    ) -> Generator[Dict[str, List[Union[models.ModelBase, str]]], None, None]:
        """Generator that produces lists of instances of models to be supplied to a query request. Each list
        of dictionaries is at most ``_batch_size`` long.

        Each individual dictionary can be passed to the request constructor as a kwarg.

        Yields
        ------
            Batched **kwargs.

        Raises
        ------
        RuntimeError
            Error to raise if ``item_type_name`` has not been set before the arguments are generated.

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
    """Provides the base class for all queries."""

    _data: "_BaseQueryDataManager"

    def _validate_items(self) -> None:
        """Perform pre-flight checks on the items that have been added to the query.

        Raises
        ------
        ValueError
            Error to raise if no items have been added to the query.
        """

        if not self._data.populated_inputs:
            raise ValueError(f"No {self._data.item_type_name} have been added to the query.")


class _RecordBasedQueryBuilder(_BaseQueryBuilder, ABC):
    """Provides all record-based query types.

    The properties and methods for this base class primarily represent generic record identifiers. The method
    ``.with_batch_size()`` is implemented here because record-based queries are the only queries that can
    operate on multiple items.
    """

    _definition_factory: BomItemDefinitionFactory

    def __init__(self) -> None:
        self._data: "_RecordQueryDataManager" = _RecordQueryDataManager()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._data}>"

    @validate_argument_type("batch_size", int)
    def with_batch_size(self: _RecordQuery, batch_size: int) -> _RecordQuery:
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
            Error to raise if the batch size is set to a number less than 1.
        TypeError
            Error to raise if a value of any type other than :class:`int` is specified.

        Notes
        -----
        The Restricted Substances database makes extensive use of tabular data and associated records to store the
        complex hierarchical relationships that define compliance of products, assemblies, parts, specifications,
        and materials. As a result, it is impossible to determine the complexity of a particular query without knowing
        precisely how many records are related to the record included in the query.

        The default batch sizes are set for each record type and represent appropriate numbers of those records to be
        included in the same request assuming typical numbers of associated records.

        Even if the records are queried in multiple batches, the results are assembled into a single result object.

        Examples
        --------
        >>> MaterialComplianceQuery().with_batch_size(50)
        <MaterialCompliance: 0 materials, batch size = 50, 0 indicators>
        """

        if batch_size < 1:
            raise ValueError("Batch size must be a positive integer")
        self._data.batch_size = batch_size
        return self

    @validate_argument_type("record_history_identities", [int], {int})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_record_history_ids(
        self: _RecordQuery,
        record_history_identities: List[int],
        external_database_key: Optional[str] = None,
    ) -> _RecordQuery:
        """
        Add a list or set of record history identities to a query.

        If the records referenced by values in the ``record_history_identities`` argument are stored in an external
        database, you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        record_history_identities : list[int] | set[int]
           List or set of record history identities.
        external_database_key : str, optional
            Required if records referenced by the ``record_history_identities`` argument are stored in an external
            database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described
            earlier.

        Examples
        --------
        >>> MaterialComplianceQuery().with_record_history_ids([15321, 17542, 942])
        <MaterialCompliance: 3 materials, batch size = 50, 0 indicators>
        """

        for value in record_history_identities:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=value,
                database_key=external_database_key,
            )
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("record_history_guids", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_record_history_guids(
        self: _RecordQuery,
        record_history_guids: List[str],
        external_database_key: Optional[str] = None,
    ) -> _RecordQuery:
        """
        Add a list or set of record history GUIDs to a query.

        If the records referenced by values in the ``record_history_guids`` argument are stored in an external database,
        you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        record_history_guids : list[str] | set[str]
            List or set of record history GUIDs.
        external_database_key : str, optional
            Required if records referenced by the ``record_history_guids`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.with_record_history_guids(['41e20a88-d496-4735-a177-6266fac9b4e2',
        >>>                                  'd117d9ad-e6a9-4ba9-8ad8-9a20b6d0b5e2'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for value in record_history_guids:
            item_reference = self._definition_factory.create_definition_by_record_history_guid(
                record_history_guid=value,
                database_key=external_database_key,
            )
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("record_guids", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_record_guids(
        self: _RecordQuery,
        record_guids: List[str],
        external_database_key: Optional[str] = None,
    ) -> _RecordQuery:
        """
        Add a list or set of record GUIDs to a query.

        If the records referenced by values in the ``record_guids`` argument are stored in an external database, you
        must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        record_guids : list[str] | set[str]
            List or set of record GUIDs.
        external_database_key : str, optional
            Required if records referenced by the ``record_guids`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query = query.with_record_guids(['bdb0b880-e6ee-4f1a-bebd-af76959ae3c8',
        >>>                                  'a98cf4b3-f96a-4714-9f79-afe443982c69'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for value in record_guids:
            item_reference = self._definition_factory.create_definition_by_record_guid(
                record_guid=value,
                database_key=external_database_key,
            )
            self._data.append_record_definition(item_reference)
        return self


class _ApiMixin(_BaseQueryBuilder, _BaseQuery, ABC):
    """Provides API-specific mixins.

    This base class describes generic properties of a call to an API, such as calling the API and processing results.
    It also defines abstract concepts related to the parameter dimension of a query, including validation.
    """

    _request_type: Type[models.ModelBase]
    """Type of object to send to the Granta MI server. The actual value is set in the concrete class
    definition."""

    def __init__(self) -> None:
        super().__init__()

    def _call_api(self, api_method: Callable[..., _Responses], arguments: Dict) -> None:
        """Perform the actual call against the Granta MI database.

        This method finalizes the arguments by appending each batch of ``'item'`` arguments to the passed-in
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
        self._validate_items()
        self._data.initialize_results()
        for batch in self._data.batched_arguments:
            args = {**arguments, **batch}
            request = self._request_type(**args)
            response = api_method(body=request)
            self._data.append_response(response)

    @abstractmethod
    def _run_query(
        self,
        api_instance: Union[  # type: ignore[override]
            api.ComplianceApi,
            api.ImpactedSubstancesApi,
            api.SustainabilityApi,
        ],
        static_arguments: Dict,
    ) -> ResultBaseClass:
        """
        Abstract method. Inherited classes must pass the current state of the query as arguments to _call_api and
        handle the response.

        This method should not be used by an end user. The ``BomAnalyticsClient.run()`` method should
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
        This method gets the bound method for this particular query from the ``api_instance`` parameter and passes
        it to the ``self._call_api()`` method, which performs the actual call. It then passes the result to
        the ``QueryResultFactory`` class to build the corresponding result object.
        """

    @abstractmethod
    def _validate_parameters(self) -> None:
        pass


class _ComplianceMixin(_ApiMixin, ABC):
    """Implements the compliance aspects of a query.

    This class adds indicator parameters to the query, generates the indicator-specific argument to send to Granta
    MI, and creates the compliance result objects.
    """

    _api_method: str
    """Name of the method in the ``api`` class. The name is specified in the concrete class and
    retrieved dynamically because the ``api`` instance doesn't exist until runtime."""

    def __init__(self) -> None:
        super().__init__()
        self._indicators: Dict[str, _Indicator] = {}
        """Indicators added to the query."""

        self.api_class: Type[api.ComplianceApi] = api.ComplianceApi
        """Class in the low-level API for this query type. This class requires instantiation with the client object,
        and so only the reference to the class is stored here, not the instance itself."""

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {self._data}," f" {len(self._indicators)} indicators>"
        return result

    @validate_argument_type("indicators", [_Indicator], {_Indicator})
    def with_indicators(
        self: _ComplianceQuery, indicators: List[Union[WatchListIndicator, RoHSIndicator]]
    ) -> _ComplianceQuery:
        """Add a list or set of :class:`~ansys.grantami.bomanalytics.indicators.WatchListIndicator` or
        :class:`~ansys.grantami.bomanalytics.indicators.RoHSIndicator` objects to evaluate compliance against.

        Parameters
        ----------
        indicators : list[|WatchListIndicator| | |RoHSIndicator|]
            List of indicators.

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described above.

        Examples
        --------
        >>> indicator = WatchListIndicator(
        ...     name="Prop 65",
        ...     legislation_ids=["Prop65"]
        ... )
        >>> MaterialComplianceQuery().with_indicators([indicator])
        <MaterialCompliance: 0 materials, batch size = 100, 1 indicators>
        """

        for value in indicators:
            self._indicators[value.name] = value
        return self

    def _run_query(
        self,
        api_instance: api.ComplianceApi,  # type: ignore[override]
        static_arguments: Dict,
    ) -> ResultBaseClass:
        """Passes the current state of the query as arguments to Granta MI and returns the results.

        This method should not be used by an end user. The ``BomAnalyticsClient.run()`` method should
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
        This method gets the bound method for this particular query from the ``api_instance`` parameter and passes
        it to the ``self._call_api()`` method, which performs the actual call. It then passes the result to
        the ``QueryResultFactory`` class to build the corresponding result object.

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
        result: ResultBaseClass = QueryResultFactory.create_result(
            results=self._data.item_results,
            messages=self._data.messages,
            indicator_definitions=self._indicators,
        )
        return result

    def _validate_parameters(self) -> None:
        """Perform pre-flight checks on the indicators that have been added to the query.

        Warns
        -----
        RuntimeWarning
            Error to raise if no indicators have been added to the query. The error warns
            that the response will be empty.
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

    _api_method: str
    """Name of the method in the ``api`` class. The name is specified in the concrete class and
    retrieved dynamically because the `api` instance doesn't exist until runtime."""

    def __init__(self) -> None:
        super().__init__()
        self._legislations: List[str] = []
        """Legislation ids added to the query."""

        self.api_class: Type[api.ImpactedSubstancesApi] = api.ImpactedSubstancesApi
        """Class in the low-level API for this query type. This class requires instantiation with the client object,
        and so only the reference to the class is stored here, not the instance itself."""

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {self._data}, " f"{len(self._legislations)} legislations>"
        return result

    @validate_argument_type("legislation_ids", [str], {str})
    def with_legislation_ids(self: _ImpactedSubstanceQuery, legislation_ids: List[str]) -> _ImpactedSubstanceQuery:
        """Add a list or set of legislations to retrieve the impacted substances for.

        Legislations are identified based on their ``Legislation ID`` attribute value.

        Parameters
        ----------
        legislation_ids : list[str] | set[str]
            List or set of legislation ids.

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.
        """

        self._legislations.extend(legislation_ids)
        return self

    def _run_query(
        self,
        api_instance: api.ImpactedSubstancesApi,  # type: ignore[override]
        static_arguments: Dict,
    ) -> ResultBaseClass:
        """Passes the current state of the query as arguments to Granta MI and returns the results.

        Gets the bound method for this particular query from the ``api_instance`` parameter and passes it to the
        ``self._call_api()`` method, which performs the actual call. It then passes the result to the
        ``QueryResultFactory`` class to build the corresponding result object.

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
        arguments = {"legislation_ids": self._legislations, **static_arguments}

        legislations_text = ", ".join(['"' + leg + '"' for leg in self._legislations])
        logger.debug(f"Legislation ids: {legislations_text}")

        self._call_api(api_method, arguments)
        result: ResultBaseClass = QueryResultFactory.create_result(
            results=self._data.item_results,
            messages=self._data.messages,
        )
        return result

    def _validate_parameters(self) -> None:
        """Perform pre-flight checks on the legislations that have been added to the query.

        Warns
        -----
        RuntimeWarning
            Error to raise if no legislations have been added to the query. The error warns that
            the response will be empty.
        """

        if not self._legislations:
            warnings.warn(
                "No legislations have been added to the query. Server response will be empty.",
                RuntimeWarning,
            )


class _MaterialQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Provides the subclass for all queries where the items added to the query are direct references to material
    records."""

    _definition_factory = MaterialDefinitionFactory()

    def __init__(self) -> None:
        super().__init__()
        self._data.item_type_name = "materials"
        self._data.batch_size = 100

    @validate_argument_type("material_ids", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_material_ids(
        self: _MaterialQuery, material_ids: List[str], external_database_key: Optional[str] = None
    ) -> _MaterialQuery:
        """
        Add a list or set of materials to a material query, referenced by the material ID attribute value.

        Material IDs are valid for both ``MaterialUniverse`` and ``Materials - in house`` records.

        If the records referenced by values in the ``material_ids`` argument are stored in an external database, you
        must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        material_ids : list[str] | set[set]
            List or set of material IDs.
        external_database_key : str, optional
            Required if records referenced by the ``material_ids`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = MaterialComplianceQuery()
        >>> query.with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
        <MaterialCompliance: 2 materials, batch size = 100, 0 indicators>
        """

        for material_id in material_ids:
            item_reference = self._definition_factory.create_definition_by_material_id(
                material_id=material_id,
                database_key=external_database_key,
            )
            self._data.append_record_definition(item_reference)
        return self


class MaterialComplianceQuery(_ComplianceMixin, _MaterialQueryBuilder):
    """Evaluates compliance for Granta MI material records against a number of indicators.

    If the materials are associated with substances, these are also evaluated and returned.

    All methods used to add materials and indicators to this query return the query itself so that they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.MaterialComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_ids=["Prop65"]
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
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> query = (
    ...     MaterialImpactedSubstancesQuery()
    ...     .with_material_ids(['elastomer-butadienerubber', 'NBR-100'])
    ...     .with_legislation_ids(["Candidate_AnnexXV"])
    ... )
    >>> cxn.run(query)
    <MaterialImpactedSubstancesQueryResult: 2 MaterialWithImpactedSubstances results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = models.GetImpactedSubstancesForMaterialsRequest
        self._api_method = "post_impactedsubstances_materials"


class _PartQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Provides the subclass for all queries where the items added to the query are direct references to part
    records."""

    _definition_factory = PartDefinitionFactory()

    def __init__(self) -> None:
        super().__init__()
        self._data.item_type_name = "parts"
        self._data.batch_size = 10

    @validate_argument_type("part_numbers", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_part_numbers(
        self: _PartQuery, part_numbers: List[str], external_database_key: Optional[str] = None
    ) -> _PartQuery:
        """
        Add a list or set of parts to a part query, referenced by part number.

        If the records referenced by values in the ``part_numbers`` argument are stored in an external database, you
        must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        part_numbers : list[str] | set[str]
            List or set of part numbers.
        external_database_key : str, optional
            Required if records referenced by the ``part_numbers`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = PartComplianceQuery().with_part_numbers(['DRILL', 'FLRY34'])
        <PartCompliance: 2 parts, batch size = 10, 0 indicators>
        """

        for value in part_numbers:
            item_reference = self._definition_factory.create_definition_by_part_number(
                part_number=value,
                database_key=external_database_key,
            )
            self._data.append_record_definition(item_reference)
        return self


class PartComplianceQuery(_ComplianceMixin, _PartQueryBuilder):
    """Evaluates compliance for Granta MI part records against a number of indicators.

    If the parts are associated with materials, parts, specifications, or substances, these are also
    evaluated and returned.

    All methods used to add parts and indicators to this query return the query itself so that they can be chained
    together as required. Records can be added using a combination of any of the available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.PartComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_ids=["Prop65"]
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
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> query = (
    ...     PartImpactedSubstancesQuery()
    ...     .with_part_numbers(['DRILL', 'FLRY34'])
    ...     .with_legislation_ids(["Candidate_AnnexXV"])
    ... )
    >>> cxn.run(query)
    <PartImpactedSubstancesQueryResult: 2 PartWithImpactedSubstances results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = models.GetImpactedSubstancesForPartsRequest
        self._api_method = "post_impactedsubstances_parts"


class _SpecificationQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Provides the subclass for all queries where the items added to the query are direct references to specification
    records."""

    _definition_factory = SpecificationDefinitionFactory()

    def __init__(self) -> None:
        super().__init__()
        self._data.item_type_name = "specifications"
        self._data.batch_size = 10

    @validate_argument_type("specification_ids", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_specification_ids(
        self: _SpecificationQuery,
        specification_ids: List[str],
        external_database_key: Optional[str] = None,
    ) -> _SpecificationQuery:
        """Add a list or set of specifications to a specification query, referenced by specification ID.

        If the records referenced by values in the ``specification_ids`` argument are stored in an external database,
        you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        specification_ids : list[str] | set[str]
            List or set of specification IDs.
        external_database_key : str, optional
            Required if records referenced by the ``specification_ids`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SpecificationComplianceQuery()
        >>> query.with_specification_ids(['MIL-A-8625', 'PSP101'])
        <SpecificationComplianceQuery: 2 specifications, batch size = 10, 0 indicators>
        """

        for specification_id in specification_ids:
            item_reference = self._definition_factory.create_definition_by_specification_id(
                specification_id=specification_id,
                database_key=external_database_key,
            )
            self._data.append_record_definition(item_reference)
        return self


class SpecificationComplianceQuery(_ComplianceMixin, _SpecificationQueryBuilder):
    """Evaluates compliance for Granta MI specification records against a number of indicators.

    If the specifications are associated with specifications, materials, coatings, or substances, these are
    also evaluated and returned.

    All methods used to add specifications and indicators to this query return the query itself so that
    they can be chained together as required. Records can be added using a combination of any of the
    available methods.

    Once the query is fully constructed, use the cxn.
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.SpecificationComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_ids=["Prop65"]
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
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> query = (
    ...     SpecificationImpactedSubstancesQuery()
    ...     .with_specification_ids(['MIL-A-8625', 'PSP101'])
    ...     .with_legislation_ids(["Candidate_AnnexXV"])
    ... )
    >>> cxn.run(query)
    <SpecificationImpactedSubstancesQueryResult:
                    2 SpecificationWithImpactedSubstances results>
    """

    def __init__(self) -> None:
        super().__init__()
        self._request_type = models.GetImpactedSubstancesForSpecificationsRequest
        self._api_method = "post_impactedsubstances_specifications"


class _SubstanceQueryBuilder(_RecordBasedQueryBuilder, ABC):
    """Provides the subclass for all queries where the items added to the query are direct references to substance
    records."""

    _definition_factory = SubstanceComplianceDefinitionFactory()

    def __init__(self) -> None:
        super().__init__()
        self._data.item_type_name = "substances"
        self._data.batch_size = 500

    @validate_argument_type("cas_numbers", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_cas_numbers(
        self: _SubstanceQuery,
        cas_numbers: List[str],
        external_database_key: Optional[str] = None,
    ) -> _SubstanceQuery:
        """Add a list or set of CAS numbers to a substance query.

        The amount of substance in the material is set to 100%.

        If the records referenced by values in the ``cas_numbers`` argument are stored in an external database,
        you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        cas_numbers : list[str] | set[str]
            List or set of CAS numbers.
        external_database_key : str, optional
            Required if records referenced by the ``cas_numbers`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_cas_numbers(['50-00-0', '57-24-9'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for cas_number in cas_numbers:
            item_reference = self._definition_factory.create_definition_by_cas_number(
                cas_number=cas_number,
                database_key=external_database_key,
            )
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("ec_numbers", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_ec_numbers(
        self: "_SubstanceQueryBuilder", ec_numbers: List[str], external_database_key: Optional[str] = None
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of EC numbers to a substance query.

        The amount of substance in the material is set to 100%.

        If the records referenced by values in the ``ec_numbers`` argument are stored in an external database,
        you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        ec_numbers : list[str] | set[str]
            List or set of EC numbers.
        external_database_key : str, optional
            Required if records referenced by the ``ec_numbers`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_ec_numbers(['200-001-8', '200-319-7'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for ec_number in ec_numbers:
            item_reference = self._definition_factory.create_definition_by_ec_number(
                ec_number=ec_number, database_key=external_database_key
            )
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("chemical_names", [str], {str})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_chemical_names(
        self: "_SubstanceQueryBuilder", chemical_names: List[str], external_database_key: Optional[str] = None
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of chemical names to a substance query.

        The amount of substance in the material is set to 100%.

        If the records referenced by values in the ``chemical_names`` argument are stored in an external database,
        you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        chemical_names : list[str] | set[str]
            List or set of chemical names.
        external_database_key : str, optional
            Required if records referenced by the ``chemical_names`` argument are stored in an external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SubstanceComplianceQuery().with_chemical_names(['Formaldehyde', 'Strychnine'])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for chemical_name in chemical_names:
            item_reference = self._definition_factory.create_definition_by_chemical_name(
                chemical_name=chemical_name, database_key=external_database_key
            )
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("record_history_identities_and_amounts", [(int, Number)], {(int, Number)})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_record_history_ids_and_amounts(
        self: "_SubstanceQueryBuilder",
        record_history_identities_and_amounts: List[Tuple[int, float]],
        external_database_key: Optional[str] = None,
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of record history identities and amounts to a substance query.

        The identity and quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        If the records referenced by values in the ``record_history_identities_and_amounts`` argument are stored in an
        external database, you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        record_history_identities_and_amounts : list[tuple[int, float]] | set[tuple[int, float]]
            List or set of record hirstory identities and amounts expressed as a tuple.
        external_database_key : str, optional
            Required if records referenced by the ``record_history_identities_and_amounts`` argument are stored in an
            external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_record_history_ids_and_amounts([(15321, 25), (17542, 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for record_history_id, amount in record_history_identities_and_amounts:
            item_reference = self._definition_factory.create_definition_by_record_history_identity(
                record_history_identity=record_history_id,
                database_key=external_database_key,
            )
            item_reference.percentage_amount = amount
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("record_history_guids_and_amounts", [(str, Number)], {(str, Number)})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_record_history_guids_and_amounts(
        self: "_SubstanceQueryBuilder",
        record_history_guids_and_amounts: List[Tuple[str, float]],
        external_database_key: Optional[str] = None,
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of record history GUID and amounts to a substance query.

        The GUID and quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        If the records referenced by values in the ``record_history_guids_and_amounts`` argument are stored in an
        external database, you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        record_history_guids_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]
            List or set of record history GUIDs and amounts expressed as a tuple.
        external_database_key : str, optional
            Required if records referenced by the ``record_history_guids_and_amounts`` argument are stored in an
            external database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described above.

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
                record_history_guid=record_history_guid,
                database_key=external_database_key,
            )
            item_reference.percentage_amount = amount
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("record_guids_and_amounts", [(str, Number)], {(str, Number)})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_record_guids_and_amounts(
        self: "_SubstanceQueryBuilder",
        record_guids_and_amounts: List[Tuple[str, float]],
        external_database_key: Optional[str] = None,
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of record GUIDs and amounts to a substance query.

        The GUID and quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        If the records referenced by values in the ``record_guids_and_amounts`` argument are stored in an
        external database, you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        record_guids_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]
            List or set of record GUIDs and amounts expressed as a tuple.
        external_database_key : str, optional
            Required if records referenced by the ``record_guids_and_amounts`` argument are stored in an external
            database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

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
            item_reference = self._definition_factory.create_definition_by_record_guid(
                record_guid=record_guid, database_key=external_database_key
            )
            item_reference.percentage_amount = amount
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("cas_numbers_and_amounts", [(str, Number)], {(str, Number)})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_cas_numbers_and_amounts(
        self: "_SubstanceQueryBuilder",
        cas_numbers_and_amounts: List[Tuple[str, float]],
        external_database_key: Optional[str] = None,
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of CAS numbers and amounts to a substance query.

        The CAS numbers and quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        If the records referenced by values in the ``cas_numbers_and_amounts`` argument are stored in an
        external database, you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        cas_numbers_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]
            List or set of CAS numbers and amounts expressed as a tuple.
        external_database_key : str, optional
            Required if records referenced by the ``cas_numbers_and_amounts`` argument are stored in an external
            database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_cas_numbers_and_amounts([('50-00-0', 25), ('57-24-9', 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for cas_number, amount in cas_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_cas_number(
                cas_number=cas_number, database_key=external_database_key
            )
            item_reference.percentage_amount = amount
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("ec_numbers_and_amounts", [(str, Number)], {(str, Number)})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_ec_numbers_and_amounts(
        self: "_SubstanceQueryBuilder",
        ec_numbers_and_amounts: List[Tuple[str, float]],
        external_database_key: Optional[str] = None,
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of EC numbers and amounts to a substance query.

        The EC numbers and quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        If the records referenced by values in the ``ec_numbers_and_amounts`` argument are stored in an
        external database, you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        ec_numbers_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]
            Listor set of EC numbers and amounts expressed as a tuple.
        external_database_key : str, optional
            Required if records referenced by the ``ec_numbers_and_amounts`` argument are stored in an external
            database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_ec_numbers_and_amounts([('200-001-8', 25),
        ...                                            ('200-319-7', 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for ec_number, amount in ec_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_ec_number(
                ec_number=ec_number, database_key=external_database_key
            )
            item_reference.percentage_amount = amount
            self._data.append_record_definition(item_reference)
        return self

    @validate_argument_type("chemical_names_and_amounts", [(str, Number)], {(str, Number)})
    @validate_argument_type("external_database_key", str, NoneType)
    def with_chemical_names_and_amounts(
        self: "_SubstanceQueryBuilder",
        chemical_names_and_amounts: List[Tuple[str, float]],
        external_database_key: Optional[str] = None,
    ) -> "_SubstanceQueryBuilder":
        """Add a list or set of chemical names and amounts to a substance query.

        The chemical names and quantity pairs are expressed as a tuple, with the quantity in units of wt. %.

        If the records referenced by values in the ``chemical_names_and_amounts`` argument are stored in an
        external database, you must provide the external database key using the ``external_database_key`` argument. See
        :ref:`ref_grantami_bomanalytics_external_record_references` for more details.

        Parameters
        ----------
        chemical_names_and_amounts : list[tuple[str, float]] | set[tuple[str, float]]
            List or set of chemical names and amounts expressed as a tuple.
        external_database_key : str, optional
            Required if records referenced by the ``chemical_names_and_amounts`` argument are stored in an external
            database.

            .. versionadded:: 2.4

        Returns
        -------
        Query
            Current query object.

        Raises
        ------
        TypeError
            Error to raise if the method is called with values that do not match the types described earlier.

        Examples
        --------
        >>> query = SubstanceComplianceQuery()
        >>> query = query.with_chemical_names_and_amounts([('Formaldehyde', 25),
        ...                                                ('Strychnine', 0.1)])
        <SubstanceComplianceQuery: 2 substances, batch size = 500, 0 indicators>
        """

        for chemical_name, amount in chemical_names_and_amounts:
            item_reference = self._definition_factory.create_definition_by_chemical_name(
                chemical_name=chemical_name,
                database_key=external_database_key,
            )
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
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_ids=["Prop65"]
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
        self._api_method = "post_compliance_substances"


class _BomFormat(Enum):
    """
    Defines all supported BoM formats and provides a mapping between the expected argument name in a request and the
    associated namespace.
    """

    bom_xml1711 = "http://www.grantadesign.com/17/11/BillOfMaterialsEco"
    bom_xml2301 = "http://www.grantadesign.com/23/01/BillOfMaterialsEco"
    bom_xml2412 = "http://www.grantadesign.com/24/12/BillOfMaterialsEco"
    bom_xml2505 = "http://www.grantadesign.com/25/05/BillOfMaterialsEco"


class _BomQueryDataManager(_BaseQueryDataManager):
    """Stores a BoM for use in queries and generates the kwarg to send to the server.

    Because of the base class, ``_item_definitions`` must be a list. However, this list only ever contains a
    single string because only one BoM can be sent to the server in a single query.
    """

    def __init__(self, supported_bom_formats: List[_BomFormat]) -> None:
        super().__init__()
        self._item_definitions = []
        self._item_results = []
        self._supported_bom_formats = supported_bom_formats
        self.item_type_name = "bom_xml"

    def __repr__(self) -> str:
        items_repr = f' {{bom: "{self._item_definitions[0][:100]}"}}' if self._item_definitions else ""
        return f"<_BomQueryDataManager{items_repr}>"

    @property
    def bom(self) -> str:
        """BoM to use for the query. Because only one BoM is used per query, this property
        enforces storing only one BoM per ``_BomQueryDataManager`` instance.

        Returns
        -------
        bom : str
            BoM to use for the query.
        """
        bom: str = self._item_definitions[0]
        return bom

    @bom.setter
    def bom(self, value: str) -> None:
        self._validate_bom(value)
        self._item_definitions = [value]

    def _validate_bom(self, bom: str) -> _BomFormat:
        """
        Checks that the provided string is valid XML and that the root tag matches the root tag of a supported BoM
        format.
        """
        try:
            root = ElementTree.XML(bom)
        except ElementTree.ParseError as e:
            raise ValueError(f"BoM provided as input is not valid XML ({str(e)}).") from e

        valid_bom_formats = {f"{{{_format.value}}}PartsEco": _format for _format in _BomFormat}
        try:
            _bom_format = valid_bom_formats[root.tag]
        except KeyError:
            raise ValueError("Invalid input BoM. Ensure the document is compliant with the expected XML schema.")
        if _bom_format not in self._supported_bom_formats:
            raise ValueError(f"BoM format {_bom_format.name} ({_bom_format.value}) is not supported by this query.")

        return _bom_format

    @property
    def batched_arguments(self) -> List[Dict[str, str]]:
        """Dictionary with a key that passes the BoM as a kwarg to the request constructor.

        Returns
        -------
            BoM with the appropriate keyword argument.

        Examples
        --------
        >>> bom_item = _BomQueryDataManager("bom_xml1711")
        >>> bom_item.bom = "<PartsEco xmlns..."
        >>> bom_item.batched_arguments
        {"bom_xml1711": "<PartsEco xmlns..."}
        """

        return [{self.item_type_name: self._item_definitions[0]}]

    def _extract_results_from_response(self, response: models.ModelBase) -> List[models.ModelBase]:
        """Extracts the individual results from a response object.

        For BoM queries, the result isn't contained within a larger response object. It is already the object
        that is wanted.

        Returns
        -------
            Response wrapped in a list.
        """
        return [response]


@dataclass
class _BomFormatConfiguration:
    """Defines the class for a BoM request and the api method to pass it to."""

    request_model_type: Type
    api_method_name: str


class _BomQueryBuilder(_BaseQueryBuilder, ABC):
    """Subclass for all queries where the items added to the query are Boms."""

    _supported_bom_formats: List[_BomFormat]

    def __init__(self) -> None:
        self._data: _BomQueryDataManager = _BomQueryDataManager(self._supported_bom_formats)

    @validate_argument_type("bom", str)
    def with_bom(self: _BomQuery, bom: str) -> _BomQuery:
        """Set the BoM to use for the query.

        See the documentation for the parent query class for supported BoM formats.

        Minimal validation is performed on the provided BoM to ensure it defines a supported XML schema. XSD files are
        provided in :mod:`~.schemas` for full validation.

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
           Error raised if the method is called with values that do not match the types described earlier.
        ValueError
            Error raised if the bom isn't valid XML, or isn't in a known supported BoM format.

        Notes
        -----
        See the :py:mod:`ansys.grantami.bomanalytics.schemas` subpackage for Ansys Granta XML BoM Schema Definitions.

        """
        self._data.bom = bom
        return self

    def _validate_items(self) -> None:
        """Override validation method to replace error message with a more generic value, since the `item_type_name`
        isn't known until a BoM has been provided.

        Raises
        -----
        ValueError
            Error to raise if no items have been added to the query.
        """
        if not self._data.populated_inputs:
            raise ValueError("No BoM has been added to the query.")


class BomComplianceQuery(_ComplianceMixin, _BomQueryBuilder):
    """Evaluates compliance for a BoM against a number of indicators.

    The BoM must be in the Ansys Granta 1711 XML BoM format or Ansys Granta 2301 XML BoM format.

    All BoM-based queries only operate on a single BoM. As a result, the ``.with_batch_size()`` method is not
    implemented for BoM-based queries.

    The methods used to add the BoM and Indicators to this query return the query itself so that they can be
    chained together as required.

    Once the query is fully constructed, use the `cxn.`
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.PartComplianceQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> bom = "<PartsEco xmlns..."
    >>> indicator = WatchListIndicator(
    ...     name="Prop 65",
    ...     legislation_ids=["Prop65"]
    ... )
    >>> query = (
    ...     BomComplianceQuery()
    ...     .with_bom(bom)
    ...     .with_indicators([indicator])
    ... )
    >>> cxn.run(query)
    <BomComplianceQueryResult: 1 PartWithCompliance results>
    """

    _supported_bom_formats = [
        _BomFormat.bom_xml1711,
        _BomFormat.bom_xml2301,
        _BomFormat.bom_xml2412,
        _BomFormat.bom_xml2505,
    ]
    _api_method = "post_compliance_bom"
    _request_type = models.GetComplianceForBomRequest


class BomImpactedSubstancesQuery(_ImpactedSubstanceMixin, _BomQueryBuilder):
    """Gets the substances impacted by a list of legislations for a BoM.

    The BoM must be in the Ansys Granta 1711 XML BoM format or Ansys Granta 2301 XML BoM format.

    All BoM-based queries only operate on a single BoM. As a result, the ``.with_batch_size()`` method is not
    implemented for BoM-based queries.

    Once the query is fully constructed, use the `cxn.`
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.BomImpactedSubstancesQueryResult`.

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> bom = "<PartsEco xmlns..."
    >>> query = (
    ...     BomImpactedSubstancesQuery()
    ...     .with_bom("<PartsEco xmlns...")
    ...     .with_legislation_ids(["Candidate_AnnexXV"])
    ... )
    >>> cxn.run(query)
    <BomImpactedSubstancesQueryResult: 1 Bom1711WithImpactedSubstances results>
    """

    _supported_bom_formats = [
        _BomFormat.bom_xml1711,
        _BomFormat.bom_xml2301,
        _BomFormat.bom_xml2412,
        _BomFormat.bom_xml2505,
    ]
    _api_method = "post_impactedsubstances_bom"
    _request_type = models.GetImpactedSubstancesForBomRequest


class _SustainabilityMixin(_ApiMixin):
    _api_method: str
    api_class = api.SustainabilityApi  # TODO consider making private. Manually excluded from docs for now.

    def __init__(self) -> None:
        super().__init__()
        self._preferred_units = models.CommonPreferredUnits()

    def with_units(
        self: _SustainabilityQuery,
        distance: Optional[str] = None,
        energy: Optional[str] = None,
        mass: Optional[str] = None,
    ) -> _SustainabilityQuery:
        """
        Specifies units to use in the response.

        Sets all units, overriding any previous configuration. The specified units must exist in the target database.
        Units not set will default to the API default unit:

        * Distance: ``km``
        * Energy: ``MJ``
        * Mass: ``kg``

        Parameters
        ----------
        distance : str | None
            Unit for distance.
        energy : str | None
            Unit for energy.
        mass : str | None
            Unit for mass.

        """
        if distance is not None:
            self._preferred_units.distance_unit = distance
        if energy is not None:
            self._preferred_units.energy_unit = energy
        if mass is not None:
            self._preferred_units.mass_unit = mass
        return self

    def _run_query(
        self,
        api_instance: api.SustainabilityApi,  # type: ignore[override]
        static_arguments: Dict,
    ) -> ResultBaseClass:
        """Implementation of abstract method _run_query for sustainability endpoints.

        Sets the arguments ``preferred_units`` from user inputs.
        """
        api_method = getattr(api_instance, self._api_method)
        arguments = {
            **static_arguments,
            "preferred_units": self._preferred_units,
        }

        self._call_api(api_method, arguments)
        result: ResultBaseClass = QueryResultFactory.create_result(
            results=self._data.item_results,
            messages=self._data.messages,
        )
        return result

    def _validate_parameters(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._data}>"


class BomSustainabilityQuery(_SustainabilityMixin, _BomQueryBuilder):
    """Evaluates sustainability impact for an XML BoM and returns metrics for each item in the BoM.

    * 23/01 XML BoMs supported by MI Restricted Substances and Sustainability Reports 2024 R2 or later.
    * 24/12 XML BoMs supported by MI Restricted Substances and Sustainability Reports 2025 R2 or later.

    The methods used to configure units and add the BoM to this query return the query itself so that they can be
    chained together as required.

    Once the query is fully constructed, use the `cxn.`
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.BomSustainabilityQueryResult`.

    .. versionadded:: 2.0

    .. versionchanged:: 2.3
       Added support for 24/12 XML BoMs

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> bom = "<PartsEco xmlns..."
    >>> query = (
    ...     BomSustainabilityQuery()
    ...     .with_bom(bom)
    ... )
    >>> cxn.run(query)

    """

    _supported_bom_formats = [_BomFormat.bom_xml2301, _BomFormat.bom_xml2412, _BomFormat.bom_xml2505]
    _api_method = "post_sustainability_bom"
    _request_type = models.GetSustainabilityForBomRequest


class BomSustainabilitySummaryQuery(_SustainabilityMixin, _BomQueryBuilder):
    """
    Evaluates sustainability impact for an XML BoM and returns aggregated metrics.

    * 23/01 XML BoMs supported by MI Restricted Substances and Sustainability Reports 2024 R2 or later.
    * 24/12 XML BoMs supported by MI Restricted Substances and Sustainability Reports 2025 R2 or later.

    The methods used to configure units and add the BoM to this query return the query itself so that they can be
    chained together as required.

    Once the query is fully constructed, use the `cxn.`
    :meth:`~ansys.grantami.bomanalytics._connection.BomAnalyticsClient.run` method to return a result of type
    :class:`~ansys.grantami.bomanalytics._query_results.BomSustainabilitySummaryQueryResult`.

    .. versionadded:: 2.0

    Examples
    --------
    >>> cxn = Connection("http://my_mi_server/mi_servicelayer").with_autologon().connect()
    >>> bom = "<PartsEco xmlns..."
    >>> query = (
    ...     BomSustainabilitySummaryQuery()
    ...     .with_bom(bom)
    ... )
    >>> cxn.run(query)

    """

    _supported_bom_formats = [_BomFormat.bom_xml2301, _BomFormat.bom_xml2412, _BomFormat.bom_xml2505]
    _api_method = "post_sustainabilitysummary_bom"
    _request_type = models.GetSustainabilitySummaryForBomRequest
