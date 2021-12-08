"""BoM Analytics BoM query result definitions.

Defines the representations of the query results themselves, which allows them to implement pivots and summaries over
the entire query result, instead of being constrained to individual parts, materials, etc.
"""
from typing import List, Dict, Type, Callable, Any, Union, TYPE_CHECKING
from collections import defaultdict
from abc import ABC

from ansys.grantami.bomanalytics_openapi import models  # type: ignore[import]

from ._item_results import (
    ItemResultFactory,
    MaterialWithImpactedSubstancesResult,
    MaterialWithComplianceResult,
    PartWithImpactedSubstancesResult,
    PartWithComplianceResult,
    SpecificationWithImpactedSubstancesResult,
    SpecificationWithComplianceResult,
    SubstanceWithComplianceResult,
    ImpactedSubstance,
)
from .indicators import WatchListIndicator, RoHSIndicator

if TYPE_CHECKING:
    from .queries import Query_Result


class QueryResultFactory:
    """Creates query results for a given type of API query. The key to control which result type is created is the type
    of the response from the low-level API.
    """

    registry: Dict = {}
    "Mapping between a query result class and the API response it supports."

    @classmethod
    def register(cls, response_type: Type[models.Model]) -> Callable:
        """Decorator function to register a specific query result class with a response object type.

        Parameters
        ----------
        response_type
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
    def create_result(cls, results: Union[List[models.Model], models.Model], **kwargs: Dict) -> "Query_Result":
        """Factory method to return a specific query result.

        Uses the type of the `results` parameter to determine which specific `Query_Result` to return. If `results` is a
        list, then use the type of the first item in the list (since the list will always be homogeneous).

        Parameters
        ----------
        results
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

        item_result: Query_Result = item_factory_class(results, **kwargs)
        return item_result


class ImpactedSubstancesBaseClass(ABC):
    """Base class for an impacted substances query result.

    This is where generic 'pivots' on the result are implemented, such as aggregating over all items to give a view of
    impacted substances by legislation only, or as a fully flattened list.
    """

    _results: list
    _result_type_name: str

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {len(self._results)} " f"{self._result_type_name} results>"
        return result

    @property
    def impacted_substances_by_legislation(self) -> Dict[str, List["ImpactedSubstance"]]:
        """A view of the results for an impacted substances query grouped by legislation only.

        The substances from all items specified in the query are merged for each legislation, providing a single
        list of impacted substances grouped by legislation only. Substances are duplicated where they appear in
        multiple items for the same legislation.

        Returns
        -------
        impacted_substances : dict[str, :class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]

        Examples
        --------
        >>> result: MaterialImpactedSubstancesQueryResult
        >>> result.impacted_substances_by_legislation
        {'REACH - The Candidate List': [
            <ImpactedSubstance: {"cas_number": 90481-04-2}>, ...]
        }
        """

        results = defaultdict(list)
        for item_result in self._results:
            for (
                legislation_name,
                legislation_result,
            ) in item_result.substances_by_legislation.items():
                results[legislation_name].extend(
                    legislation_result
                )  # TODO: Merge these property, i.e. take max amount? range?
        return dict(results)

    @property
    def impacted_substances(self) -> List["ImpactedSubstance"]:
        """A view of the results for an impacted substances query flattened into a single list.

        The substances from all items specified in the query are merged across item and legislation, providing a
        single flat list. Substances are duplicated where they appear in multiple items and/or legislations.

        Returns
        -------
        impacted_substances : list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]

        Examples
        --------
        >>> result: MaterialImpactedSubstancesQueryResult
        >>> result.impacted_substances
        [<ImpactedSubstance: {"cas_number": 90481-04-2}>, ...]
        """

        results = []
        for item_result in self._results:
            for legislation_result in item_result.substances_by_legislation.values():
                results.extend(legislation_result)  # TODO: Merge these property, i.e. take max amount? range?
        return results


class ComplianceBaseClass(ABC):
    """Base class for a compliance query result.

    This is where generic 'pivots' on the result are implemented, such as aggregating over all items to give a view of
    compliance by indicator only.
    """

    _results: list
    _result_type_name: str

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {len(self._results)} " f"{self._result_type_name} results>"
        return result

    @property
    def compliance_by_indicator(self) -> Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]:
        """The compliance status for each indicator in the original query. The indicator name
        is used as the dictionary key.

        The result for each indicator is determined by taking the worst result for that indicator across all items
        included in the query.

        Returns
        -------
        indicator_results : dict[str, :class:`~ansys.grantami.bomanalytics.indicators.WatchListIndicator` | :class:`~ansys.grantami.bomanalytics.indicators.RoHSIndicator`]  # noqa: E501

        Examples
        --------
        >>> compliance_result: MaterialComplianceQueryResult
        >>> compliance_result.compliance_by_indicator
        {'Prop 65': <WatchListIndicator,
                name: Prop 65,
                flag: WatchListFlag.WatchListAboveThreshold>
        }
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


@QueryResultFactory.register(models.GetImpactedSubstancesForMaterialsMaterial)
class MaterialImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.MaterialImpactedSubstancesQuery`. Describes
    the substances in the specified materials impacted by one or more legislations.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[models.GetImpactedSubstancesForMaterialsMaterial],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        """

        self._results = []
        self._result_type_name = "MaterialWithImpactedSubstances"
        for result in results:
            material_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name=self._result_type_name,
                result_with_impacted_substances=result,
            )
            self._results.append(material_with_impacted_substances)

    @property
    def impacted_substances_by_material(self) -> List["MaterialWithImpactedSubstancesResult"]:
        """The impacted substances for each material specified in the original query.

        Returns
        -------
        impacted_substances_by_material : list[:class:`~ansys.grantami.bomanalytics._item_results.MaterialWithImpactedSubstancesResult`]  # noqa: E501

        Examples
        --------
        >>> result: MaterialImpactedSubstancesQueryResult
        >>> result.impacted_substances_by_material
        [<MaterialWithImpactedSubstancesResult({MaterialId: elastomer-butadienerubber}),
                1 legislations>,...]
        """

        return self._results


