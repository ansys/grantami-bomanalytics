"""Bom Analytics Bom item result definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are returned from
queries. These are extensions of the classes in _bom_item_definitions.py.
"""

from typing import List, Dict, Union, Callable, TypeVar
from copy import copy
from ansys.granta.bomanalytics import models
from ._bom_item_definitions import (
    MaterialDefinition,
    PartDefinition,
    SpecificationDefinition,
    BoM1711Definition,
    BaseSubstanceDefinition,
    RecordDefinition,
    ReferenceType,
)
from .indicators import Indicator_Definitions


Item_Result = TypeVar(
    "Item_Result",
    covariant=True,
    bound=Union["ImpactedSubstancesResultMixin", "ComplianceResultMixin"],
)


class BomItemResultFactory:
    """Creates item results for a given type of API query. The key to control which result type is created is the name
     of the query class in `queries.py`.

    Class Attributes
    ----------------
    registry : dict
        Mapping between an item result class and the query type it supports.
    """

    registry = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        """Decorator function to register a specific item result class with a query name.

        Parameters
        ----------
        name : str
            The name of the query to be registered.

        Returns
        -------
        Callable
            The function that's being decorated.
        """

        def inner(result_class: RecordDefinition) -> RecordDefinition:
            cls.registry[name] = result_class
            return result_class

        return inner

    @classmethod
    def create_record_result(cls, name: str, reference_type: Union[str, None], **kwargs) -> Item_Result:
        """Factory method to return a specific item result.

        Parameters
        ----------
        name : str
            The name of the query for which a result object is needed
        reference_type : str, optional
            The `reference_type` is pulled out of **kwargs because it needs to be used as a key to get the appropriate
            `ReferenceType` enum member. Not populated for Bom item results.
        **kwargs
            All other arguments required to instantiate the item definition, including the `reference_value` for
            `RecordDefinition`-based results.

        Returns
        -------
        Item_Result

        Raises
        ------
        RuntimeError
            If a query type is not registered to any factory.
        """

        try:
            item_result_class = cls.registry[name]
        except KeyError:
            raise RuntimeError(f"Unregistered result object {name}")

        reference_type = cls.parse_reference_type(reference_type)
        item_result = item_result_class(reference_type=reference_type, **kwargs)
        return item_result

    @staticmethod
    def parse_reference_type(reference_type: str) -> ReferenceType:
        """Parse the `reference_type` returned by the low-level API into a `ReferenceType`.

        Parameters
        ----------
        reference_type : str
            The type of record reference returned from the API for a particular result.

        Returns
        -------
        ReferenceType
            The specific enum value for the `reference_type` `str`.

        Raises
        ------
        KeyError
            If the `reference_type` returned by the low-level API doesn't appear in `ReferenceType`.
        """

        try:
            return ReferenceType[reference_type]
        except KeyError as e:
            raise KeyError(f"Unknown reference_type {reference_type} returned.").with_traceback(e.__traceback__)


class ComplianceResultMixin:
    """Adds results from a compliance query to an `ItemDefinition` class.

    Extensions to the constructor only, doesn't implement any additional methods.

    Parameters
    ----------
    indicator_results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult`
        Compliance of the `ItemDefinition` item for the specified indicators. Does not include the full indicator
        definition; only the indicator name
    indicator_definitions : `Indicator_Definitions`
        The indicators defined in the original query
    substances_with_compliance : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance`
        The substances associated with the `ItemDefinition` item for the legislations included in the specified
        indicators.
    **kwargs
        Contains the `reference_type` and `reference_value` for `RecordDefinition`-based objects.

    Attributes
    ----------
    indicators : `Indicator_Definitions`
        Created as a copy of the `indicator_definitions` parameter, with each indicator definition augmented with the
        result returned by the low-level API.
    substances : list of `SubstanceWithCompliance`
        Summarizes the compliance of each substance found in the `ItemDefinition`, allowing the source of non-compliance
        to be determined.
    """

    def __init__(
        self,
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Indicator_Definitions,
        substances_with_compliance: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.indicators: Indicator_Definitions = copy(indicator_definitions)
        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag

        if not substances_with_compliance:
            substances_with_compliance = []
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
    """Adds results from an impacted substances query to an `ItemDefinition` class.

    Extensions to the constructor only, doesn't implement any additional methods.

    Parameters
    ----------
    legislations : list of `models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances`
        The substances that are found in the `ItemDefinition` item for the specified legislations.
    **kwargs
        Contains the `reference_type` and `reference_value` for `RecordDefinition`-based objects.

    Attributes
    ----------
    legislations : dict of (str, LegislationResult)
        Describes the substances in the `ItemDefinition` for a particular legislation. The legislation name is used
        as the dictionary key.
    """

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
    """Adds a recursive 17/11 Bill of Materials structure to an `ItemDefinition`.

    Bills of Materials are recursively defined structures. The top-level item is always a 'Part', but 'Parts' can
    contain zero or more of 'Parts', 'Materials', 'Specifications' and 'Substances'. 'Specifications' can contain
    'Materials', 'Specifications', and 'Substances', and 'Materials' can only contain 'Substances'. 'Substances' have
    no children and are always leaf nodes.

    As a result, there is in principle no limit to how complex a Bill of Materials can be. This mixin allows for
    arbitrary complexity by calling itself, 'material' and 'specification' factories.

    This mixin is only applied to `ItemDefinitions` that represent part-like objects, i.e. `PartDefinition` and
    `BoM1711Definition` classes. Only compliance queries fully evaluate and return the Bom structure, so
    impacted substance queries do not require this mixin.

    Parameters
    ----------
    child_parts : list of `models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance`
        The parts returned by the low-level API that are children of this part.
    child_materials : list of `models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance`
        The materials returned by the low-level API that are children of this part.
    child_specifications : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance`
        The specifications returned by the low-level API that are children of this part.
    indicator_results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult`
        Required by the the `ComplianceMixin`, which is always used with this mixin. Not required here.
    indicator_definitions : `Indicator_Definitions`
        Required by the the `ComplianceMixin`, which is always used with this mixin. Not required here.
    substances_with_compliance : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance`
        Required by the the `ComplianceMixin`, which is always used with this mixin. Not required here.
    **kwargs
        Contains the `reference_type` and `reference_value` for `RecordDefinition`-based objects.

    Attributes
    ----------
    parts : list of `PartWithCompliance`
        The part result objects that are direct children of this part.
    materials : list of `MaterialWithCompliance`
        The material result objects that are direct children of this part.
    specifications : list of `SpecificationWithCompliance`
        The specification result objects that are direct children of this part.
    """

    def __init__(
        self,
        child_parts: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
        child_materials: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
        child_specifications: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Indicator_Definitions,
        substances_with_compliance: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance],
        **kwargs,
    ):
        super().__init__(indicator_results, indicator_definitions, substances_with_compliance, **kwargs)

        if not child_parts:
            child_parts = []
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

        if not child_materials:
            child_materials = []
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

        if not child_specifications:  # TODO: Specifications can have material children? And coating children!
            child_specifications = []
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
    """Extension of `MaterialDefinition` which includes impacted substances query results."""

    pass


