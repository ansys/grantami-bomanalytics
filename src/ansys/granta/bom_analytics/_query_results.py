from typing import List, Dict, Type, Callable, Any, Union
from collections import defaultdict
from abc import ABC

from ansys.granta.bomanalytics import models

from ._bom_item_results import ItemResultFactory

# Required for type hinting
from ._bom_item_results import (
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
from .indicators import Indicator_Definitions


class QueryResultFactory:
    registry = {}

    @classmethod
    def register(cls, response_type: Type[models.Model]) -> Callable:
        def inner(item_factory: Any) -> Any:
            cls.registry[response_type] = item_factory
            return item_factory

        return inner

    @classmethod
    def create_result(
        cls, response_type: Type[models.Model], **kwargs
    ) -> Union["ImpactedSubstancesBaseClass", "ComplianceBaseClass"]:
        try:
            item_factory_class = cls.registry[response_type]
        except KeyError as e:
            raise RuntimeError(f'Unregistered response type "{response_type}"').with_traceback(e.__traceback__)

        return item_factory_class(**kwargs)


class ImpactedSubstancesBaseClass(ABC):
    _results = []

    @property
    def impacted_substances_by_legislation(
        self,
    ) -> Dict[str, List[ImpactedSubstance]]:
        results = defaultdict(list)
        for item_result in self._results:
            for (
                legislation_name,
                legislation_result,
            ) in item_result.legislations.items():
                results[legislation_name].extend(legislation_result.substances)
        return results

    @property
    def impacted_substances(self) -> List[ImpactedSubstance]:
        results = []
        for item_result in self._results:
            for legislation_result in item_result.legislations.values():
                results.extend(
                    legislation_result.substances
                )  # TODO: Merge these property, i.e. take max amount? range?
        return results


class ComplianceBaseClass(ABC):
    _results = []

    @property
    def compliance_by_indicator(self) -> Indicator_Definitions:
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
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial  # noqa: E501
        ],
    ):
        self._results = []
        for result in results:
            material_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name="materialWithImpactedSubstances",
                result_with_impacted_substances=result,
            )
            self._results.append(material_with_impacted_substances)

    @property
    def impacted_substances_by_material_and_legislation(
        self,
    ) -> List[MaterialWithImpactedSubstancesResult]:
        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance)
class MaterialComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = []
        for result in results:
            material_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="materialWithCompliance",
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            material_with_compliance._add_child_substances(result.substances)
            self._results.append(material_with_compliance)

    @property
    def compliance_by_material_and_indicator(
        self,
    ) -> List[MaterialWithComplianceResult]:
        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart)
class PartImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart],
    ):
        self._results = []
        for result in results:
            part_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name="partWithImpactedSubstances",
                result_with_impacted_substances=result,
            )
            self._results.append(part_with_impacted_substances)

    @property
    def impacted_substances_by_part_and_legislation(
        self,
    ) -> List[PartWithImpactedSubstancesResult]:
        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance)
class PartComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = []
        for result in results:
            part_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="partWithCompliance",
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            part_with_compliance._add_child_parts(result.parts)
            part_with_compliance._add_child_materials(result.materials)
            part_with_compliance._add_child_specifications(result.specifications)
            part_with_compliance._add_child_substances(result.substances)
            self._results.append(part_with_compliance)

    @property
    def compliance_by_part_and_indicator(
        self,
    ) -> List[PartWithComplianceResult]:
        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification
)
class SpecificationImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification  # noqa: E501
        ],
    ):
        self._results = []
        for result in results:
            specification_with_impacted_substances = ItemResultFactory.create_impacted_substances_result(
                result_type_name="specificationWithImpactedSubstances",
                result_with_impacted_substances=result,
            )
            self._results.append(specification_with_impacted_substances)

    @property
    def impacted_substances_by_specification_and_legislation(
        self,
    ) -> List[SpecificationWithImpactedSubstancesResult]:
        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance)
class SpecificationComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = []
        for result in results:
            specification_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="specificationWithCompliance",
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
    ) -> List[SpecificationWithComplianceResult]:
        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance)
class SubstanceComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        indicator_definitions: Indicator_Definitions,
    ):
        self._results = []
        for result in results:
            substance_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="substanceWithCompliance",
                result_with_compliance=result,
                indicator_definitions=indicator_definitions,
            )
            self._results.append(substance_with_compliance)

    @property
    def compliance_by_substance_and_indicator(
        self,
    ) -> List[SubstanceWithComplianceResult]:
        return self._results


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response)
class BomImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    def __init__(self, results):
        self._results = [BoM1711WithImpactedSubstancesResult(legislations=results.legislations)]


@QueryResultFactory.register(models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response)
class BomComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results,
        indicator_definitions: Indicator_Definitions,
    ):
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

    @property
    def compliance_by_part_and_indicator(
        self,
    ) -> List[PartWithComplianceResult]:
        return self._results
