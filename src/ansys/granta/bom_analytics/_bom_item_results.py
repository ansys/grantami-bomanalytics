from typing import List, Dict, Union, Callable
from copy import copy
from ansys.granta.bomanalytics import models
from ._bom_item_definitions import (
    MaterialDefinition,
    PartDefinition,
    SpecificationDefinition,
    BoM1711Definition,
    BaseSubstanceReference,
    RecordDefinition,
    ReferenceType,
    CoatingDefinition,
)
from .indicators import Indicator_Definitions


class BomItemResultFactory:
    registry = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def inner(result_class: RecordDefinition) -> RecordDefinition:
            cls.registry[name] = result_class
            return result_class

        return inner

    @classmethod
    def create_record_result(cls, name: str, reference_type: Union[str, None], **kwargs):
        try:
            item_result_class = cls.registry[name]
        except KeyError:
            raise RuntimeError(f"Unregistered result object {name}")

        reference_type = cls.parse_reference_type(reference_type)
        item_result = item_result_class(reference_type=reference_type, **kwargs)
        return item_result

    @staticmethod
    def parse_reference_type(reference_type: str) -> str:
        try:
            return ReferenceType[reference_type]
        except KeyError as e:
            raise KeyError(f"Unknown reference_type {reference_type} returned.").with_traceback(e.__traceback__)


class ComplianceResultMixin:
    def __init__(
        self,
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Indicator_Definitions,
        child_substances: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        **kwargs,  # Contains record reference for non-Bom queries
    ):
        super().__init__(**kwargs)

        self.indicators: Indicator_Definitions = copy(indicator_definitions)
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
            for substance in child_substances
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
        child_materials: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
        child_specifications: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
        child_substances: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Indicator_Definitions,
        **kwargs,  # Contains record reference for non-Bom queries
    ):
        super().__init__(indicator_results, indicator_definitions, child_substances, **kwargs)

        self.materials: List[MaterialWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="materialWithCompliance",
                indicator_results=material.indicators,
                indicator_definitions=indicator_definitions,
                child_substances=material.substances,
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
                child_materials=specification.materials,
                child_specifications=specification.specifications,
                child_coatings=specification.coatings,
                child_substances=specification.substances,
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
    def __init__(
        self,
        child_parts: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
        indicator_definitions: Indicator_Definitions,
        **kwargs,  # Contains common bom items and record reference for non-Bom queries
    ):
        super().__init__(indicator_definitions=indicator_definitions, **kwargs)

        self.parts: List[PartWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="partWithCompliance",
                indicator_results=part.indicators,
                indicator_definitions=indicator_definitions,
                child_parts=part.parts,
                child_materials=part.materials,
                child_specifications=part.specifications,
                child_substances=part.substances,
                reference_type=part.reference_type,
                reference_value=part.reference_value,
            )
            for part in child_parts
        ]


@BomItemResultFactory.register("specificationWithImpactedSubstances")
class SpecificationWithImpactedSubstances(ImpactedSubstancesResultMixin, SpecificationDefinition):
    pass


@BomItemResultFactory.register("specificationWithCompliance")
class SpecificationWithCompliance(BomStructureResultMixin, ComplianceResultMixin, SpecificationDefinition):
    def __init__(
        self,
        child_coatings: List[models.GrantaBomAnalyticsServicesInterfaceCommonCoatingWithCompliance],
        indicator_definitions: Indicator_Definitions,
        **kwargs,  # Contains common bom items and record reference for non-Bom queries
    ):
        super().__init__(indicator_definitions=indicator_definitions, **kwargs)

        self.coatings: List[CoatingWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="coatingWithCompliance",
                indicator_results=coating.indicators,
                indicator_definitions=indicator_definitions,
                child_substances=coating.substances,
                reference_type=coating.reference_type,
                reference_value=coating.reference_value,
            )
            for coating in child_coatings
        ]


@BomItemResultFactory.register("coatingWithCompliance")
class CoatingWithCompliance(ComplianceResultMixin, CoatingDefinition):
    pass


@BomItemResultFactory.register("bom1711WithImpactedSubstances")
class BoM1711WithImpactedSubstances(ImpactedSubstancesResultMixin, BoM1711Definition):
    pass


@BomItemResultFactory.register("bom1711WithCompliance")
class BoM1711WithCompliance(BomStructureResultMixin, ComplianceResultMixin, BoM1711Definition):
    pass


@BomItemResultFactory.register("substanceWithCompliance")
class SubstanceWithCompliance(BaseSubstanceReference):
    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Indicator_Definitions,
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        if not indicator_results:
            indicator_results = []
        self.indicators: Indicator_Definitions = copy(indicator_definitions)
        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag


class ImpactedSubstance(BaseSubstanceReference):
    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
        max_percentage_amount_in_material: float,
        legislation_threshold: float,
    ):
        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
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
            if substance.cas_number:
                reference_type = ReferenceType.CasNumber
                reference_value = substance.cas_number
            elif substance.ec_number:
                reference_type = ReferenceType.EcNumber
                reference_value = substance.ec_number
            elif substance.substance_name:
                reference_type = ReferenceType.ChemicalName
                reference_value = substance.substance_name
            else:
                raise RuntimeError(
                    "Substance result returned from Granta MI has no reference. Ensure any substances "
                    "in your request include references, and check you are using an up-to-date version"
                    " of the base bom analytics package."
                )
            impacted_substance = ImpactedSubstance(
                max_percentage_amount_in_material=substance.max_percentage_amount_in_material,  # noqa: E501
                legislation_threshold=substance.legislation_threshold,
                reference_type=reference_type,
                reference_value=reference_value,
            )
            impacted_substance.ec_number = substance.ec_number
            impacted_substance.cas_number = substance.cas_number
            impacted_substance.chemical_name = substance.substance_name
            self.substances.append(impacted_substance)
