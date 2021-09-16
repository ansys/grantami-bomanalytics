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
    result, item_type, **kwargs
):  # TODO: I don't like this function sitting here. # TODO: Switch the signature to item_type, result
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


class ImpactedSubstancesMixin:  # TODO: Think about all the pivots we will want to do on these results
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
                    pass
                    # TODO: Merge Indicators
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
                result=result,
                item_type=MaterialWithImpactedSubstances,
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
    ):
        self._results = [
            instantiate_type(
                result=result,
                item_type=MaterialWithCompliance,
                indicators=result.indicators,
                substances=result.substances,
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
                result=result,
                item_type=PartWithImpactedSubstances,
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
    ):
        self._results = [
            instantiate_type(
                result=result,
                item_type=PartWithCompliance,
                indicators=result.indicators,
                substances=result.substances,
                parts=result.parts,
                materials=result.materials,
                specifications=result.specifications,
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
                result=result,
                item_type=SpecificationWithImpactedSubstances,
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
    ):
        self._results = [
            instantiate_type(
                result=result,
                item_type=SpecificationWithCompliance,
                indicators=result.indicators,
                substances=result.substances,
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
    ):
        self._results = [
            instantiate_type(
                result=result,
                item_type=SubstanceWithCompliance,
                indicators=result.indicators,
            )
            for result in results
        ]

    @property
    def compliance_by_substance_and_indicator(
        self,
    ) -> List[SubstanceWithCompliance,]:
        return self._results


class BoMImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(self, result):
        self._results = [
            BoM1711WithImpactedSubstances(legislations=result.legislations)
        ]


class BoMComplianceResult(ComplianceMixin):
    def __init__(self, result):
        part = result.parts[0]
        obj = PartWithCompliance(
            indicators=part.indicators,
            substances=part.substances,
            parts=part.parts,
            materials=part.materials,
            specifications=part.specifications,
        )
        self._results = [obj]

    @property
    def compliance_by_part_and_indicator(
        self,
    ) -> List[PartWithCompliance,]:
        return self._results