@BomItemResultFactory.register("materialWithCompliance")
class MaterialWithCompliance(ComplianceResultMixin, MaterialDefinition):
    """Extension of `MaterialDefinition` which includes compliance query results."""

    pass


@BomItemResultFactory.register("partWithImpactedSubstances")
class PartWithImpactedSubstances(ImpactedSubstancesResultMixin, PartDefinition):
    """Extension of `PartDefinition` which includes impacted substances query results."""

    pass


@BomItemResultFactory.register("partWithCompliance")
class PartWithCompliance(BomStructureResultMixin, ComplianceResultMixin, PartDefinition):
    """Extension of `PartDefinition` which includes compliance query results and bom structure attributes."""

    pass


@BomItemResultFactory.register("specificationWithImpactedSubstances")
class SpecificationWithImpactedSubstances(ImpactedSubstancesResultMixin, SpecificationDefinition):
    """Extension of `SpecificationDefinition` which includes impacted substances query results."""

    pass


@BomItemResultFactory.register("specificationWithCompliance")
class SpecificationWithCompliance(ComplianceResultMixin, SpecificationDefinition):
    """Extension of `SpecificationDefinition` which includes compliance query results."""

    pass


@BomItemResultFactory.register("bom1711WithImpactedSubstances")
class BoM1711WithImpactedSubstances(ImpactedSubstancesResultMixin, BoM1711Definition):
    """Extension of `BoM1711Definition` which includes impacted substances query results."""

    pass


@BomItemResultFactory.register("bom1711WithCompliance")
class BoM1711WithCompliance(BomStructureResultMixin, ComplianceResultMixin, BoM1711Definition):
    """Extension of `BoM1711Definition` which includes compliance query results and bom structure attributes."""

    pass


@BomItemResultFactory.register("substanceWithCompliance")
class SubstanceWithCompliance(BaseSubstanceDefinition):
    """Extension of `BaseSubstanceDefinition` which includes compliance query results.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    indicator_results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult`
        Compliance of the `ItemDefinition` item for the specified indicators. Does not include the full indicator
        definition; only the indicator name
    indicator_definitions : `Indicator_Definitions`
        The indicators defined in the original query

    Attributes
    ----------
    indicators : `Indicator_Definitions`
        Created as a copy of the `indicator_definitions` parameter, with each indicator definition augmented with the
        result returned by the low-level API.
    """

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

    @property
    def definition(self):
        return


class ImpactedSubstance(BaseSubstanceDefinition):
    """Extension of `BaseSubstanceDefinition` which includes impacted substance results.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    max_percentage_amount_in_material : float
        The percentage amount of this substance that occurs in the parent material. In the case where a range is
        specified in the declaration, only the maximum is reported here.
    legislation_threshold : float
        The substance concentration threshold over which the material is non-compliant with the legislation.
    """

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

    @property
    def definition(self):
        return


class LegislationResult:
    """Describes the result of an impacted substances query for a particular legislation.

    Parameters
    ----------
    name : str
        The name of the legislation.
    impacted_substances : list of `models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance`
        The result from the low-level API that describes which substances appear in the parent item.

    Attributes
    ----------
    substances : list of `ImpactedSubstance`

    Raises
    ------
    RuntimeError
        If the substance returned by the low-level API does not contain a reference.
    """

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
                    "in your request include references, and check you are using an up-to-date version "
                    "of the base bom analytics package."
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
