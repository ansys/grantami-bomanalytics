"""Bom Analytics Bom query result definitions.

Defines the representations of the query results themselves, which allows them to implement pivots and summaries over
the entire query result, instead of being constrained to individual parts, materials, etc.
"""

from typing import List, Dict, Type, Callable, Any, Union, TypeVar
from collections import defaultdict
from abc import ABC

from ansys.granta.bomanalytics import models

from ._item_results import ItemResultFactory

# Required for type hinting
from ._item_results import (
    MaterialWithImpactedSubstancesResult,
    MaterialWithComplianceResult,
    PartWithImpactedSubstancesResult,
    PartWithComplianceResult,
    SpecificationWithImpactedSubstancesResult,
    SpecificationWithComplianceResult,
    SubstanceWithComplianceResult,
    ImpactedSubstance,
    BoM1711WithImpactedSubstancesResult,
)

from .indicators import WatchListIndicator, RoHSIndicator

Query_Result = TypeVar(
    "Query_Result",
    covariant=True,
    bound=Union["ImpactedSubstancesBaseClass", "ComplianceBaseClass"],
)


class QueryResultFactory:
    """Creates query results for a given type of API query. The key to control which result type is created is the type
     of the response from the low-level API.

    Class Attributes
    ----------------
    registry : dict
        Mapping between a query result class and the API response it supports.
    """

    registry = {}

    @classmethod
    def register(cls, response_type: Type[models.Model]) -> Callable:
        """Decorator function to register a specific query result class with a response object type.

        Parameters
        ----------
        response_type : Type[models.Model]
            The type of response to be registered.

        Returns
        -------
        Callable
            The function that's being decorated.
        """

        def inner(item_factory: Any) -> Any:
            cls.registry[response_type] = item_factory
            return item_factory

        return inner

    @classmethod
    def create_result(cls, results: Union[List[models.Model], models.Model], **kwargs) -> Query_Result:
        """Factory method to return a specific query result.

        Uses the type of the `results` parameter to determine which specific `Query_Result` to return. If `results` is a
        list, then use the type of the first item in the list (since the list will always be homogeneous).

        Parameters
        ----------
        results : models.Model or list of models.Model
            The result or results returned from the low-level API.
        **kwargs
            All other arguments required to instantiate the item definition, including the `reference_value` for
            `RecordDefinition`-based results.

        Returns
        -------
        Query_Result

        Raises
        ------
        RuntimeError
            If a query type is not registered to any factory.
        """

        try:
            response_type = type(results[0])
        except TypeError:
            response_type = type(results)  # Bom results aren't returned in an iterable
        try:
            item_factory_class = cls.registry[response_type]
        except KeyError as e:
            raise RuntimeError(f'Unregistered response type "{response_type}"').with_traceback(e.__traceback__)

        return item_factory_class(results, **kwargs)


class ImpactedSubstancesBaseClass(ABC):
    """Base class for an impacted substances query result.

    This is where generic 'pivots' on the result are implemented, such as aggregating over all items to give a view of
    impacted substances by legislation only, or as a fully flattened list.
    """

    # Used to satisfy the linter
    _results = []
    result_type_name: str = ""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {len(self._results)} {self.result_type_name} results>"

    @property
    def impacted_substances_by_legislation(
        self,
    ) -> Dict[str, List[ImpactedSubstance]]:
        """A view of the results for an impacted substances query grouped by legislation only.

        Returns
        -------
        dict of (str, list of `ImpactedSubstances`)
            The substances from all items specified in the query are merged for each legislation, providing a single
            list of impacted substances grouped by legislation only. Substances are duplicated where they appear in
            multiple items for the same legislation.
        """

        results = defaultdict(list)
        for item_result in self._results:
            for (
                legislation_name,
                legislation_result,
            ) in item_result.legislations.items():
                results[legislation_name].extend(
                    legislation_result.substances
                )  # TODO: Merge these property, i.e. take max amount? range?
        return results

    @property
    def impacted_substances(self) -> List[ImpactedSubstance]:
        """A view of the results for an impacted substances query flattened into a single list.

        Returns
        -------
        list of `ImpactedSubstances`
            The substances from all items specified in the query are merged across item and legislation, providing a
            single flat list. Substances are duplicated where they appear in multiple items and/or legislations.
        """

        results = []
        for item_result in self._results:
            for legislation_result in item_result.legislations.values():
                results.extend(
                    legislation_result.substances
                )  # TODO: Merge these property, i.e. take max amount? range?
        return results


class ComplianceBaseClass(ABC):
    """Base class for a compliance query result.

    This is where generic 'pivots' on the result are implemented, such as aggregating over all items to give a view of
    compliance by indicator only.
    """

    # Used to satisfy the linter
    _results = []
    result_type_name: str = ""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {len(self._results)} {self.result_type_name} results>"

    @property
    def compliance_by_indicator(self) -> Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]:
        """A view of the results for a compliance query grouped by indicator only.

        The compliance results from all items specified in the query are merged for each indicator by taking the
        worst result returned for that indicator.
        """

        results = {}
        for result in self._results:
            for indicator_name, indicator_result in result.indicators.items():
                if indicator_name not in results:
                    results[indicator_name] = indicator_result
                else:
                    if indicator_result.flag > results[indicator_name].flag:
                        results[indicator_name] = indicator_result
        return results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial)
class MaterialImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.MaterialImpactedSubstancesQuery`."""

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        """

        self._results = []
        self.result_type_name = "MaterialWithImpactedSubstances"
        for result in results:
            material_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name=self.result_type_name,
                result_with_impacted_substances=result,
            )
            self._results.append(material_with_impacted_substances)

    @property
    def impacted_substances_by_material_and_legislation(self) -> List[MaterialWithImpactedSubstancesResult]:
        """The impacted substances for each legislation in the original query, grouped by material and
        legislation."""

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance)
class MaterialComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.MaterialComplianceQuery`."""

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        indicator_definitions
            The indicator definitions supplied as part of the query. Used here as the base for the indicator result
             objects.
        """

        self._results = []
        self.result_type_name = "MaterialWithCompliance"
        for result in results:
            material_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self.result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            material_with_compliance._add_child_substances(result.substances)
            self._results.append(material_with_compliance)

    @property
    def compliance_by_material_and_indicator(self) -> List[MaterialWithComplianceResult]:
        """The compliance status for each indicator in the original query, grouped by material."""

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart)
class PartImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.PartImpactedSubstancesQuery`."""

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        """

        self._results = []
        self.result_type_name = "PartWithImpactedSubstances"
        for result in results:
            part_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name=self.result_type_name,
                result_with_impacted_substances=result,
            )
            self._results.append(part_with_impacted_substances)

    @property
    def impacted_substances_by_part_and_legislation(self) -> List[PartWithImpactedSubstancesResult]:
        """The impacted substances for each legislation in the original query, grouped by part and
        legislation."""

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance)
class PartComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.PartComplianceQuery`."""

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        indicator_definitions
            The indicator definitions supplied as part of the query. Used here as the base for the indicator result
             objects.
        """

        self._results = []
        self.result_type_name = "PartWithCompliance"
        for result in results:
            part_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self.result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            part_with_compliance._add_child_parts(result.parts)
            part_with_compliance._add_child_materials(result.materials)
            part_with_compliance._add_child_specifications(result.specifications)
            part_with_compliance._add_child_substances(result.substances)
            self._results.append(part_with_compliance)

    @property
    def compliance_by_part_and_indicator(self) -> List[PartWithComplianceResult]:
        """The compliance status for each indicator in the original query, grouped by part."""

        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification
)
class SpecificationImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.SpecificationImpactedSubstancesQuery`."""

    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification
            # noqa: E501
        ],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        """

        self._results = []
        self.result_type_name = "SpecificationWithImpactedSubstances"
        for result in results:
            specification_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name=self.result_type_name,
                result_with_impacted_substances=result,
            )
            self._results.append(specification_with_impacted_substances)

    @property
    def impacted_substances_by_specification_and_legislation(self) -> List[SpecificationWithImpactedSubstancesResult]:
        """The impacted substances for each legislation in the original query, grouped by specification and
        legislation."""

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance)
class SpecificationComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.SpecificationComplianceQuery`."""

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        indicator_definitions
            The indicator definitions supplied as part of the query. Used here as the base for the indicator result
             objects.
        """

        self._results = []
        self.result_type_name = "SpecificationWithCompliance"
        for result in results:
            specification_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self.result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            specification_with_compliance._add_child_materials(result.materials)
            specification_with_compliance._add_child_specifications(result.specifications)
            specification_with_compliance._add_child_coatings(result.coatings)
            specification_with_compliance._add_child_substances(result.substances)
            self._results.append(specification_with_compliance)

    @property
    def compliance_by_specification_and_indicator(self) -> List[SpecificationWithComplianceResult]:
        """The compliance status for each indicator in the original query, grouped by specification."""

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance)
class SubstanceComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.SubstanceComplianceQuery`."""

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        indicator_definitions
            The indicator definitions supplied as part of the query. Used here as the base for the indicator result
             objects.
        """

        self._results = []
        self.result_type_name = "SubstanceWithCompliance"
        for result in results:
            substance_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self.result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            self._results.append(substance_with_compliance)

    @property
    def compliance_by_substance_and_indicator(self) -> List[SubstanceWithComplianceResult]:
        """The compliance status for each indicator in the original query, grouped by substance."""

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response)
class BomImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.BomImpactedSubstancesQuery`."""

    def __init__(self, results: models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        """

        self._results = [BoM1711WithImpactedSubstancesResult(legislations=results.legislations)]
        self.result_type_name = "Bom1711WithImpactedSubstances"


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response)
class BomComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`ansys.granta.bom_analytics.queries.BomComplianceQuery`."""

    def __init__(
        self,
        results: models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        indicator_definitions
            The indicator definitions supplied as part of the query. Used here as the base for the indicator result
             objects.
        """

        part = results.parts[0]
        part_with_compliance = PartWithComplianceResult(
            indicator_results=part.indicators,
            indicator_definitions=indicator_definitions,
            reference_type=part.reference_type,
            reference_value=part.reference_value,
        )
        part_with_compliance._add_child_parts(part.parts)
        part_with_compliance._add_child_materials(part.materials)
        part_with_compliance._add_child_specifications(part.specifications)
        part_with_compliance._add_child_substances(part.substances)
        self._results = [part_with_compliance]
        self.result_type_name = "PartWithCompliance"

    @property
    def compliance_by_part_and_indicator(self) -> List[PartWithComplianceResult]:
        """The compliance status for each indicator in the original query."""

        return self._results
