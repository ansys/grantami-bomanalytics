from abc import ABC, abstractmethod
from typing import Union, List, Dict, Callable, Tuple, Any
import warnings
from numbers import Number

from ansys.granta.bomanalytics import models

from .bom_item_definitions import AbstractBomFactory
from .query_results import QueryResultFactory
from .type_check import type_check

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

    @type_check(Any, int)
    def set_batch_size(self, batch_size: int):
        """
        Number of items included in a single request. Sensible values are set by default, but this value can be changed
        to optimize performance if required on a query-by-query basis.

        Parameters
        ----------
        batch_size : int

        Examples
        --------
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.set_batch_size(batch_size=50)
        """

        if batch_size < 1:
            raise ValueError("Batch must be a positive integer")
        self._batch_size = batch_size
        return self

    @property
    def _content(self) -> List[List[models.Model]]:
        for i in range(0, len(self._items), self._batch_size):
            yield [i.definition for i in self._items][
                i : i + self._batch_size
            ]  # noqa: E203 E501


class RecordBasedQueryBuilder(BaseQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._definition_factory = None

    @type_check(Any, [int])
    def add_record_history_ids(self, record_history_identities: List[int]):
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
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.add_record_history_ids([15321, 17542, 942])
        """

        for value in record_history_identities:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_identity=value
            )
            self._items.append(item_reference)
        return self

    @type_check(Any, [str])
    def add_record_history_guids(self, record_history_guids: List[str]):
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
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.add_record_history_guids(['41e20a88-d496-4735-a177-6266fac9b4e2',
        >>>                               'd117d9ad-e6a9-4ba9-8ad8-9a20b6d0b5e2'])
        """

        for value in record_history_guids:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_guid=value
            )
            self._items.append(item_reference)
        return self

    @type_check(Any, [str])
    def add_record_guids(self, record_guids: List[str]):
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
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.add_record_guids(['bdb0b880-e6ee-4f1a-bebd-af76959ae3c8',
        >>>                         'a98cf4b3-f96a-4714-9f79-afe443982c69'])
        """

        for value in record_guids:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_guid=value
            )
            self._items.append(item_reference)
        return self

    @type_check(Any, [{str: str}])
    def add_stk_records(self, stk_records: List[Dict[str, str]]):
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
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.add_stk_records(stk_records)
        """

        record_guids = []
        for r in stk_records:
            if r["db_key"] != self._connection.dbkey:
                db_key = r["db_key"]
                raise ValueError(
                    f'Database key "{db_key}" does not match connection database key "{self._connection.dbkey}"'
                )
            record_guids.append(r["record_guid"])
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

    @type_check(Any, [IndicatorDefinition])
    def add_indicators(self, indicators: List[IndicatorDefinition]):
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
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.add_indicators([WatchListIndicator(...)])
        """

        for value in indicators:
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

    @type_check(Any, [str])
    def add_legislations(self, legislation_names: List[str]):
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
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.add_legislations(["California Proposition 65 List", "REACH - The Candidate List"])
        """

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


class MaterialQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 100
        self._item_type_name = "materials"
        self._definition_factory = None

    @type_check(Any, [str])
    def add_material_ids(self, material_ids: List[str]):
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
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.add_material_ids(['elastomer-butadienerubber',
        >>>                         'NBR-100'])
        """
        for material_id in material_ids:
            item_reference = self._definition_factory.create_definition_by_material_id(
                material_id
            )
            self._items.append(item_reference)
        return self


class MaterialComplianceQuery(ComplianceMixin, MaterialQueryBuilder):
    """
    A query to evaluate compliance for Granta MI material records against a number of indicators. If the materials are
    associated with substances, these are also evaluated and returned.

    All methods used to add materials and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    MaterialComplianceQuery
        The query containing the material records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = MaterialComplianceQuery(conn) \
    >>>             .add_material_ids(['elastomer-butadienerubber', 'NBR-100']) \
    >>>             .add_indicators([WatchListIndicator(...)]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        MaterialComplianceResult
            The result of the compliance query.

        """
        return super().execute()


class MaterialImpactedSubstanceQuery(ImpactedSubstanceMixin, MaterialQueryBuilder):
    """
    A query to determine the substances impacted by a list of legislations for Granta MI material records.

    All methods used to add materials and legislations to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    MaterialImpactedSubstancesQuery
        The query containing the material records and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = MaterialImpactedSubstancesQuery(conn) \
    >>>             .add_material_ids(['elastomer-butadienerubber', 'NBR-100']) \
    >>>             .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        MaterialImpactedSubstancesResult
            The result of the impacted substances query.
        """
        return super().execute()


class PartQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 10
        self._item_type_name = "parts"
        self._definition_factory = None

    @type_check(Any, [str])
    def add_part_numbers(self, part_numbers: List[str]):
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
        >>> conn = Connection(...)
        >>> query = PartComplianceQuery(conn)
        >>> query.add_part_numbers(['ABC12345', 'Q356AQ'])
        """

        for value in part_numbers:
            item_reference = self._definition_factory.create_definition_by_part_number(
                value
            )
            self._items.append(item_reference)
        return self


class PartComplianceQuery(ComplianceMixin, PartQueryBuilder):
    """
    A query to evaluate compliance for Granta MI part records against a number of indicators. If the parts are
    associated with materials, parts, specifications, or substances, these are also evaluated and returned.

    All methods used to add parts and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    PartComplianceQuery
        The query containing the part records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = PartComplianceQuery(conn) \
    >>>             .add_part_numbers(['ABC12345', 'Q356AQ']) \
    >>>             .add_indicators([WatchListIndicator(...)]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        PartComplianceResult
            The result of the compliance query.
        """
        return super().execute()


class PartImpactedSubstanceQuery(ImpactedSubstanceMixin, PartQueryBuilder):
    """
    A query to determine the substances impacted by a list of legislations for Granta MI part records.

    All methods used to add parts and legislations to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    PartImpactedSubstancesQuery
        The query containing the part records and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = PartImpactedSubstancesQuery(conn) \
    >>>             .add_part_numbers(['ABC12345', 'Q356AQ']) \
    >>>             .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        PartImpactedSubstancesResult
            The result of the impacted substances query.
        """
        return super().execute()


class SpecificationQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 10
        self._item_type_name = "specifications"
        self._definition_factory = None

    @type_check(Any, [str])
    def add_specification_ids(self, specification_ids: List[str]):
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
        >>> conn = Connection(...)
        >>> query = SpecificationComplianceQuery(conn)
        >>> query.add_part_numbers(['MIL-A-8625', 'PSP101'])
        """
        for value in specification_ids:
            item_reference = (
                self._definition_factory.create_definition_by_specification_id(value)
            )
            self._items.append(item_reference)
        return self


class SpecificationComplianceQuery(ComplianceMixin, SpecificationQueryBuilder):
    """
    A query to evaluate compliance for Granta MI specification records against a number of indicators. If the
    specifications are associated with materials, specifications, or substances, these are also evaluated and returned.

    All methods used to add specifcations and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    SpecificationComplianceQuery
        The query containing the specification records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = SpecificationComplianceQuery(conn) \
    >>>             .add_specification_ids(['MIL-A-8625', 'PSP101']) \
    >>>             .add_indicators([WatchListIndicator(...)]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        SpecificationComplianceResult
            The result of the compliance query.
        """
        return super().execute()


class SpecificationImpactedSubstanceQuery(
    ImpactedSubstanceMixin, SpecificationQueryBuilder
):
    """
    A query to determine the substances impacted by a list of legislations for Granta MI specification records.

    All methods used to add specifications and legislations to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    SpecificationImpactedSubstancesQuery
        The query containing the specification records and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = SpecificationImpactedSubstancesQuery(conn) \
    >>>             .add_specification_ids(['MIL-A-8625', 'PSP101']) \
    >>>             .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        SpecificationImpactedSubstancesResult
            The result of the impacted substances query.
        """
        return super().execute()


class SubstanceQueryBuilder(RecordBasedQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 500
        self._item_type_name = "substances"
        self._definition_factory = None

    @type_check(Any, [str])
    def add_cas_numbers(self, cas_numbers: List[str]):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_cas_numbers(['50-00-0', '57-24-9'])
        """
        for cas_number in cas_numbers:
            item_reference = self._definition_factory.create_definition_by_cas_number(
                cas_number
            )
            self._items.append(item_reference)
        return self

    @type_check(Any, [str])
    def add_ec_numbers(self, ec_numbers: List[str]):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_ec_numbers(['200-001-8', '200-319-7'])
        """
        for ec_number in ec_numbers:
            item_reference = self._definition_factory.create_definition_by_ec_number(
                ec_number
            )
            self._items.append(item_reference)
        return self

    @type_check(Any, [str])
    def add_chemical_names(self, chemical_names: List[str]):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_chemical_names(['Formaldehyde', 'Strychnine'])
        """
        for chemical_name in chemical_names:
            item_reference = (
                self._definition_factory.create_definition_by_chemical_name(
                    chemical_name
                )
            )
            self._items.append(item_reference)
        return self

    @type_check(Any, [(int, Number)])
    def add_record_history_ids_with_amounts(
        self, record_history_identities_and_amounts: List[Tuple[int, float]]
    ):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_record_history_ids_with_amounts([(15321, 25),
        >>>                                            (17542, 0.1)])
        """

        for record_history_id, amount in record_history_identities_and_amounts:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_identity=record_history_id
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @type_check(Any, [(str, Number)])
    def add_record_history_guids_with_amounts(
        self, record_history_guids_and_amounts: List[Tuple[str, float]]
    ):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_record_history_guids_with_amounts([('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        >>>                                              ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)])
        """
        for record_history_guid, amount in record_history_guids_and_amounts:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_history_guid=record_history_guid
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @type_check(Any, [(str, Number)])
    def add_record_guids_with_amounts(
        self, record_guids_and_amounts: List[Tuple[str, float]]
    ):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_record_guids_with_amounts([('bdb0b880-e6ee-4f1a-bebd-af76959ae3c8', 25),
        >>>                                      ('a98cf4b3-f96a-4714-9f79-afe443982c69', 0.1)])
        """

        for record_guid, amount in record_guids_and_amounts:
            item_reference = self._definition_factory.create_bom_item_definition(
                record_guid=record_guid
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @type_check(Any, [(str, Number)])
    def add_cas_numbers_with_amounts(
        self, cas_numbers_and_amounts: List[Tuple[str, float]]
    ):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_cas_numbers_with_amounts([('50-00-0', 25), ('57-24-9', 0.1)])
        """

        for cas_number, amount in cas_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_cas_number(
                cas_number
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @type_check(Any, [(str, Number)])
    def add_ec_numbers_with_amounts(
        self, ec_numbers_and_amounts: List[Tuple[str, float]]
    ):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_ec_numbers_with_amounts([('200-001-8', 25), ('200-319-7', 0.1)])
        """

        for ec_number, amount in ec_numbers_and_amounts:
            item_reference = self._definition_factory.create_definition_by_ec_number(
                ec_number
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self

    @type_check(Any, [(str, Number)])
    def add_chemical_names_with_amounts(
        self, chemical_names_and_amounts: List[Tuple[str, float]]
    ):
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
        >>> conn = Connection(...)
        >>> query = SubstanceComplianceQuery(conn)
        >>> query.add_chemical_names_with_amounts([('Formaldehyde', 25), ('Strychnine', 0.1)])
        """

        for chemical_name, amount in chemical_names_and_amounts:
            item_reference = (
                self._definition_factory.create_definition_by_chemical_name(
                    chemical_name
                )
            )
            item_reference.percentage_amount = amount
            self._items.append(item_reference)
        return self


class SubstanceComplianceQuery(ComplianceMixin, SubstanceQueryBuilder):
    """
    A query to evaluate compliance for Granta MI substance records against a number of indicators.

    All methods used to add substances and indicators to this query return the query itself, so they can be chained
    together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    SubstanceComplianceQuery
        The query containing the substance records and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = SubstanceComplianceQuery(conn) \
    >>>             .add_cas_numbers(['50-00-0', '57-24-9']) \
    >>>             .add_indicators([WatchListIndicator(...)]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        SubstanceComplianceResult
            The result of the compliance query.
        """
        return super().execute()


class Bom1711QueryBuilder(BaseQueryBuilder, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._batch_size = 1
        self._item_type_name = "bom_xml1711"
        self._definition_factory = None

    @type_check(Any, str)
    def set_bom(self, bom: str):
        """
        Set the bom to be used for the query. Must be in the Granta 17/11 XML format. This format can be saved from the
        BoM Analyzer.

        Parameters
        ----------
        bom : str

        Examples
        --------
        >>> conn = Connection(...)
        >>> query = MaterialComplianceQuery(conn)
        >>> query.set_bom(bom)
        """

        self._items = [self._definition_factory.create_definition(bom=bom)]
        return self


class Bom1711QueryOverride:
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

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    BomComplianceQuery
        The query containing the BoM and indicator definitions.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = BomComplianceQuery(conn) \
    >>>             .set_bom(bom) \
    >>>             .add_indicators([WatchListIndicator(...)]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        BoMComplianceResult
            The result of the compliance query.
        """
        return super().execute()


class BomImpactedSubstancesQuery(
    Bom1711QueryOverride, ImpactedSubstanceMixin, Bom1711QueryBuilder
):
    """
    A query to determine the substances impacted by a list of legislations for a Bill of Maerials in 17/11 XML format.

    All methods used to add the bom and legislations to this query return the query itself, so they can be
    chained together as required. Use the .execute() method once the query is fully constructed to return the result.

    Parameters
    ----------
    connection : Connection
        The connection to the Granta MI server.

    Returns
    -------
    BomImpactedSubstancesQuery
        The query containing the bom and legislation names.

    Examples
    --------
    >>> conn = Connection(...)
    >>> result = BomImpactedSubstancesQuery(conn) \
    >>>             .set_bom(bom) \
    >>>             .add_legislations(["California Proposition 65 List", "REACH - The Candidate List"]) \
    >>>             .execute()
    """

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
        """
        Run the query against the Granta MI database and return the results.

        Returns
        -------
        BoMImpactedSubstancesResult
            The result of the impacted substances query.
        """
        return super().execute()
