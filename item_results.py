from item_definitions import (
    MaterialDefinition,
    PartDefinition,
    SpecificationDefinition,
    BoM1711Definition,
    BaseSubstanceDefinition,
)


class ComplianceResultMixin:
    def __init__(self, indicators=None, substances=None, **kwargs):
        super().__init__(**kwargs)
        if not indicators:
            indicators = []
        self.indicators = {
            indicator.name: IndicatorResult(indicator.name, indicator.flag)
            for indicator in indicators
        }

        if not substances:
            substances = []

        from query_results import instantiate_type

        self.substances = [
            instantiate_type(
                result=substance,
                item_type=SubstanceWithCompliance,
                indicators=substance.indicators,
            )
            for substance in substances
        ]


class ImpactedSubstancesResultMixin:
    def __init__(self, legislations=None, **kwargs):
        super().__init__(**kwargs)
        if not legislations:
            legislations = []

        self.legislations = {}
        for legislation in legislations:
            new_legislation_name = legislation.legislation_name
            new_legislation = LegislationResult(new_legislation_name)
            new_legislation.add_substances(legislation.impacted_substances)
            self.legislations[new_legislation_name] = new_legislation


class BomStructureResultMixin:
    def __init__(self, parts=None, materials=None, specifications=None, **kwargs):
        super().__init__(**kwargs)

        from query_results import instantiate_type

        self.parts = []
        if not parts:
            parts = []
        for part in parts:
            new_part = instantiate_type(
                result=part,
                item_type=PartWithCompliance,
                indicators=part.indicators,
                substances=part.substances,
                parts=part.parts,
                materials=part.materials,
                specifications=part.specifications,
            )
            self.parts.append(new_part)

        self.materials = []
        if not materials:
            materials = []
        for material in materials:
            new_material = instantiate_type(
                result=material,
                item_type=MaterialWithCompliance,
                indicators=material.indicators,
                substances=material.substances,
            )
            self.materials.append(new_material)

        self.specifications = []
        if not specifications:
            specifications = []
        for specification in specifications:
            new_spec = instantiate_type(
                result=specification,
                item_type=SpecificationWithCompliance,
                indicators=specification.indicators,
                substances=specification.substances,
            )
            self.materials.append(new_spec)


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
        substance_name=None,
        cas_number=None,
        ec_number=None,
        record_history_identity=None,
        record_guid=None,
        record_history_guid=None,
        indicators=None,
    ):
        super().__init__(
            substance_name,
            cas_number,
            ec_number,
            record_history_identity,
            record_guid,
            record_history_guid,
        )
        if not indicators:
            indicators = []
        self.indicators = {
            indicator.name: IndicatorResult(indicator.name, indicator.flag)
            for indicator in indicators
        }


class SubstanceWithAmounts(BaseSubstanceDefinition):
    def __init__(
        self,
        substance_name=None,
        cas_number=None,
        ec_number=None,
        record_history_identity=None,
        record_guid=None,
        record_history_guid=None,
        max_percentage_amount_in_material=None,
        legislation_threshold=None,
    ):
        super().__init__(
            substance_name,
            cas_number,
            ec_number,
            record_history_identity,
            record_guid,
            record_history_guid,
        )
        self.max_percentage_amount_in_material = max_percentage_amount_in_material
        self.legislation_threshold = legislation_threshold


class LegislationResult:
    def __init__(self, name: str):
        self.name = name
        self.substances = []

    def add_substances(self, substances):
        for substance in substances:
            new_substance = SubstanceWithAmounts(
                substance_name=substance.substance_name,
                cas_number=substance.cas_number,
                ec_number=substance.ec_number,
                max_percentage_amount_in_material=substance.max_percentage_amount_in_material,
                legislation_threshold=substance.legislation_threshold,
            )
            self.substances.append(new_substance)


class IndicatorResult:
    def __init__(self, name, result):
        self.name = name
        self.result = result
