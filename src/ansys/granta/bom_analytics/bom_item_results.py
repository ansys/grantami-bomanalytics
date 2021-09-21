from typing import List, Dict, Union, Callable
from copy import copy
from ansys.granta.bomanalytics import models
from .bom_item_definitions import (
    MaterialDefinition,
    PartDefinition,
    SpecificationDefinition,
    BoM1711Definition,
    BaseSubstanceDefinition,
    RecordDefinition,
)
from .bom_indicators import (
    WatchListIndicator,
    RoHSIndicator,
)


class BomItemResultFactory:
    registry = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner(result_class: RecordDefinition) -> RecordDefinition:
            cls.registry[name] = result_class
            return result_class

        return inner

    @classmethod
    def create_record_result(cls, name: str, **kwargs):
        try:
            item_result_class = cls.registry[name]
        except KeyError:
            raise RuntimeError(f"Unregistered result object {name}")
        item_result = item_result_class(**kwargs)
        return item_result


class ComplianceResultMixin:
    def __init__(
        self,
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Dict[str, Union[WatchListIndicator, RoHSIndicator]],
        substances_with_compliance: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        **kwargs,  # Contains record reference for non-Bom queries
    ):
        super().__init__(**kwargs)

        self.indicators: Dict[str, Union[WatchListIndicator, RoHSIndicator]] = copy(indicator_definitions)
        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag

        self.substances: List[SubstanceWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="substanceWithCompliance",
                indicator_results=substance.indicators,
                indicator_definitions=indicator_definitions,
                reference_type=substance.reference_type,
                reference_value=substance.reference_value,
            )
            for substance in substances_with_compliance
        ]


class ImpactedSubstancesResultMixin:
    def __init__(
        self,
        legislations: List[models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances],
        **kwargs,  # Contains record reference for non-Bom queries
    ):
        super().__init__(**kwargs)

        self.legislations: Dict[str, LegislationResult] = {
            legislation.legislation_name: LegislationResult(
                name=legislation.legislation_name,
                impacted_substances=legislation.impacted_substances,
            )
            for legislation in legislations
        }


class BomStructureResultMixin:
    def __init__(
        self,
        child_parts: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
        child_materials: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
        child_specifications: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Dict[str, Union[WatchListIndicator, RoHSIndicator]],
        substances_with_compliance: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        **kwargs,  # Contains record reference for non-Bom queries
    ):
        super().__init__(indicator_results, indicator_definitions, substances_with_compliance, **kwargs)

        self.parts: List[PartWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="partWithCompliance",
                indicator_results=part.indicators,
                indicator_definitions=indicator_definitions,
                substances_with_compliance=part.substances,
                child_parts=part.parts,
                child_materials=part.materials,
                child_specifications=part.specifications,
                reference_type=part.reference_type,
                reference_value=part.reference_value,
            )
            for part in child_parts
        ]

        self.materials: List[MaterialWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="materialWithCompliance",
                indicator_results=material.indicators,
                indicator_definitions=indicator_definitions,
                substances_with_compliance=material.substances,
                reference_type=material.reference_type,
                reference_value=material.reference_value,
            )
            for material in child_materials
        ]

        self.specifications: List[SpecificationWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="specificationWithCompliance",
                indicator_results=specification.indicators,
                indicator_definitions=indicator_definitions,
                substances_with_compliance=specification.substances,
                reference_type=specification.reference_type,
                reference_value=specification.reference_value,
            )
            for specification in child_specifications
        ]


@BomItemResultFactory.register("materialWithImpactedSubstances")
class MaterialWithImpactedSubstances(ImpactedSubstancesResultMixin, MaterialDefinition):
    pass


@BomItemResultFactory.register("materialWithCompliance")
class MaterialWithCompliance(ComplianceResultMixin, MaterialDefinition):
    pass


@BomItemResultFactory.register("partWithImpactedSubstances")
class PartWithImpactedSubstances(ImpactedSubstancesResultMixin, PartDefinition):
    pass


@BomItemResultFactory.register("partWithCompliance")
class PartWithCompliance(BomStructureResultMixin, ComplianceResultMixin, PartDefinition):
    pass


@BomItemResultFactory.register("specificationWithImpactedSubstances")
class SpecificationWithImpactedSubstances(ImpactedSubstancesResultMixin, SpecificationDefinition):
    pass


@BomItemResultFactory.register("specificationWithCompliance")
class SpecificationWithCompliance(ComplianceResultMixin, SpecificationDefinition):
    pass


@BomItemResultFactory.register("bom1711WithImpactedSubstances")
class BoM1711WithImpactedSubstances(ImpactedSubstancesResultMixin, BoM1711Definition):
    pass


@BomItemResultFactory.register("bom1711WithCompliance")
class BoM1711WithCompliance(BomStructureResultMixin, ComplianceResultMixin, BoM1711Definition):
    pass


@BomItemResultFactory.register("substanceWithCompliance")
class SubstanceWithCompliance(BaseSubstanceDefinition):
    def __init__(
        self,
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Dict[str, Union[WatchListIndicator, RoHSIndicator]],
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not indicator_results:
            indicator_results = []
        self.indicators: Dict[str, Union[WatchListIndicator, RoHSIndicator]] = copy(indicator_definitions)
        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag


class ImpactedSubstance(BaseSubstanceDefinition):
    def __init__(
        self,
        max_percentage_amount_in_material: float,
        legislation_threshold: float,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_percentage_amount_in_material = max_percentage_amount_in_material
        self.legislation_threshold = legislation_threshold


class LegislationResult:
    def __init__(
        self,
        name: str,
        impacted_substances: List[models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance],
    ):
        self.name: str = name
        self.substances: List[ImpactedSubstance] = []
        for substance in impacted_substances:
            impacted_substance = ImpactedSubstance(
                max_percentage_amount_in_material=substance.max_percentage_amount_in_material,  # noqa: E501
                legislation_threshold=substance.legislation_threshold,
                reference_type=None,
                reference_value=None,
            )
            impacted_substance.ec_number = substance.ec_number
            impacted_substance.cas_number = substance.cas_number
            impacted_substance.chemical_name = substance.substance_name
            self.substances.append(impacted_substance)
