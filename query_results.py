from typing import List
from collections import defaultdict

from ansys.granta.bomanalytics import models

from item_results import (
    MaterialWithImpactedSubstances,
    MaterialWithCompliance,
    PartWithImpactedSubstances,
    PartWithCompliance,
    SpecificationWithImpactedSubstances,
    SpecificationWithCompliance,
    SubstanceWithCompliance,
    BoM1711WithImpactedSubstances,
)


def instantiate_type(result, item_type, **kwargs):
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
        obj = item_type(substance_name=result.reference_value, **kwargs)
    elif result.reference_type == "MiRecordHistoryIdentity":
        obj = item_type(record_history_identity=int(result.reference_value), **kwargs)
    elif result.reference_type == "MiRecordGuid":
        obj = item_type(record_guid=result.reference_value, **kwargs)
    elif result.reference_type == "MiRecordHistoryGuid":
        obj = item_type(record_history_guid=result.reference_value, **kwargs)
    else:
        raise Exception  # TODO: Raise a real exception
    return obj


class ImpactedSubstancesMixin:
    _results = []

    @property
    def impacted_substances_by_legislation(self):
        results = defaultdict(list)
        for item_result in self._results:
            for (
                legislation_name,
                legislation_result,
            ) in item_result.legislations.items():
                results[legislation_name].extend(legislation_result.substances)
        return results

    @property
    def all_impacted_substances(self):
        results = []
        for item_result in self._results:
            for legislation_result in item_result.legislations.values():
                results.extend(
                    legislation_result.substances
                )  # TODO: Merge these property, i.e. take max amount? range?
        return results

    @property
    def impacted_substances(self):
        return self._results


class ComplianceMixin:
    _results = []

    @property
    def compliance_by_indicator(self):
        results = {}
        for result in self._results:
            for indicator_name, indicator_result in result.indicators.items():
                if indicator_name not in results:
                    results[indicator_name] = indicator_result
                else:
                    pass
                    # TODO: Merge Indicators
        return results

    @property
    def compliance(self):
        return self._results


class MaterialImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial
        ],
    ):
        self._results = []
        for result in results:
            obj = instantiate_type(
                result=result,
                item_type=MaterialWithImpactedSubstances,
                legislations=result.legislations,
            )
            self._results.append(obj)


class MaterialComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance
        ],
    ):
        self._results = []
        for result in results:
            obj = instantiate_type(
                result=result,
                item_type=MaterialWithCompliance,
                indicators=result.indicators,
                substances=result.substances,
            )
            self._results.append(obj)


class PartImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart
        ],
    ):
        self._results = []

        for result in results:
            obj = instantiate_type(
                result=result,
                item_type=PartWithImpactedSubstances,
                legislations=result.legislations,
            )
            self._results.append(obj)


class PartComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance
        ],
    ):
        self._results = []
        for result in results:
            obj = instantiate_type(
                result=result,
                item_type=PartWithCompliance,
                indicators=result.indicators,
                substances=result.substances,
                parts=result.parts,
                materials=result.materials,
                specifications=result.specifications,
            )
            self._results.append(obj)


class SpecificationImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification
        ],
    ):
        self._results = []
        for result in results:
            obj = instantiate_type(
                result=result,
                item_type=SpecificationWithImpactedSubstances,
                legislations=result.legislations,
            )
            self._results.append(obj)


class SpecificationComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance
        ],
    ):
        self._results = []
        for result in results:
            obj = instantiate_type(
                result=result,
                item_type=SpecificationWithCompliance,
                indicators=result.indicators,
                substances=result.substances,
            )
            self._results.append(obj)


class SubstanceComplianceResult(ComplianceMixin):
    def __init__(
        self,
        results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
        ],
    ):
        self._results = []
        for result in results:
            obj = instantiate_type(
                result=result,
                item_type=SubstanceWithCompliance,
                indicators=result.indicators,
            )
            self._results.append(obj)


class BoMImpactedSubstancesResult(ImpactedSubstancesMixin):
    def __init__(self, result):
        self._results = [
            BoM1711WithImpactedSubstances(legislations=result.legislations)
        ]


class BoMComplianceResult(ComplianceMixin):
    def __init__(self, result):
        part = result.parts[0]
        obj = PartWithCompliance(indicators=part.indicators,
                                 substances=part.substances,
                                 parts=part.parts,
                                 materials=part.materials,
                                 specifications=part.specifications)
        self._results = [obj]
