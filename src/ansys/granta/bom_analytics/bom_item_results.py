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
    def create_record_result(cls, name: str, result, **kwargs):
        try:
            item_result_class = cls.registry[name]
        except KeyError:
            raise RuntimeError(f"Unregistered result object {name}")
        id_kwargs = cls.generate_kwarg(result)
        kwargs = dict(**id_kwargs, **kwargs)
        item_result = item_result_class(**kwargs)
        return item_result

    @staticmethod
    def generate_kwarg(result) -> Dict[str, Union[str, int]]:
        if result.reference_type == "MaterialId":
            return dict(material_id=result.reference_value)
        elif result.reference_type == "PartNumber":
            return dict(part_number=result.reference_value)
        elif result.reference_type == "SpecificationId":
            return dict(specification_id=result.reference_value)
        elif result.reference_type == "CasNumber":
            return dict(cas_number=result.reference_value)
        elif result.reference_type == "EcNumber":
            return dict(ec_number=result.reference_value)
        elif result.reference_type == "SubstanceName":
            return dict(chemical_name=result.reference_value)
        elif result.reference_type == "MiRecordHistoryIdentity":
            return dict(record_history_identity=int(result.reference_value))
        elif result.reference_type == "MiRecordGuid":
            return dict(record_guid=result.reference_value)
        elif result.reference_type == "MiRecordHistoryGuid":
            return dict(record_history_guid=result.reference_value)
        raise RuntimeError(f"Unknown reference type {result.reference_type}")


class ComplianceResultMixin:
    def __init__(
        self,
        indicator_results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult
        ],
        indicator_definitions: Dict[str, Union[WatchListIndicator, RoHSIndicator]],
        substances_with_compliance: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
        ],
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.indicators: Dict[str, Union[WatchListIndicator, RoHSIndicator]] = copy(
            indicator_definitions
        )
        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag

        self.substances: List[SubstanceWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="substanceWithCompliance",
                result=substance,
                indicator_results=substance.indicators,
                indicator_definitions=indicator_definitions,
            )
            for substance in substances_with_compliance
        ]


class ImpactedSubstancesResultMixin:
    def __init__(
        self,
        legislations: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances
        ],
        **kwargs,
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
        child_parts: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance
        ],
        child_materials: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance
        ],
        child_specifications: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance
        ],
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.parts: List[PartWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="partWithCompliance",
                result=part,
                indicator_results=part.indicators,
                indicator_definitions=kwargs.get("indicator_definitions", []),
                substances_with_compliance=part.substances,
                child_parts=part.parts,
                child_materials=part.materials,
                child_specifications=part.specifications,
            )
            for part in child_parts
        ]

        self.materials: List[MaterialWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="materialWithCompliance",
                result=material,
                indicator_results=material.indicators,
                indicator_definitions=kwargs.get("indicator_definitions", []),
                substances_with_compliance=material.substances,
            )
            for material in child_materials
        ]

        self.specifications: List[SpecificationWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="specificationWithCompliance",
                result=specification,
                indicator_results=specification.indicators,
                indicator_definitions=kwargs.get("indicator_definitions", []),
                substances_with_compliance=specification.substances,
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
class PartWithCompliance(
    BomStructureResultMixin, ComplianceResultMixin, PartDefinition
):
    pass


@BomItemResultFactory.register("specificationWithImpactedSubstances")
class SpecificationWithImpactedSubstances(
    ImpactedSubstancesResultMixin, SpecificationDefinition
):
    pass


@BomItemResultFactory.register("specificationWithCompliance")
class SpecificationWithCompliance(ComplianceResultMixin, SpecificationDefinition):
    pass


@BomItemResultFactory.register("bom1711WithImpactedSubstances")
class BoM1711WithImpactedSubstances(ImpactedSubstancesResultMixin, BoM1711Definition):
    pass


@BomItemResultFactory.register("bom1711WithCompliance")
class BoM1711WithCompliance(
    BomStructureResultMixin, ComplianceResultMixin, BoM1711Definition
):
    pass


@BomItemResultFactory.register("substanceWithCompliance")
class SubstanceWithCompliance(BaseSubstanceDefinition):
    def __init__(
        self,
        indicator_results: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult
        ],
        indicator_definitions: Dict[str, Union[WatchListIndicator, RoHSIndicator]],
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not indicator_results:
            indicator_results = []
        self.indicators: Dict[str, Union[WatchListIndicator, RoHSIndicator]] = copy(
            indicator_definitions
        )
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
        impacted_substances: List[
            models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance
        ],
    ):
        self.name: str = name
        self.substances: List[ImpactedSubstance] = [
            ImpactedSubstance(
                chemical_name=substance.substance_name,
                cas_number=substance.cas_number,
                ec_number=substance.ec_number,
                max_percentage_amount_in_material=substance.max_percentage_amount_in_material,  # noqa: E501
                legislation_threshold=substance.legislation_threshold,
            )
            for substance in impacted_substances
        ]