@QueryResultFactory.register(models.CommonMaterialWithCompliance)
class MaterialComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.MaterialComplianceQuery`. Describes the
    compliance status of materials against one or more indicators.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[models.CommonMaterialWithCompliance],
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
        self._result_type_name = "MaterialWithCompliance"
        for result in results:
            material_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self._result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            material_with_compliance._add_child_substances(result.substances)
            self._results.append(material_with_compliance)

    @property
    def compliance_by_material_and_indicator(self) -> List["MaterialWithComplianceResult"]:
        """The compliance status for each material specified in the original query.

        Since materials do not have a single well-defined reference, the results are provided as a flat list.

        Returns
        -------
        compliance_by_material_and_indicator : list[:class:`~ansys.grantami.bomanalytics._item_results.MaterialWithComplianceResult`]  # noqa: E501

        Examples
        --------
        >>> result: MaterialComplianceQueryResult
        >>> result.compliance_by_material_and_indicator
        [<MaterialWithComplianceResult({MaterialId: elastomer-butadienerubber}),
                1 indicators>, ...]
        """

        return self._results


@QueryResultFactory.register(models.GetImpactedSubstancesForPartsPart)
class PartImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.PartImpactedSubstancesQuery`. Describes
    the substances in the specified parts impacted by one or more legislations.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[models.GetImpactedSubstancesForPartsPart],
    ):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        """

        self._results = []
        self._result_type_name = "PartWithImpactedSubstances"
        for result in results:
            part_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name=self._result_type_name,
                result_with_impacted_substances=result,
            )
            self._results.append(part_with_impacted_substances)

    @property
    def impacted_substances_by_part(self) -> List["PartWithImpactedSubstancesResult"]:
        """The impacted substances for each part specified in the original query.

        Since parts do not have a single well-defined reference, the results are provided as a flat list.

        Returns
        -------
        impacted_substances_by_part : list[:class:`~ansys.grantami.bomanalytics._item_results.PartWithImpactedSubstancesResult`]  # noqa: E501

        Examples
        --------
        >>> result: PartImpactedSubstancesQueryResult
        >>> result.impacted_substances_by_part
        [<PartWithImpactedSubstancesResult({PartNumber: DRILL}), 1 legislations>,...]
        """

        return self._results


@QueryResultFactory.register(models.CommonPartWithCompliance)
class PartComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.PartComplianceQuery`. Describes the
    compliance status of parts against one or more indicators.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[models.CommonPartWithCompliance],
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
        self._result_type_name = "PartWithCompliance"
        for result in results:
            part_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self._result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            part_with_compliance._add_child_parts(result.parts)
            part_with_compliance._add_child_materials(result.materials)
            part_with_compliance._add_child_specifications(result.specifications)
            part_with_compliance._add_child_substances(result.substances)
            self._results.append(part_with_compliance)

    @property
    def compliance_by_part_and_indicator(self) -> List["PartWithComplianceResult"]:
        """The compliance status for each part specified in the original query.

        Returns
        -------
        compliance_by_part_and_indicator : list[:class:`~ansys.grantami.bomanalytics._item_results.PartWithComplianceResult`]  # noqa: E501

        Examples
        --------
        >>> result: PartComplianceQueryResult
        >>> result.compliance_by_part_and_indicator
        [<PartWithComplianceResult({PartNumber: DRILL}), 1 indicators>,...]
        """

        return self._results


@QueryResultFactory.register(models.GetImpactedSubstancesForSpecificationsSpecification)
class SpecificationImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.SpecificationImpactedSubstancesQuery`.
    Describes the substances in the specified specifications impacted by one or more legislations.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[
            models.GetImpactedSubstancesForSpecificationsSpecification
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
        self._result_type_name = "SpecificationWithImpactedSubstances"
        for result in results:
            specification_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name=self._result_type_name,
                result_with_impacted_substances=result,
            )
            self._results.append(specification_with_impacted_substances)

    @property
    def impacted_substances_by_specification(
        self,
    ) -> List["SpecificationWithImpactedSubstancesResult"]:
        """The impacted substances for each specification specified in the original query.

        Since specifications do not have a single well-defined reference, the results are provided as a flat list.

        Returns
        -------
        impacted_substances_by_specification : list[:class:`~ansys.grantami.bomanalytics._item_results.SpecificationWithImpactedSubstancesResult`]  # noqa: E501

        Examples
        --------
        >>> result: SpecificationImpactedSubstancesQueryResult
        >>> result.impacted_substances_by_specification
        [<SpecificationWithImpactedSubstancesResult({SpecificationId: MIL-A-8625}),
                1 legislations>, ...]
        """

        return self._results


@QueryResultFactory.register(models.CommonSpecificationWithCompliance)
class SpecificationComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.SpecificationComplianceQuery`.
    Describes the compliance status of specifications against one or more indicators.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[models.CommonSpecificationWithCompliance],
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
        self._result_type_name = "SpecificationWithCompliance"
        for result in results:
            specification_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self._result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            specification_with_compliance._add_child_materials(result.materials)
            specification_with_compliance._add_child_specifications(result.specifications)
            specification_with_compliance._add_child_coatings(result.coatings)
            specification_with_compliance._add_child_substances(result.substances)
            self._results.append(specification_with_compliance)

    @property
    def compliance_by_specification_and_indicator(
        self,
    ) -> List["SpecificationWithComplianceResult"]:
        """The compliance status for each specification specified in the original query.

        Returns
        -------
        compliance_by_specification_and_indicator : list[:class:`~ansys.grantami.bomanalytics._item_results.SpecificationWithComplianceResult`]  # noqa: E501

        Examples
        --------
        >>> result: SpecificationComplianceQueryResult
        >>> result.compliance_by_specification_and_indicator
        [<SpecificationWithComplianceResult({SpecificationId: MIL-A-8625}),
                1 indicators>, ...]
        """

        return self._results


@QueryResultFactory.register(models.CommonSubstanceWithCompliance)
class SubstanceComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.SubstanceComplianceQuery`. Describes the
    compliance status of substances against one or more indicators.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[models.CommonSubstanceWithCompliance],
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
        self._result_type_name = "SubstanceWithCompliance"
        for result in results:
            substance_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self._result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            self._results.append(substance_with_compliance)

    @property
    def compliance_by_substance_and_indicator(self) -> List["SubstanceWithComplianceResult"]:
        """The compliance status for each substance specified in the original query.

        Returns
        -------
        compliance_by_substance_and_indicator : list[:class:`~ansys.grantami.bomanalytics._item_results.SubstanceWithComplianceResult`]  # noqa: E501

        Examples
        --------
        >>> result: SubstanceComplianceQueryResult
        >>> result.compliance_by_substance_and_indicator
        [<SubstanceWithComplianceResult({"cas_number": 50-00-0}), 1 indicators>, ...]
        """

        return self._results


@QueryResultFactory.register(models.GetImpactedSubstancesForBom1711Response)
class BomImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery`. Describes
    the substances in the specified BoM impacted by one or more legislations.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(self, results: List[models.GetImpactedSubstancesForBom1711Response]):
        """
        Parameters
        ----------
        results
            The low-level API objects returned by the REST API.
        """

        self._result_type_name = "BomWithImpactedSubstances"
        bom_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
            result_type_name=self._result_type_name,
            result_with_impacted_substances=results[0],
        )
        self._results = [bom_with_impacted_substances]


@QueryResultFactory.register(models.GetComplianceForBom1711Response)
class BomComplianceQueryResult(ComplianceBaseClass):
    """The result of running a :class:`~ansys.grantami.bomanalytics.queries.BomComplianceQuery`. Summarizes the
    compliance status of a BoM against one or more indicators.

    Notes
    -----
    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """

    def __init__(
        self,
        results: List[models.GetComplianceForBom1711Response],
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
        self._result_type_name = "PartWithCompliance"
        parts: List[models.CommonPartWithCompliance] = results[0].parts
        for result in parts:
            part_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name=self._result_type_name,
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            part_with_compliance._add_child_parts(result.parts)
            part_with_compliance._add_child_materials(result.materials)
            part_with_compliance._add_child_specifications(result.specifications)
            part_with_compliance._add_child_substances(result.substances)
            self._results.append(part_with_compliance)

    @property
    def compliance_by_part_and_indicator(self) -> List["PartWithComplianceResult"]:
        """The compliance status for each root part included in the BoM that was specified in the original query.

        Returns
        -------
        compliance_by_part_and_indicator : list[:class:`~ansys.grantami.bomanalytics._item_results.PartWithComplianceResult`]  # noqa: E501

        Examples
        --------
        >>> result: BomComplianceQueryResult
        >>> result.compliance_by_part_and_indicator
        [<PartWithComplianceResult, 1 indicators>]
        """

        return self._results
