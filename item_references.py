from abc import ABC, abstractmethod
from typing import Union, List, Dict

from ansys.granta import bomanalytics
from ansys.granta.bomanalytics.models import Model
from ansys.granta.bomanalytics import models

from indicators import IndicatorResult


class ItemReference(ABC):
    @property
    @abstractmethod
    def definition(self) -> str:
        pass


class ComplianceResultMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.indicators = {}
        self.substances = []

    def add_compliance(self,
                       indicators: Union[List, None],
                       indicator_definitions: Union[List, None],
                       substances: Union[List, None] = None):
        id_def_lookup = {id.name: id for id in indicator_definitions}
        self.indicators = {indicator.name: IndicatorResult(id_def_lookup[indicator.name], indicator.flag) for indicator in indicators}
        if substances:
            self.substances = [SubstanceReference(substance.reference_value, substance.indicators) for substance in substances]
        else:
            self.substances = []


class SubstanceResultMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.legislations = {}

    def add_substances(self, legislations: Union[List, None] = None):
        self.legislations = {legislation.legislation_name: LegislationResult(legislation.legislation_name, legislation.impacted_substances) for
                         legislation in legislations}


class BoM1711Reference(ItemReference):
    def __init__(self, bom: Union[str, None] = None):
        super().__init__()
        self._bom = bom

    @property
    def definition(self) -> str:
        return self._bom


class RecordBasedItemReference(ItemReference):
    def __init__(self,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        self._record_history_identity = record_history_identity
        self._record_guid = record_guid
        self._record_history_guid = record_history_guid
        self._model = None

    @classmethod
    def add_record_by_record_history_identity(cls, value):
        return cls(record_history_identity=value)

    @classmethod
    def add_record_by_record_history_guid(cls, value):
        return cls(record_history_guid=value)

    @classmethod
    def add_record_by_record_guid(cls, value):
        return cls(record_guid=value)

    @classmethod
    def add_stk_records(cls, stk_records: List[Dict[str, str]]):
        item_references = []
        for record in stk_records:
            assert 'dbkey' in record
            assert 'record_guid' in record

            item_references.append(cls(record_guid=record['record_guid']))
        return item_references

    def _create_definition(self):
        if self._record_history_identity:
            return self._model(reference_type="MiRecordHistoryIdentity", reference_value=self._record_history_identity)
        if self._record_guid:
            return self._model(reference_type="MiRecordGuid", reference_value=self._record_guid)
        if self._record_history_guid:
            return self._model(reference_type="MiRecordHistoryGuid", reference_value=self._record_history_guid)

    @property
    @abstractmethod
    def definition(self):
        pass


class PartReference(RecordBasedItemReference):
    def __init__(self,
                 record_history_identity: Union[str, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None,
                 part_number: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.part_number = part_number
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonPartReference

    @classmethod
    def add_record_by_part_number(cls, value):
        return cls(part_number=value)

    @property
    def definition(self) -> Model:
        definition = super()._create_definition() or self._model(reference_type="PartNumber", reference_value=self.part_number)
        return definition


class PartResult(PartReference, ComplianceResultMixin, SubstanceResultMixin):
    pass


class MaterialReference(RecordBasedItemReference):
    def __init__(self,
                 material_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.material_id = material_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonMaterialReference

    @classmethod
    def add_record_by_material_id(cls, value):
        return cls(material_id=value)

    @property
    def definition(self) -> Model:
        definition = super()._create_definition() or \
                     self._model(reference_type="MaterialId", reference_value=self.material_id)
        return definition


class MaterialResult(MaterialReference, ComplianceResultMixin, SubstanceResultMixin):
    pass


class SpecificationReference(RecordBasedItemReference):
    def __init__(self,
                 specification_id: Union[str, None] = None,
                 record_history_identity: Union[int, None] = None,
                 record_guid: Union[str, None] = None,
                 record_history_guid: Union[str, None] = None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.specification_id = specification_id
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceCommonSpecificationReference

    @classmethod
    def add_record_by_specification_id(cls, value):
        return cls(specification_id=value)

    @property
    def definition(self) -> Model:
        definition = super()._create_definition() or \
                     self._model(reference_type="SpecificationId", reference_value=self.specification_id)
        return definition


class SpecificationResult(SpecificationReference, ComplianceResultMixin, SubstanceResultMixin):
    pass


class SubstanceReference(RecordBasedItemReference):
    def __init__(self,
                 substance_name=None,
                 cas_number=None,
                 ec_number=None,
                 record_history_identity=None,
                 record_guid=None,
                 record_history_guid=None,
                 percentage_amount=None):
        super().__init__(record_history_identity, record_guid, record_history_guid)
        self.substance_name = substance_name
        self.cas_number = cas_number
        self.ec_number = ec_number
        if percentage_amount:
            self._percentage_amount = percentage_amount
        self._model = bomanalytics.GrantaBomAnalyticsServicesInterfaceGetComplianceForSubstancesSubstanceWithAmount

    @classmethod
    def add_record_by_substance_name(cls, value):
        return cls(substance_name=value)

    @classmethod
    def add_record_by_cas_number(cls, value):
        return cls(cas_number=value)

    @classmethod
    def add_record_by_ec_number(cls, value):
        return cls(ec_number=value)

    @property
    def percentage_amount(self) -> float:
        return self._percentage_amount

    @percentage_amount.setter
    def percentage_amount(self, value: float):
        assert 0 < value < 100
        self._percentage_amount = value

    @property
    def definition(self) -> Model:
        definition = super()._create_definition()
        if not definition:
            if self.substance_name:
                definition = self._model(reference_type="ChemicalName", reference_value=self.substance_name)
            elif self.cas_number:
                definition = self._model(reference_type="CasNumber", reference_value=self.cas_number)
            elif self.ec_number:
                definition = self._model(reference_type="EcNumber", reference_value=self.ec_number)
        assert definition
        definition.percentage_amount = self._percentage_amount
        return definition


class SubstanceResult(SubstanceReference, ComplianceResultMixin):
    pass


class SubstanceWithAmount(SubstanceReference):
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


class LegislationReference:
    def __init__(self, name: str):
        self.name = name

    @property
    def definition(self):
        return self.name


class LegislationResult(LegislationReference):
    def __init__(self, name: str, substances: List[Union[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance,
                                                         models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance]]):
        super().__init__(name)
        self.substances = [SubstanceWithAmount(**substance.to_dict()) for substance in substances]