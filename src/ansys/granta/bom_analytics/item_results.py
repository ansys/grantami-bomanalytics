from typing import List, Dict, Union
from .item_definitions import (
    MaterialDefinition,
    PartDefinition,
    SpecificationDefinition,
    BoM1711Definition,
    BaseSubstanceDefinition,
)
from .indicators import (
    WatchListIndicatorDefinition,
    RoHSIndicatorDefinition,
    WatchListIndicatorResult,
    RoHSIndicatorResult,
    create_indicator_result,
)


class ComplianceResultMixin:
    def __init__(self, indicators=None, substances=None, **kwargs):
        super().__init__(**kwargs)
        if not indicators:
            indicators = []
        indicator_definitions = kwargs.get("indicator_definitions", [])
        self.indicators: Dict[
            str, Union[WatchListIndicatorResult, RoHSIndicatorResult]
        ] = {
            indicator.name: create_indicator_result(indicator, indicator_definitions)
            for indicator in indicators
        }

        if not substances:
            substances = []
        from .query_results import instantiate_type  # TODO: Any way around this import?

        self.substances: List[SubstanceWithCompliance] = [
            instantiate_type(
                item_type=SubstanceWithCompliance,
                result=substance,
                indicators=substance.indicators,
                indicator_definitions=indicator_definitions,
            )
            for substance in substances
        ]


class ImpactedSubstancesResultMixin:
    def __init__(self, legislations=None, **kwargs):
        super().__init__(**kwargs)
        if not legislations:
            legislations = []

        self.legislations: Dict[str, LegislationResult] = {
            legislation.legislation_name: LegislationResult(
                name=legislation.legislation_name,
                substances=legislation.impacted_substances,
            )
            for legislation in legislations
        }


class BomStructureResultMixin:
    def __init__(self, parts=None, materials=None, specifications=None, **kwargs):
        super().__init__(**kwargs)

        from .query_results import instantiate_type  # TODO: Any way around this import?

        if not parts:
            parts = []
        if not materials:
            materials = []
        if not specifications:
            specifications = []

        self.parts: List[PartWithCompliance] = [
            instantiate_type(
                item_type=PartWithCompliance,
                result=part,
                indicators=part.indicators,
                substances=part.substances,
                parts=part.parts,
                materials=part.materials,
                specifications=part.specifications,
                indicator_definitions=kwargs.get("indicator_definitions", []),
            )
            for part in parts
        ]

        self.materials: List[MaterialWithCompliance] = [
            instantiate_type(
                item_type=MaterialWithCompliance,
                result=material,
                indicators=material.indicators,
                substances=material.substances,
                indicator_definitions=kwargs.get("indicator_definitions", []),
            )
            for material in materials
        ]

        self.specifications: List[SpecificationWithCompliance] = [
            instantiate_type(
                item_type=SpecificationWithCompliance,
                result=specification,
                indicators=specification.indicators,
                substances=specification.substances,
                indicator_definitions=kwargs.get("indicator_definitions", []),
            )
            for specification in specifications
        ]


class MaterialWithImpactedSubstances(ImpactedSubstancesResultMixin, MaterialDefinition):
    pass


class MaterialWithCompliance(ComplianceResultMixin, MaterialDefinition):
    pass


class PartWithImpactedSubstances(ImpactedSubstancesResultMixin, PartDefinition):
    pass


class PartWithCompliance(
    ComplianceResultMixin, BomStructureResultMixin, PartDefinition
):
    pass


class SpecificationWithImpactedSubstances(
    ImpactedSubstancesResultMixin, SpecificationDefinition
):
    pass


class SpecificationWithCompliance(ComplianceResultMixin, SpecificationDefinition):
    pass


class BoM1711WithImpactedSubstances(ImpactedSubstancesResultMixin, BoM1711Definition):
    pass


class BoM1711WithCompliance(
    ComplianceResultMixin, BomStructureResultMixin, BoM1711Definition
):
    pass


class SubstanceWithCompliance(BaseSubstanceDefinition):
    def __init__(
        self,
        chemical_name: str = None,
        cas_number: str = None,
        ec_number: str = None,
        record_history_identity: int = None,
        record_guid: str = None,
        record_history_guid: str = None,
        indicators: List = None,
        indicator_definitions: List[
            Union[WatchListIndicatorDefinition, RoHSIndicatorDefinition]
        ] = None,
    ):
        super().__init__(
            chemical_name,
            cas_number,
            ec_number,
            record_history_identity,
            record_guid,
            record_history_guid,
        )
        if not indicators:
            indicators = []
        if not indicator_definitions:
            indicator_definitions = []
        self.indicators: Dict[
            str, Union[WatchListIndicatorResult, RoHSIndicatorResult]
        ] = {
            indicator.name: create_indicator_result(indicator, indicator_definitions)
            for indicator in indicators
        }


class SubstanceWithAmounts(BaseSubstanceDefinition):
    def __init__(
        self,
        chemical_name: str = None,
        cas_number: str = None,
        ec_number: str = None,
        record_history_identity: int = None,
        record_guid: str = None,
        record_history_guid: str = None,
        max_percentage_amount_in_material: float = None,
        legislation_threshold: float = None,
    ):
        super().__init__(
            chemical_name,
            cas_number,
            ec_number,
            record_history_identity,
            record_guid,
            record_history_guid,
        )
        self.max_percentage_amount_in_material = max_percentage_amount_in_material
        self.legislation_threshold = legislation_threshold


class LegislationResult:
    def __init__(self, name: str, substances=None):
        self.name: str = name

        if not substances:
            substances = []

        self.substances: List[SubstanceWithAmounts] = [
            SubstanceWithAmounts(
                chemical_name=substance.substance_name,
                cas_number=substance.cas_number,
                ec_number=substance.ec_number,
                max_percentage_amount_in_material=substance.max_percentage_amount_in_material,  # noqa: E501
                legislation_threshold=substance.legislation_threshold,
            )
            for substance in substances
        ]
