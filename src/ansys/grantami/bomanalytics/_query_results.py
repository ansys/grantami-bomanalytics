# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""BoM Analytics BoM query result definitions.

Defines the representations of the query results themselves, which allows them to implement pivots and summaries over
the entire query result instead of being constrained to individual parts and materials.
"""

from abc import ABC
from collections import defaultdict, namedtuple
from typing import Any, Callable, Dict, List, Type, Union
import warnings

from ansys.grantami.bomanalytics_openapi import models

from ._item_results import (
    ImpactedSubstance,
    ItemResultFactory,
    MaterialSummaryResult,
    MaterialWithComplianceResult,
    MaterialWithImpactedSubstancesResult,
    PartWithComplianceResult,
    PartWithImpactedSubstancesResult,
    PartWithSustainabilityResult,
    ProcessSummaryResult,
    SpecificationWithComplianceResult,
    SpecificationWithImpactedSubstancesResult,
    SubstanceWithComplianceResult,
    SustainabilityPhaseSummaryResult,
    TransportSummaryResult,
    TransportWithSustainabilityResult,
)
from ._typing import _raise_if_unset
from .indicators import RoHSIndicator, WatchListIndicator

LogMessage = namedtuple("LogMessage", ["severity", "message"])
""" Message returned by Granta MI when running the query.

Messages marked with the error ``severity`` are more likely to produce incorrect results and should be treated with
increased caution.

Attributes
----------
severity : str
    Level of severity. Options are ``"error"``, ``"warning"``, and ``"information"``.
message : str
    Description of the issue.
"""


class QueryResultFactory:
    """Creates query results for a given type of API query.

    The type of the response from the low-level API is the key to controlling which result type is created.
    """

    registry: Dict = {}
    "Mapping between a query result class and the API response it supports."

    @classmethod
    def register(cls, response_type: Type[models.ModelBase]) -> Callable:
        """Registers a specific query result class with a response object type.

        Parameters
        ----------
        response_type
            Type of response to be registered.

        Returns
        -------
        Callable
            Function that's being decorated.
        """

        def inner(item_factory: Any) -> Any:
            cls.registry[response_type] = item_factory
            return item_factory

        return inner

    @classmethod
    def create_result(
        cls,
        results: Union[List[models.ModelBase], models.ModelBase],
        messages: List[models.CommonLogEntry],
        **kwargs: Dict,
    ) -> "ResultBaseClass":
        """Returns a specific query result.

        Uses the type of the ``results`` parameter to determine which specific ``Query_Result`` object to return.
        If the ``results`` parameter is a list, use the type of the first item in the list (because the list will
        always be homogeneous).

        Parameters
        ----------
        results
            Result or results to return from the low-level API.
        messages
            Logs returned by Granta MI describing any problems encountered when running the query.
        **kwargs
            All other arguments required to instantiate the item definition, including the ``reference_value`` for
            ``RecordDefinition``-based results.

        Returns
        -------
        Query_Result

        Raises
        ------
        RuntimeError
            Error raised if a query type is not registered to any factory.
        """

        try:
            response_type = type(results[0])  # type: ignore[index]
        except TypeError:
            response_type = type(results)  # BoM results aren't returned in an iterable
        try:
            item_factory_class = cls.registry[response_type]
        except KeyError as e:
            raise RuntimeError(f"Unregistered response type" f' "{response_type}"').with_traceback(e.__traceback__)

        item_result: ResultBaseClass = item_factory_class(results=results, messages=messages, **kwargs)
        return item_result


class ResultBaseClass(ABC):
    def __init__(self, log_messages: List[models.CommonLogEntry]) -> None:
        self._messages = [LogMessage(severity=msg.severity, message=msg.message) for msg in log_messages]

    @property
    def messages(self) -> List[LogMessage]:
        """Messages generated by Granta MI when running the query. The presence of one or more messages means
        that something unexpected happened when running the query but that the query could still be completed.

        Messages are sorted in order of decreasing severity and are available in the Service Layer log file.

        Messages are also logged using the Python ``logging`` module to the ``ansys.grantami.bomanalytics`` logger. By
        default, messages with a severity of ``"warning"`` or higher are printed on stderr.
        """

        return self._messages


class ImpactedSubstancesBaseClass(ResultBaseClass):
    """Retrieves an impacted substances query result.

    This is where generic pivots on the result are implemented, such as aggregating over all items to give a
    view of impacted substances by legislation only or as a fully flattened list.
    """

    _results: List

    @property
    def impacted_substances_by_legislation(self) -> Dict[str, List["ImpactedSubstance"]]:
        """View of the results for a query for impacted substances, grouped by legislation only.

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
        {'Candidate_AnnexXV': [
            <ImpactedSubstance: {"cas_number": 90481-04-2}>, ...]
        }
        """

        results = defaultdict(list)
        for item_result in self._results:
            for (
                legislation_name,
                legislation_result,
            ) in item_result.substances_by_legislation.items():
                results[legislation_name].extend(legislation_result)
        return dict(results)

    @property
    def impacted_substances(self) -> List["ImpactedSubstance"]:
        """View of the results for a query for impacted substances, flattened into a single list.

        The substances from all items specified in the query are merged across item and legislation, providing a
        single flat list. Substances are duplicated where they appear in multiple items or legislations.

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
                results.extend(legislation_result)
        return results


