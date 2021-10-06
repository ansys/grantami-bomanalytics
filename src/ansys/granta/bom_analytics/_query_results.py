"""Bom Analytics Bom query result definitions.

Defines the representations of the query results themselves, which allows them to implement pivots and summaries over
the entire query result, instead of being constrained to individual parts, materials, etc.
"""

from typing import List, Dict, Type, Callable, Any, Union, TypeVar
from collections import defaultdict
from abc import ABC

from ansys.granta.bomanalytics import models

from ._bom_item_results import BomItemResultFactory

# Required for type hinting
from ._bom_item_results import (
    MaterialWithImpactedSubstances,
    MaterialWithCompliance,
    PartWithImpactedSubstances,
    PartWithCompliance,
    SpecificationWithImpactedSubstances,
    SpecificationWithCompliance,
    SubstanceWithCompliance,
    ImpactedSubstance,
    BoM1711WithImpactedSubstances,
)
from .indicators import Indicator_Definitions

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

    _results = []  # Used to satisfy the linter

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

    _results = []  # Used to satisfy the linter

    @property
    def compliance_by_indicator(self) -> Indicator_Definitions:
        """A view of the results for a compliance query grouped by indicator only.

        Returns
        -------
        dict of (str, `WatchListIndicator` or `RoHSIndicator`)
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
class MaterialImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    """The result of a `MaterialImpactedSubstances` query.

    Parameters
    ----------
    results : list of `models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial`
    """

    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial  # noqa: E501
        ],
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="materialWithImpactedSubstances",
                legislations=result.legislations,
                reference_type=result.reference_type,
                reference_value=result.reference_value,
            )
            for result in results
        ]

    @property
    def impacted_substances_by_material_and_legislation(
        self,
    ) -> List[MaterialWithImpactedSubstances]:
        """The result of a material with impacted substances query.

        Returns
        -------
        list of `MaterialWithImpactedSubstances`
            Material definition objects with the substances impacted by the legislation specified in the query.
        """

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance)
class MaterialComplianceResult(ComplianceBaseClass):
    """The result of a `MaterialCompliance` query.

    Parameters
    ----------
    results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance`
    indicator_definitions : `Indicator_Definitions`
        The indicator definitions supplied as part of the query. Used here as the base for the indicator result objects.
    """

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="materialWithCompliance",
                indicator_results=result.indicators,
                indicator_definitions=indicator_definitions,
                substances_with_compliance=result.substances,
                reference_type=result.reference_type,
                reference_value=result.reference_value,
            )
            for result in results
        ]

    @property
    def compliance_by_material_and_indicator(
        self,
    ) -> List[MaterialWithCompliance]:
        """The compliance status for each indicator of each material in the original query.

        Returns
        ----------
        list of `MaterialWithCompliance`
        """
        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart)
class PartImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    """The result of a `PartImpactedSubstances` query.

    Parameters
    ----------
    results : list of `models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart`
    """

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart],
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="partWithImpactedSubstances",
                legislations=result.legislations,
                reference_type=result.reference_type,
                reference_value=result.reference_value,
            )
            for result in results
        ]

    @property
    def impacted_substances_by_part_and_legislation(
        self,
    ) -> List[PartWithImpactedSubstances]:
        """The result of a material with impacted substances query.

        Returns
        -------
        list of `PartWithImpactedSubstances`
            Part definition objects with the substances impacted by the legislation specified in the query.
        """

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance)
class PartComplianceResult(ComplianceBaseClass):
    """The result of a `PartCompliance` query.

    Parameters
    ----------
    results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance`
    indicator_definitions : `Indicator_Definitions`
        The indicator definitions supplied as part of the query. Used here as the base for the indicator result objects.
    """

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="partWithCompliance",
                indicator_results=result.indicators,
                indicator_definitions=indicator_definitions,
                substances_with_compliance=result.substances,
                child_parts=result.parts,
                child_materials=result.materials,
                child_specifications=result.specifications,
                reference_type=result.reference_type,
                reference_value=result.reference_value,
            )
            for result in results
        ]

    @property
    def compliance_by_part_and_indicator(
        self,
    ) -> List[PartWithCompliance]:
        """The compliance status for each indicator of each part in the original query.

        Returns
        ----------
        list of `PartWithCompliance`
        """

        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification
)
class SpecificationImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    """The result of a `SpecificationImpactedSubstances` query.

    Parameters
    ----------
    results : list of `models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification`
    """

    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification  # noqa: E501
        ],
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="specificationWithImpactedSubstances",
                legislations=result.legislations,
                reference_type=result.reference_type,
                reference_value=result.reference_value,
            )
            for result in results
        ]

    @property
    def impacted_substances_by_specification_and_legislation(
        self,
    ) -> List[SpecificationWithImpactedSubstances]:
        """The result of a specification with impacted substances query.

        Returns
        -------
        list of `SpecificationWithImpactedSubstances`
            Specification definition objects with the substances impacted by the legislation specified in the query.
        """

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance)
class SpecificationComplianceResult(ComplianceBaseClass):
    """The result of a `SpecificationCompliance` query.

    Parameters
    ----------
    results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance`
    indicator_definitions : `Indicator_Definitions`
        The indicator definitions supplied as part of the query. Used here as the base for the indicator result objects.
    """

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="specificationWithCompliance",
                indicator_results=result.indicators,
                indicator_definitions=indicator_definitions,
                substances_with_compliance=result.substances,
                reference_type=result.reference_type,
                reference_value=result.reference_value,
            )
            for result in results
        ]

    @property
    def compliance_by_specification_and_indicator(
        self,
    ) -> List[SpecificationWithCompliance]:
        """The compliance status for each indicator of each specification in the original query.

        Returns
        ----------
        list of `SpecificationWithCompliance`
        """

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance)
class SubstanceComplianceResult(ComplianceBaseClass):
    """The result of a `SubstanceCompliance` query.

    Parameters
    ----------
    results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance`
    indicator_definitions : `Indicator_Definitions`
        The indicator definitions supplied as part of the query. Used here as the base for the indicator result objects.
    """

    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="substanceWithCompliance",
                indicator_results=result.indicators,
                indicator_definitions=indicator_definitions,
                reference_type=result.reference_type,
                reference_value=result.reference_value,
            )
            for result in results
        ]

    @property
    def compliance_by_substance_and_indicator(
        self,
    ) -> List[SubstanceWithCompliance]:
        """The compliance status for each indicator of each substance in the original query.

        Returns
        ----------
        list of `SubstanceWithCompliance`
        """

        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response)
class BomImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    """The result of a `BomImpactedSubstances` query.

    Since by definition a Bom query is only ever on a single Bom, we only get a single result object. The property
    implemented in the other impacted substances result classes that simply wraps `_results` is not useful here.

    Parameters
    ----------
    results : `models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response`
    """

    def __init__(self, results):
        self._results = [BoM1711WithImpactedSubstances(legislations=results.legislations)]


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response)
class BomComplianceResult(ComplianceBaseClass):
    """The result of a `BomCompliance` query.

    Parameters
    ----------
    results : `models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response`
    indicator_definitions : `Indicator_Definitions`
        The indicator definitions supplied as part of the query. Used here as the base for the indicator result objects.
    """

    def __init__(
        self,
        results,
        indicator_definitions: Indicator_Definitions,
    ):
        part = results.parts[0]
        obj = PartWithCompliance(
            indicator_results=part.indicators,
            indicator_definitions=indicator_definitions,
            substances_with_compliance=part.substances,
            child_parts=part.parts,
            child_materials=part.materials,
            child_specifications=part.specifications,
            reference_type=part.reference_type,
            reference_value=part.reference_value,
        )
        self._results = [obj]

    @property
    def compliance_by_part_and_indicator(
        self,
    ) -> List[PartWithCompliance]:
        """The compliance status for each indicator of each part in the original Bom.

        Returns
        ----------
        list of `PartWithCompliance`
        """

        return self._results
