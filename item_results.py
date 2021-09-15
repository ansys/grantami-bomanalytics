from typing import List, Union
from ansys.granta.bomanalytics import models
from item_definitions import (MaterialDefinition,
                              PartDefinition,
                              SpecificationDefinition,
                              BoM1711Definition,
                              BaseSubstanceDefinition)


class ComplianceResultMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.indicators = {}
        self.substances = []

    def add_compliance(self, indicators: List, substances: List):
        from query_results import instantiate_type

        self.indicators = {indicator.name: IndicatorResult(indicator.name, indicator.flag)
                           for indicator in indicators}
        for substance in substances:
            new_substance = instantiate_type(substance, SubstanceWithCompliance)
            new_substance.add_compliance(substance.indicators)
            self.substances.append(new_substance)


class ImpactedSubstancesResultMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.legislations = {}

    def add_legislations(self, legislations: List):
        for legislation in legislations:
            new_legislation_name = legislation.legislation_name
            new_legislation = LegislationResult(new_legislation_name)
            new_legislation.add_substances(legislation.impacted_substances)
            self.legislations[new_legislation_name] = new_legislation


class BomStructureResultMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parts = []
        self.materials = []
        self.specifications = []
        self.substances = []

    def add_parts(self, parts: List):
        from query_results import instantiate_type

        for part in parts:
            new_part = instantiate_type(part, PartWithCompliance)
            new_part.add_parts(part.parts)
            new_part.add_materials(part.materials)
            new_part.add_specifications(part.specifications)
            new_part.add_compliance(indicators=part.indicators, substances=part.substances)
            self.parts.append(new_part)

    def add_materials(self, materials: List):
        from query_results import instantiate_type
        for material in materials:
            new_material = instantiate_type(material, MaterialWithCompliance)
            new_material.add_compliance(indicators=material.indicators, substances=material.substances)
            self.materials.append(new_material)

    def add_specifications(self, specifications: List):
        from query_results import instantiate_type
        for specification in specifications:
            new_spec = instantiate_type(specification, SpecificationWithCompliance)
            new_spec.add_compliance(indicators=specification.indicators, substances=specification.substances)
            self.materials.append(new_spec)


class MaterialWithImpactedSubstances(MaterialDefinition, ImpactedSubstancesResultMixin):
    pass


class MaterialWithCompliance(MaterialDefinition, ComplianceResultMixin):
    pass


class PartWithImpactedSubstances(PartDefinition, ImpactedSubstancesResultMixin):
    pass


class PartWithCompliance(PartDefinition, ComplianceResultMixin, BomStructureResultMixin):
    pass


class SpecificationWithImpactedSubstances(SpecificationDefinition, ImpactedSubstancesResultMixin):
    pass


class SpecificationWithCompliance(SpecificationDefinition, ComplianceResultMixin):
    pass


class BoM1711WithImpactedSubstances(BoM1711Definition, ImpactedSubstancesResultMixin):
    pass


class BoM1711WithCompliance(BoM1711Definition, ComplianceResultMixin, BomStructureResultMixin):
    pass


class SubstanceWithCompliance(BaseSubstanceDefinition):
    def __init__(self, substance_name=None,
                 cas_number=None,
                 ec_number=None,
                 record_history_identity=None,
                 record_guid=None,
                 record_history_guid=None):
        super().__init__(substance_name, cas_number, ec_number, record_history_identity, record_guid, record_history_guid)
        self.indicators = {}

    def add_compliance(self, indicators: List):
        self.indicators = {indicator.name: IndicatorResult(indicator.name, indicator.flag) for indicator in indicators}


class SubstanceWithAmounts(BaseSubstanceDefinition):
    def __init__(self, substance_name=None,
                 cas_number=None,
                 ec_number=None,
                 record_history_identity=None,
                 record_guid=None,
                 record_history_guid=None,
                 max_percentage_amount_in_material=None,
                 legislation_threshold=None):
        super().__init__(substance_name, cas_number, ec_number, record_history_identity, record_guid, record_history_guid)
        self.max_percentage_amount_in_material = max_percentage_amount_in_material
        self.legislation_threshold = legislation_threshold


class LegislationResult:
    def __init__(self, name: str):
        self.name = name
        self.substances = []

    def add_substances(self, substances):
        for substance in substances:
            new_substance = SubstanceWithAmounts(substance_name=substance.substance_name,
                                                 cas_number=substance.cas_number,
                                                 ec_number=substance.ec_number,
                                                 max_percentage_amount_in_material=substance.max_percentage_amount_in_material,
                                                 legislation_threshold=substance.legislation_threshold)
            self.substances.append(new_substance)



class IndicatorResult:
    def __init__(self, name, result):
        self.name = name
        self.result = result