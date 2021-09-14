from typing import List, Union
from ansys.granta.bomanalytics import models
from item_definitions import (MaterialDefinition,
                              PartDefinition,
                              SpecificationDefinition,
                              BoM1711Definition,
                              SubstanceDefinition)


class ComplianceResultMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.indicators = {}
        self.substances = []

    def add_compliance(self, indicators: List, substances: List):
        self.indicators = {indicator.name: IndicatorResult(indicator.name, indicator.flag)
                           for indicator in indicators}
        self.substances = [SubstanceResult(substance.reference_value, substance.indicators) for substance in substances]


class ImpactedSubstancesResultMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.legislations = {}

    def add_substances(self, legislations: Union[List, None] = None):
        self.legislations = {legislation.legislation_name: LegislationResult(legislation.legislation_name, legislation.impacted_substances) for
                         legislation in legislations}


class MaterialResult(MaterialDefinition, ComplianceResultMixin, ImpactedSubstancesResultMixin):
    pass


class PartResult(PartDefinition, ComplianceResultMixin, ImpactedSubstancesResultMixin):
    pass


class SpecificationResult(SpecificationDefinition, ComplianceResultMixin, ImpactedSubstancesResultMixin):
    pass


class BoM1711Result(BoM1711Definition, ComplianceResultMixin, ImpactedSubstancesResultMixin):
    pass


class SubstanceResult(SubstanceDefinition):
    def __init__(self, substance_name=None,
                 cas_number=None,
                 ec_number=None,
                 record_history_identity=None,
                 record_guid=None,
                 record_history_guid=None,
                 percentage_amount=None,
                 max_percentage_amount_in_material=None,
                 legislation_threshold=None):
        super().__init__(substance_name, cas_number, ec_number, record_history_identity, record_guid, record_history_guid, percentage_amount)
        self.max_percentage_amount_in_material = max_percentage_amount_in_material
        self.legislation_threshold = legislation_threshold
        self.indicators = {}
        self.substance = None

    def add_compliance(self, indicators: List):
        self.indicators = {indicator.name: IndicatorResult(indicator.name, indicator.flag) for indicator in indicators}


class LegislationResult:
    def __init__(self, name: str, substances: List[Union[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance,
                                                         models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance]]):
        self.name = name
        self.substances = [SubstanceResult(**substance.to_dict()) for substance in substances]



class IndicatorResult:
    def __init__(self, name, result):
        self.name = name
        self.result = result