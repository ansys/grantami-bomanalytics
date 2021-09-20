from typing import List, Dict, Type, Callable, Any, Union
from collections import defaultdict
from abc import ABC

from ansys.granta.bomanalytics import models

from .bom_item_results import BomItemResultFactory

# Required for type hinting
from .bom_item_results import (
    MaterialWithImpactedSubstances,
    MaterialWithCompliance,
    PartWithImpactedSubstances,
    PartWithCompliance,
    SpecificationWithImpactedSubstances,
    SpecificationWithCompliance,
    SubstanceWithCompliance,
    SubstanceWithAmounts,
    BoM1711WithImpactedSubstances,
    WatchListIndicatorResult,
    RoHSIndicatorResult
)


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
            raise RuntimeError(
                f'Unregistered response type "{response_type}"'
            ).with_traceback(e.__traceback__)
        return item_factory_class(**kwargs)


class ImpactedSubstancesBaseClass(ABC):
    _results = []

    @property
    def impacted_substances_by_legislation(
        self,
    ) -> Dict[str, List[SubstanceWithAmounts]]:
        results = defaultdict(list)
        for item_result in self._results:
            for (
                legislation_name,
                legislation_result,
            ) in item_result.legislations.items():
                results[legislation_name].extend(legislation_result.substances)
        return results

    @property
    def impacted_substances(self) -> List[SubstanceWithAmounts]:
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
    def compliance_by_indicator(self) -> Dict[str, Union[WatchListIndicatorResult, RoHSIndicatorResult]]:
        results = {}
        for result in self._results:
            for indicator_name, indicator_result in result.indicators.items():
                if indicator_name not in results:
                    results[indicator_name] = indicator_result
                else:
                    if indicator_result.flag > results[indicator_name].flag:
                        results[indicator_name] = indicator_result
        return results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial
)
class MaterialImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial  # noqa: E501
        ],
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="materialWithImpactedSubstances",
                result=result,
                legislations=result.legislations,
            )
            for result in results
        ]

    @property
    def impacted_substances_by_material_and_legislation(
        self,
    ) -> List[MaterialWithImpactedSubstances]:
        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance
)
class MaterialComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="materialWithCompliance",
                result=result,
                indicators=result.indicators,
                substances=result.substances,
                indicator_definitions=indicator_definitions,
            )
            for result in results
        ]

    @property
    def compliance_by_material_and_indicator(
        self,
    ) -> List[MaterialWithCompliance,]:
        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart
)
class PartImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart
        ],
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="partWithImpactedSubstances",
                result=result,
                legislations=result.legislations,
            )
            for result in results
        ]

    @property
    def impacted_substances_by_part_and_legislation(
        self,
    ) -> List[PartWithImpactedSubstances]:
        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance
)
class PartComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="partWithCompliance",
                result=result,
                indicators=result.indicators,
                substances=result.substances,
                parts=result.parts,
                materials=result.materials,
                specifications=result.specifications,
                indicator_definitions=indicator_definitions,
            )
            for result in results
        ]

    @property
    def compliance_by_part_and_indicator(
        self,
    ) -> List[PartWithCompliance,]:
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
        self._results = [
            BomItemResultFactory.create_record_result(
                name="specificationWithImpactedSubstances",
                result=result,
                legislations=result.legislations,
            )
            for result in results
        ]

    @property
    def impacted_substances_by_specification_and_legislation(
        self,
    ) -> List[SpecificationWithImpactedSubstances]:
        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance
)
class SpecificationComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="specificationWithCompliance",
                result=result,
                indicators=result.indicators,
                substances=result.substances,
                indicator_definitions=indicator_definitions,
            )
            for result in results
        ]

    @property
    def compliance_by_specification_and_indicator(
        self,
    ) -> List[SpecificationWithCompliance,]:
        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
)
class SubstanceComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            BomItemResultFactory.create_record_result(
                name="substanceWithCompliance",
                result=result,
                indicators=result.indicators,
                indicator_definitions=indicator_definitions,
            )
            for result in results
        ]

    @property
    def compliance_by_substance_and_indicator(
        self,
    ) -> List[SubstanceWithCompliance]:
        return self._results


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response
)
class BoMImpactedSubstancesResult(ImpactedSubstancesBaseClass):
    def __init__(self, results):
        self._results = [
            BoM1711WithImpactedSubstances(legislations=results.legislations)
        ]


@QueryResultFactory.register(
    models.GrantaBomAnalyticsServicesInterfaceGetComplianceForBom1711Response
)
class BoMComplianceResult(ComplianceBaseClass):
    def __init__(
        self,
        results,
        indicator_definitions: List,
    ):
        part = results.parts[0]
        obj = PartWithCompliance(
            indicators=part.indicators,
            substances=part.substances,
            parts=part.parts,
            materials=part.materials,
            specifications=part.specifications,
            indicator_definitions=indicator_definitions,
        )
        self._results = [obj]

    @property
    def compliance_by_part_and_indicator(
        self,
    ) -> List[PartWithCompliance]:
        return self._results
