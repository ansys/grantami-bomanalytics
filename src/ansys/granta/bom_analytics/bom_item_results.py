from typing import List, Dict, Union, Callable, TYPE_CHECKING
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
    IndicatorDefinition,
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
    def generate_kwarg(result):
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
        self.substances: List[SubstanceWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="substanceWithCompliance",
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

        if not parts:
            parts = []
        if not materials:
            materials = []
        if not specifications:
            specifications = []

        self.parts: List[PartWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="partWithCompliance",
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
            BomItemResultFactory.create_record_result(
                name="materialWithCompliance",
                result=material,
                indicators=material.indicators,
                substances=material.substances,
                indicator_definitions=kwargs.get("indicator_definitions", []),
            )
            for material in materials
        ]

        self.specifications: List[SpecificationWithCompliance] = [
            BomItemResultFactory.create_record_result(
                name="specificationWithCompliance",
                result=specification,
                indicators=specification.indicators,
                substances=specification.substances,
                indicator_definitions=kwargs.get("indicator_definitions", []),
            )
            for specification in specifications
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
    ComplianceResultMixin, BomStructureResultMixin, PartDefinition
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
    ComplianceResultMixin, BomStructureResultMixin, BoM1711Definition
):
    pass


@BomItemResultFactory.register("substanceWithCompliance")
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
        indicator_definitions: List[Union[WatchListIndicator, RoHSIndicator]] = None,
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


@BomItemResultFactory.register("substanceWithAmounts")
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


class IndicatorResultMixin:
    if TYPE_CHECKING:
        _indicator_type = None
        flags = None

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        flag: str,
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        try:
            self.flag: str = self.__class__.flags[flag]
        except KeyError as e:
            raise Exception(
                f'Unknown flag {flag} for indicator {name}, type "{self._indicator_type}"'
            ).with_traceback(e.__traceback__)


class RoHSIndicatorResult(IndicatorResultMixin, RoHSIndicator):
    pass


class WatchListIndicatorResult(IndicatorResultMixin, WatchListIndicator):
    pass


def create_indicator_result(
    indicator_from_mi: models.granta_bom_analytics_services_interface_common_indicator_result,
    indicator_definitions: List[IndicatorDefinition],
) -> Union[WatchListIndicatorResult, RoHSIndicatorResult, None]:

    assert indicator_definitions, "indicator_definitions is empty"
    for indicator_definition in indicator_definitions:
        if indicator_from_mi.name == indicator_definition.name:
            if isinstance(indicator_definition, WatchListIndicator):
                result = WatchListIndicatorResult(
                    name=indicator_from_mi.name,
                    legislation_names=indicator_definition.legislation_names,
                    default_threshold_percentage=indicator_definition.default_threshold_percentage,
                    flag=indicator_from_mi.flag,
                )
                return result
            elif isinstance(indicator_definition, RoHSIndicator):
                result = RoHSIndicatorResult(
                    name=indicator_from_mi.name,
                    legislation_names=indicator_definition.legislation_names,
                    default_threshold_percentage=indicator_definition.default_threshold_percentage,
                    flag=indicator_from_mi.flag,
                )
                return result
            else:
                raise RuntimeError(
                    f"Indicator {indicator_definition.name} has unknown type {type(indicator_definition)}"
                )
    raise RuntimeError(
        f"Indicator {indicator_from_mi.name} does not have a corresponding definition"
    )
