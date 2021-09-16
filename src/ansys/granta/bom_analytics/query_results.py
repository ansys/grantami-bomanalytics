from typing import List, Dict
from collections import defaultdict

from ansys.granta.bomanalytics import models

from .item_results import (
    MaterialWithImpactedSubstances,
    MaterialWithCompliance,
    PartWithImpactedSubstances,
    PartWithCompliance,
    SpecificationWithImpactedSubstances,
    SpecificationWithCompliance,
    SubstanceWithCompliance,
    SubstanceWithAmounts,
    BoM1711WithImpactedSubstances,
)


def instantiate_type(
    item_type, result, **kwargs
):  # TODO: I don't like this function sitting here
    if result.reference_type == "MaterialId":
        obj = item_type(material_id=result.reference_value, **kwargs)
    elif result.reference_type == "PartNumber":
        obj = item_type(part_number=result.reference_value, **kwargs)
    elif result.reference_type == "SpecificationId":
        obj = item_type(specification_id=result.reference_value, **kwargs)
    elif result.reference_type == "CasNumber":
        obj = item_type(cas_number=result.reference_value, **kwargs)
    elif result.reference_type == "EcNumber":
        obj = item_type(ec_number=result.reference_value, **kwargs)
    elif result.reference_type == "SubstanceName":
        obj = item_type(chemical_name=result.reference_value, **kwargs)
    elif result.reference_type == "MiRecordHistoryIdentity":
        obj = item_type(record_history_identity=int(result.reference_value), **kwargs)
    elif result.reference_type == "MiRecordGuid":
        obj = item_type(record_guid=result.reference_value, **kwargs)
    elif result.reference_type == "MiRecordHistoryGuid":
        obj = item_type(record_history_guid=result.reference_value, **kwargs)
    else:
        raise RuntimeError(f"Unknown reference type {result.reference_type}")
    return obj


class ImpactedSubstancesMixin:
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


class ComplianceMixin:  # TODO: Think about all the pivots we will want to do on these results
    _results = []

    @property
    def compliance_by_indicator(self) -> Dict[str, str]:
        results = {}
        for result in self._results:
            for indicator_name, indicator_result in result.indicators.items():
                if indicator_name not in results:
                    results[indicator_name] = indicator_result
                else:
                    if indicator_result.flag > results[indicator_name].flag:
                        results[indicator_name] = indicator_result
        return results


class MaterialImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial  # noqa: E501
        ],
    ):
        self._results = [
            instantiate_type(
                item_type=MaterialWithImpactedSubstances,
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


class MaterialComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            instantiate_type(
                item_type=MaterialWithCompliance,
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


class PartImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart
        ],
    ):
        self._results = [
            instantiate_type(
                item_type=PartWithImpactedSubstances,
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


class PartComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            instantiate_type(
                item_type=PartWithCompliance,
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


class SpecificationImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification  # noqa: E501
        ],
    ):
        self._results = [
            instantiate_type(
                item_type=SpecificationWithImpactedSubstances,
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


class SpecificationComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            instantiate_type(
                item_type=SpecificationWithCompliance,
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


class SubstanceComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
        ],
        indicator_definitions: List,
    ):
        self._results = [
            instantiate_type(
                item_type=SubstanceWithCompliance,
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


class BoMImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(self, result):
        self._results = [
            BoM1711WithImpactedSubstances(legislations=result.legislations)
        ]


class BoMComplianceResult(ComplianceMixin):
    def __init__(
        self,
        result,
        indicator_definitions: List,
    ):
        part = result.parts[0]
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
    ) -> List[PartWithCompliance,]:
        return self._results