class ComplianceBaseClass(ResultBaseClass):
    """Retrieves a compliance query result.

    This is where generic 'pivots' on the result are implemented, such as aggregating over all items to give a view of
    compliance by indicator only.
    """

    _results: List
    _result_type_name: str

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {len(self._results)} " f"{self._result_type_name} results>"
        return result

    @property
    def compliance_by_indicator(self) -> Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]:
        """Compliance status for each indicator in the original query. The indicator name
        is used as the dictionary key.

        The result for each indicator is determined by taking the worst result for that indicator across all items
        included in the query.

        Returns
        -------
        dict[str, |WatchListIndicator| | |RoHSIndicator|]

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
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.MaterialImpactedSubstancesQuery`
    class.

    This class describes the substances in the specified materials impacted by one or more legislations.

    Examples
    --------
    >>> result: MaterialImpactedSubstancesQueryResult
    >>> result.messages
    [LogMessage(severity='warning', message='Material "ABS+PVC (flame retarded)" has
        2 substance row(s) with missing substance links.')]
    """

    def __init__(
        self,
        results: List[models.GetImpactedSubstancesForMaterialsMaterial],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        """

        super().__init__(messages)
        self._results = []
        for result in results:
            material_with_impacted_substances = ItemResultFactory.create_material_impacted_substances_result(
                result_with_impacted_substances=result,
            )
            self._results.append(material_with_impacted_substances)

    @property
    def impacted_substances_by_material(self) -> List["MaterialWithImpactedSubstancesResult"]:
        """Impacted substances for each material specified in the original query.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.MaterialWithImpactedSubstancesResult`]

        Examples
        --------
        >>> result: MaterialImpactedSubstancesQueryResult
        >>> result.impacted_substances_by_material
        [<MaterialWithImpactedSubstancesResult({MaterialId: elastomer-butadienerubber}),
                1 legislations>,...]
        """

        return self._results

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {len(self._results)} MaterialWithImpactedSubstances results>"
        return result


@QueryResultFactory.register(models.CommonMaterialWithCompliance)
class MaterialComplianceQueryResult(ComplianceBaseClass):
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.MaterialComplianceQuery`
    class.

    This class describes the compliance status of materials against one or more indicators.
    """

    _result_type_name = "MaterialWithCompliance"

    def __init__(
        self,
        results: List[models.CommonMaterialWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        indicator_definitions
            Indicator definitions supplied as part of the query. This parameter is used here as the base
            for the indicator result objects.
        """

        super().__init__(messages)
        self._results = []
        for result in results:
            material_with_compliance = ItemResultFactory.create_material_compliance_result(
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            material_with_compliance._add_child_substances(_raise_if_unset(result.substances))
            self._results.append(material_with_compliance)

    @property
    def compliance_by_material_and_indicator(self) -> List["MaterialWithComplianceResult"]:
        """Compliance status for each material specified in the original query.

        Because materials do not have a single well-defined reference, the results are provided as a flat list.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.MaterialWithComplianceResult`]

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
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.PartImpactedSubstancesQuery`
    class.

    This class describes the substances in the specified parts impacted by one or more legislations.
    """

    def __init__(
        self,
        results: List[models.GetImpactedSubstancesForPartsPart],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        """

        super().__init__(messages)
        self._results = []
        for result in results:
            part_with_impacted_substances = ItemResultFactory.create_part_impacted_substances_result(
                result_with_impacted_substances=result,
            )
            self._results.append(part_with_impacted_substances)

    @property
    def impacted_substances_by_part(self) -> List["PartWithImpactedSubstancesResult"]:
        """Impacted substances for each part specified in the original query.

        Because parts do not have a single well-defined reference, the results are provided as a flat list.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.PartWithImpactedSubstancesResult`]

        Examples
        --------
        >>> result: PartImpactedSubstancesQueryResult
        >>> result.impacted_substances_by_part
        [<PartWithImpactedSubstancesResult({PartNumber: DRILL}), 1 legislations>,...]
        """

        return self._results

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {len(self._results)} PartWithImpactedSubstances results>"
        return result


@QueryResultFactory.register(models.CommonPartWithCompliance)
class PartComplianceQueryResult(ComplianceBaseClass):
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.PartComplianceQuery`
    class.

    This class describes the compliance status of parts against one or more indicators.
    """

    _result_type_name = "PartWithCompliance"

    def __init__(
        self,
        results: List[models.CommonPartWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        indicator_definitions
            Indicator definitions supplied as part of the query. This parameter is used
            here as the base for the indicator result objects.
        """

        super().__init__(messages)
        self._results = []
        for result in results:
            part_with_compliance = ItemResultFactory.create_part_compliance_result(
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            part_with_compliance._add_child_parts(_raise_if_unset(result.parts))
            part_with_compliance._add_child_materials(_raise_if_unset(result.materials))
            part_with_compliance._add_child_specifications(_raise_if_unset(result.specifications))
            part_with_compliance._add_child_substances(_raise_if_unset(result.substances))
            self._results.append(part_with_compliance)

    @property
    def compliance_by_part_and_indicator(self) -> List["PartWithComplianceResult"]:
        """Compliance status for each part specified in the original query.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.PartWithComplianceResult`]

        Examples
        --------
        >>> result: PartComplianceQueryResult
        >>> result.compliance_by_part_and_indicator
        [<PartWithComplianceResult({PartNumber: DRILL}), 1 indicators>,...]
        """

        return self._results


@QueryResultFactory.register(models.GetImpactedSubstancesForSpecificationsSpecification)
class SpecificationImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """Retrieves the result of running the
    :class:`~ansys.grantami.bomanalytics.queries.SpecificationImpactedSubstancesQuery`
    class.

    This class describes the substances in the specified specifications impacted by one or more legislations.
    """

    def __init__(
        self,
        results: List[models.GetImpactedSubstancesForSpecificationsSpecification],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the rest API is to return.
        """

        super().__init__(messages)
        self._results = []
        for result in results:
            specification_with_impacted_substances = ItemResultFactory.create_specification_impacted_substances_result(
                result_with_impacted_substances=result,
            )
            self._results.append(specification_with_impacted_substances)

    @property
    def impacted_substances_by_specification(
        self,
    ) -> List["SpecificationWithImpactedSubstancesResult"]:
        """Impacted substances for each specification specified in the original query. Because
        specifications do not have a single well-defined reference, the results are provided as
        a flat list.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.SpecificationWithImpactedSubstancesResult`]

        Examples
        --------
        >>> result: SpecificationImpactedSubstancesQueryResult
        >>> result.impacted_substances_by_specification
        [<SpecificationWithImpactedSubstancesResult({SpecificationId: MIL-A-8625}),
                1 legislations>, ...]
        """

        return self._results

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {len(self._results)} SpecificationWithImpactedSubstances results>"
        return result


@QueryResultFactory.register(models.CommonSpecificationWithCompliance)
class SpecificationComplianceQueryResult(ComplianceBaseClass):
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.SpecificationComplianceQuery`
    class.

    This class describes the compliance status of specifications against one or more indicators.
    """

    _result_type_name = "SpecificationWithCompliance"

    def __init__(
        self,
        results: List[models.CommonSpecificationWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        indicator_definitions
            Indicator definitions supplied as part of the query. This parameter is used here as the base
            for the indicator result objects.
        """

        super().__init__(messages)
        self._results = []
        for result in results:
            specification_with_compliance = ItemResultFactory.create_specification_compliance_result(
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            specification_with_compliance._add_child_materials(_raise_if_unset(result.materials))
            specification_with_compliance._add_child_specifications(_raise_if_unset(result.specifications))
            specification_with_compliance._add_child_coatings(_raise_if_unset(result.coatings))
            specification_with_compliance._add_child_substances(_raise_if_unset(result.substances))
            self._results.append(specification_with_compliance)

    @property
    def compliance_by_specification_and_indicator(
        self,
    ) -> List["SpecificationWithComplianceResult"]:
        """Compliance status for each specification specified in the original query.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.SpecificationWithComplianceResult`]

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
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.SubstanceComplianceQuery`
    class.

    This class describes the compliance status of substances against one or more indicators.
    """

    def __init__(
        self,
        results: List[models.CommonSubstanceWithCompliance],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        indicator_definitions
            Indicator definitions supplied as part of the query. This parameter is used here as the base
            for the indicator result objects.
        """

        super().__init__(messages)
        self._results = []
        self._result_type_name = "SubstanceWithCompliance"
        for result in results:
            substance_with_compliance = ItemResultFactory.create_substance_compliance_result(
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            self._results.append(substance_with_compliance)

    @property
    def compliance_by_substance_and_indicator(self) -> List["SubstanceWithComplianceResult"]:
        """Compliance status for each substance specified in the original query.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.SubstanceWithComplianceResult`]

        Examples
        --------
        >>> result: SubstanceComplianceQueryResult
        >>> result.compliance_by_substance_and_indicator
        [<SubstanceWithComplianceResult({"cas_number": 50-00-0}), 1 indicators>, ...]
        """

        return self._results


@QueryResultFactory.register(models.GetImpactedSubstancesForBom1711Response)
@QueryResultFactory.register(models.GetImpactedSubstancesForBom2301Response)
class BomImpactedSubstancesQueryResult(ImpactedSubstancesBaseClass):
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.BomImpactedSubstancesQuery`
    class.

    This class describes the substances in the specified BoM impacted by one or more legislations.
    """

    def __init__(
        self,
        results: List[models.GetImpactedSubstancesForBom1711Response],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        """

        super().__init__(messages)
        bom_with_impacted_substances = ItemResultFactory.create_bom_impacted_substances_result(
            result_with_impacted_substances=results[0],
        )
        self._results = [bom_with_impacted_substances]

    def __repr__(self) -> str:
        result = f"<{self.__class__.__name__}: {len(self._results)} BomWithImpactedSubstances results>"
        return result


@QueryResultFactory.register(models.GetComplianceForBom1711Response)
@QueryResultFactory.register(models.GetComplianceForBom2301Response)
class BomComplianceQueryResult(ComplianceBaseClass):
    """Retrieves the result of running the :class:`~ansys.grantami.bomanalytics.queries.BomComplianceQuery`
    class.

    This class summarizes the compliance status of a BoM against one or more indicators.
    """

    _result_type_name = "PartWithCompliance"

    def __init__(
        self,
        results: List[models.GetComplianceForBom1711Response],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
        messages: List[models.CommonLogEntry],
    ):
        """
        Parameters
        ----------
        results
            Low-level API objects that the REST API is to return.
        indicator_definitions
            Indicator definitions supplied as part of the query. This parameter is used here as the base
            for the indicator result objects.
        """

        super().__init__(messages)
        self._results = []
        parts = _raise_if_unset(results[0].parts)
        for result in parts:
            part_with_compliance = ItemResultFactory.create_part_compliance_result(
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            part_with_compliance._add_child_parts(_raise_if_unset(result.parts))
            part_with_compliance._add_child_materials(_raise_if_unset(result.materials))
            part_with_compliance._add_child_specifications(_raise_if_unset(result.specifications))
            part_with_compliance._add_child_substances(_raise_if_unset(result.substances))
            self._results.append(part_with_compliance)

    @property
    def compliance_by_part_and_indicator(self) -> List["PartWithComplianceResult"]:
        """Compliance status for each root part included in the BoM specified in the original
        query.

        Returns
        -------
        list[:class:`~ansys.grantami.bomanalytics._item_results.PartWithComplianceResult`]

        Examples
        --------
        >>> result: BomComplianceQueryResult
        >>> result.compliance_by_part_and_indicator
        [<PartWithComplianceResult, 1 indicators>]
        """

        return self._results


@QueryResultFactory.register(models.GetSustainabilityForBom2301Response)
class BomSustainabilityQueryResult(ResultBaseClass):
    """Describes the result of running a :class:`~ansys.grantami.bomanalytics.queries.BomSustainabilityQuery`.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        results: List[models.GetSustainabilityForBom2301Response],
        messages: List[models.CommonLogEntry],
    ) -> None:
        super().__init__(messages)
        self._response = results[0]
        if not self._response.parts:
            raise ValueError(
                "Found no part in BoM sustainability response. Ensure the request BoM defines a single root part."
            )
        if len(self._response.parts) > 1:
            warnings.warn(
                f"BomSustainabilityQuery only supports a single root part (found {len(self._response.parts)}). "
                f"Additional root parts do not include sustainability results and are not exposed in the query result"
                f" properties."
            )
        # Exposing only a single root part:
        # API V1 only processes the first root part but still returns part empty part objects for extra root parts.
        # API V2 will only return a single root part.
        self._part: PartWithSustainabilityResult = ItemResultFactory.create_part_with_sustainability(
            result_with_sustainability=self._response.parts[0]
        )

        self._transports: List[TransportWithSustainabilityResult] = [
            ItemResultFactory.create_transport_with_sustainability(result_with_sustainability=transport)
            for transport in _raise_if_unset(self._response.transport_stages)
        ]

    @property
    def part(self) -> PartWithSustainabilityResult:
        """Sustainability information for the root part included in the BoM specified in the original
        query.
        """
        return self._part

    @property
    def transport_stages(self) -> List[TransportWithSustainabilityResult]:
        """Sustainability information for each transport stage included in the BoM specified in the original
        query.
        """
        return self._transports

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


@QueryResultFactory.register(models.GetSustainabilitySummaryForBom2301Response)
class BomSustainabilitySummaryQueryResult(ResultBaseClass):
    """Describes the result of running a :class:`~ansys.grantami.bomanalytics.queries.BomSustainabilitySummaryQuery`.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        results: List[models.GetSustainabilitySummaryForBom2301Response],
        messages: List[models.CommonLogEntry],
    ) -> None:
        super().__init__(messages)
        self._response = results[0]

        transport_summary = _raise_if_unset(self._response.transport_summary)
        self._transport_summary = ItemResultFactory.create_phase_summary(
            _raise_if_unset(transport_summary.phase_summary)
        )

        self._transport_details: List[TransportSummaryResult] = [
            ItemResultFactory.create_transport_summary(transport)
            for transport in _raise_if_unset(transport_summary.summary)
        ]

        material_summary = _raise_if_unset(self._response.material_summary)
        self._material_summary = ItemResultFactory.create_phase_summary(_raise_if_unset(material_summary.phase_summary))

        self._material_details = [
            ItemResultFactory.create_material_summary(material)
            for material in _raise_if_unset(material_summary.summary)
        ]

        process_summary = _raise_if_unset(self._response.process_summary)
        self._process_summary = ItemResultFactory.create_phase_summary(_raise_if_unset(process_summary.phase_summary))

        self._primary_processes_details = [
            ItemResultFactory.create_process_summary(process)
            for process in _raise_if_unset(process_summary.primary_processes)
        ]

        self._secondary_processes_details = [
            ItemResultFactory.create_process_summary(process)
            for process in _raise_if_unset(process_summary.secondary_processes)
        ]

        self._joining_and_finishing_processes_details = [
            ItemResultFactory.create_process_summary(process)
            for process in _raise_if_unset(process_summary.joining_and_finishing_processes)
        ]

    # High level summaries:
    # - provide list of all phases -> allow generic plotting/reporting of all phases indistinctively
    # - provide individual phase summaries -> allow direct access without iterating through all phases

    @property
    def phases_summary(self) -> List[SustainabilityPhaseSummaryResult]:
        """
        Sustainability summary for all lifecycle phases analyzed by the query.
        """
        return [self._material_summary, self._process_summary, self._transport_summary]

    @property
    def transport(self) -> SustainabilityPhaseSummaryResult:
        """
        Sustainability summary for the transport phase.

        Values in percentages express the contribution of this phase, relative to the total contribution of all phases
        analyzed by the query.
        """
        return self._transport_summary

    @property
    def material(self) -> SustainabilityPhaseSummaryResult:
        """
        Sustainability summary for the material phase.

        Values in percentages express the contribution of this phase, relative to the total contribution of all phases
        analyzed by the query.
        """
        return self._material_summary

    @property
    def process(self) -> SustainabilityPhaseSummaryResult:
        """
        Sustainability summary for the process phase.

        Values in percentages express the contribution of this phase, relative to the total contribution of all phases
        analyzed by the query.
        """
        return self._process_summary

    @property
    def transport_details(self) -> List[TransportSummaryResult]:
        """
        Summary information for all transport stages.

        Values in percentages express the contribution of the specific transport stage, relative to contributions of all
        transport stages.
        """
        return self._transport_details

    @property
    def material_details(self) -> List[MaterialSummaryResult]:
        """
        Summary information for materials, aggregated by ``identity``.

        Relative and absolute contributions for materials whose relative contributions exceed 2% of the total impact
        for materials (by :attr:`~.MaterialSummaryResult.embodied_energy_percentage` or
        :attr:`~.MaterialSummaryResult.climate_change_percentage`).

        All materials in the BoM that do not exceed the 2% threshold are aggregated under a virtual
        :class:`.MaterialSummaryResult`, whose :attr:`~.MaterialSummaryResult.identity` property is equal to
        ``Other``.

        Values in percentages express the contribution of the specific material, relative to contributions of all
        materials.
        """
        # TODO: Feature request: it would be nice if threshold could be a request arg
        return self._material_details

    @property
    def primary_processes_details(self) -> List[ProcessSummaryResult]:
        """
        Summary information for primary processes, aggregated by ``process_name`` and ``material_identity``.

        The returned list includes all unique primary process/material combinations whose relative contributions
        exceed 5% of the total impact of all primary processes (by
        :attr:`~.ProcessSummaryResult.embodied_energy_percentage` or
        :attr:`~.ProcessSummaryResult.climate_change_percentage`).

        All process/material combinations that do not exceed the 5% threshold are aggregated under a virtual
        :class:`~.ProcessSummaryResult`, whose :attr:`~.ProcessSummaryResult.process_name` is equal to ``Other``.

        Values in percentages express the contribution of the specific process, relative to contributions of all
        primary processes.
        """
        return self._primary_processes_details

    @property
    def secondary_processes_details(self) -> List[ProcessSummaryResult]:
        """
        Summary information for secondary processes, aggregated by ``process_name`` and ``material_identity``.

        The returned list includes all unique secondary process/material combinations whose relative contributions
        exceed 5% of the total impact of all secondary processes (by
        :attr:`~.ProcessSummaryResult.embodied_energy_percentage` or
        :attr:`~.ProcessSummaryResult.climate_change_percentage`).

        All process/material combinations that do not exceed the 5% threshold are aggregated under a virtual
        :class:`~.ProcessSummaryResult`, whose :attr:`~.ProcessSummaryResult.process_name` is equal to ``Other``.

        Values in percentages express the contribution of the specific process, relative to contributions of all
        secondary processes.
        """
        return self._secondary_processes_details

    @property
    def joining_and_finishing_processes_details(self) -> List[ProcessSummaryResult]:
        """
        Summary information for joining and finishing processes, , aggregated by ``process_name`` and
        ``material_identity``.

        The returned list includes all joining and finishing processes whose relative contributions exceed 5% of the
        total impact of all joining and finishing processes (by
        :attr:`~.ProcessSummaryResult.embodied_energy_percentage` or
        :attr:`~.ProcessSummaryResult.climate_change_percentage`).

        All processes that do not exceed the 5% threshold are aggregated under a virtual
        :class:`~.ProcessSummaryResult`, whose :attr:`~.ProcessSummaryResult.process_name` is equal to ``Other``.

        Values in percentages express the contribution of the specific process, relative to contributions of all
        joining and finishing processes.
        """
        return self._joining_and_finishing_processes_details

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
