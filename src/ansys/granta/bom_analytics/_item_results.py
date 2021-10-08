"""Bom Analytics Bom item result definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are returned from
queries. These are mostly extensions of the classes in _item_definitions.py.

Attributes
----------
Impacted_Substances_REST_Result
    The set of types that represent the low-level REST API items with impacted substances results.
Item_With_Impacted_Substances_Result
    The set of types that represent objects in this module with impacted substances results.
Compliance_REST_Result
    The set of types that represent the low-level REST API items with compliance results.
Item_With_Compliance_Result
    The set of types that represent objects in this module with compliance results.
"""

from typing import List, Dict, Union, Callable, TYPE_CHECKING
from copy import copy
from ansys.granta.bomanalytics import models
from ._item_definitions import (
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

Impacted_Substances_REST_Result = Union[
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial,
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart,
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification,
    models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response,
]

Item_With_Impacted_Substances_Result = Union[
    "MaterialWithImpactedSubstancesResult",
    "PartWithImpactedSubstancesResult",
    "SpecificationsWithImpactedSubstancesResult",
    "BoM1711WithImpactedSubstancesResult",
]

Compliance_REST_Result = Union[
    models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance,
    models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance,
    models.GrantaBomAnalyticsServicesInterfaceCommonCoatingWithCompliance,
    models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance,
    models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance,
]

Item_With_Compliance_Result = Union[
    "SubstanceWithComplianceResult",
    "MaterialWithComplianceResult",
    "PartWithComplianceResult",
    "SpecificationsWithComplianceResult",
    "BoM1711WithComplianceResult",
]


class ItemResultFactory:
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
        """Decorator function to register a specific item result class with the name of a result type.

        Parameters
        ----------
        name : str
            The name of the result type to be registered.

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
    def create_impacted_substances_result(
        cls,
        result_type_name: str,
        result_with_impacted_substances: Impacted_Substances_REST_Result,
    ) -> Item_With_Impacted_Substances_Result:
        """Factory method to return a specific impacted substances result.

        Parameters
        ----------
        result_type_name : str
            The name of the result for which an object is needed.
        result_with_impacted_substances: `Impacted_Substances_Model_Result`
            The result from the REST API describing the impacted substances for this particular item.

        Returns
        -------
        `Impacted_Substances_Item_Result`
            An object that describes the substances that impacted a material, part, specification, or BoM. Substances
            are grouped by legislation.

        Raises
        ------
        RuntimeError
            If a query type is not registered to any factory.
        """

        reference_type = cls.parse_reference_type(result_with_impacted_substances.reference_type)
        item_result_class = cls.registry[result_type_name]
        item_result = item_result_class(
            reference_type=reference_type,
            reference_value=result_with_impacted_substances.reference_value,
            legislations=result_with_impacted_substances.legislations,
        )
        return item_result

    @classmethod
    def create_compliance_result(
        cls,
        result_type_name: str,
        result_with_compliance: Compliance_REST_Result,
        indicator_definitions: Indicator_Definitions,
    ) -> Item_With_Compliance_Result:
        """Factory method to return a specific item result.

        Parameters
        ----------
        result_type_name : str
            The name of the result for which an object is needed.
        result_with_compliance : `Compliance_Model_Result`
            The result from the REST API describing the compliance for this particular item.
        indicator_definitions : `Indicator_Definitions`
            The definitions of the indicators supplied to the original query. Required since the REST API does not
            provide them in the response.

        Returns
        -------
        `Compliance_Item_Result`
            An object that describes the compliance of a substance, material, part, specification, or BoM. Is defined
            recursively, with each level of the BoM having a reported compliance status for each indicator.

        Raises
        ------
        RuntimeError
            If a query type is not registered to any factory.
        """

        reference_type = cls.parse_reference_type(result_with_compliance.reference_type)
        item_result_class = cls.registry[result_type_name]
        item_result = item_result_class(
            reference_type=reference_type,
            reference_value=result_with_compliance.reference_value,
            indicator_results=result_with_compliance.indicators,
            indicator_definitions=indicator_definitions,
        )
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


class ImpactedSubstance(BaseSubstanceReference):
    """Extension of `BaseSubstanceDefinition` which includes impacted substance results.

    Parameters
    ----------
    reference_type : ReferenceType
        The type of the record reference value.
    reference_value : int or str
        The value of the record reference. All are `str`, except for record history identities which are `int`.
    max_percentage_amount_in_material : float
        The amount of this substance that occurs in the parent material. In the case where a range is specified in the
        declaration, only the maximum is reported here.
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


class ImpactedSubstancesResultMixin:
    """Adds results from an impacted substances query to an `ItemDefinition` class, turning it into an
    `ItemWithImpactedSubstancesResult` class.

    Extensions to the constructor only, doesn't implement any additional methods.

    Parameters
    ----------
    legislations : list of `models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances`
        The substances that are found in the `ItemDefinition` item for the specified legislations.
    **kwargs
        Contains the `reference_type` and `reference_value` for `RecordDefinition`-based objects. Is empty for
        `BoM1711Definition`-based objects.

    Attributes
    ----------
    legislations : dict of (str, LegislationResult)
        Describes the substances in the `ItemDefinition` for a particular legislation. The legislation name is used
        as the dictionary key.
    """

    def __init__(
        self,
        legislations: List[models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances],
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


@ItemResultFactory.register("materialWithImpactedSubstances")
class MaterialWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, MaterialDefinition):
    pass


@ItemResultFactory.register("partWithImpactedSubstances")
class PartWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, PartDefinition):
    pass


@ItemResultFactory.register("specificationWithImpactedSubstances")
class SpecificationWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, SpecificationDefinition):
    pass


@ItemResultFactory.register("bom1711WithImpactedSubstances")
class BoM1711WithImpactedSubstancesResult(ImpactedSubstancesResultMixin, BoM1711Definition):
    pass


class ComplianceResultMixin:
    """Adds results from a compliance query to a class deriving from `ItemDefinition`, turning it into an
    `[ItemType]WithComplianceResult` class.

     A compliance query returns a Bom-like result (see Notes for more background), with indicator results attached to
     each level of the Bom. This mixin implements only the indicator results for a given item; separate mixins
     instantiate and add the child items to the parent.

    Parameters
    ----------
    indicator_results : list of `models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult`
        Compliance of the `ItemDefinition` item for the specified indicators. Does not include the full indicator
        definition; only the indicator name
    indicator_definitions : `Indicator_Definitions`
        Used as a base to create the indicator results for both this item and the child substances.
    **kwargs
        Contains the `reference_type` and `reference_value` for `RecordDefinition`-based objects. Is empty
        for `BoM1711Definition`-based objects.

    Attributes
    ----------
    indicators : `Indicator_Definitions`
        Created as a copy of the `indicator_definitions` parameter, with each indicator definition augmented with the
        result returned by the low-level API.

    Notes
    -----
    Bills of Materials are recursively defined structures. The top-level item is always a 'Part'. 'Parts' can
    contain zero or more of:
    * 'Parts'
    * 'Specifications'
    * 'Materials'
    * 'Substances'

    'Specifications' can contain zero or more of:
    * 'Specifications'
    * 'Materials'
    * 'Coatings'
    * 'Substances'

    'Materials' and 'Coatings' can both contain zero or more of:
    * 'Substances'

    'Substances' have no children and are always leaf nodes.

    In addition to these items described above, a Compliance query result adds `Indicator` objects to all items at
    every level.

    This mixin is applied to `ItemDefinition` objects to turn them into `ItemWithCompliance` objects, where 'item' is
    one of 'Part', 'Specification', 'Material', 'Coating', and 'Substance'. With the exception
    """

    def __init__(
        self,
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Indicator_Definitions,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._indicator_definitions = indicator_definitions
        self.indicators: Indicator_Definitions = copy(indicator_definitions)
        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag


if TYPE_CHECKING:
    child_base_class = ComplianceResultMixin
else:
    child_base_class = object


class ChildSubstanceWithComplianceMixin(child_base_class):
    """Adds a 'substance' attribute to an `ItemWithComplianceResult` class and populates it with child substances.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_substances : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance`
        The materials returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.

    Attributes
    ----------
    substances : list of `SubstanceWithComplianceResult`
        Summarizes the compliance of each substance found in the `ItemDefinition`, allowing the source of non-compliance
        to be determined.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.substances: List[SubstanceWithComplianceResult] = []

    def _add_child_substances(
        self, child_substances: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance]
    ):
        """Populate the `substances` attribute based on a provided list of low-level API substance with compliance
        results.

        Parameters
        ----------
        child_substances : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance`
            A list of substances with compliance returned from the low-level API
        """

        for child_substance in child_substances:
            child_substance_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="substanceWithCompliance",
                result_with_compliance=child_substance,
                indicator_definitions=self._indicator_definitions,
            )
            self.substances.append(child_substance_with_compliance)


class ChildMaterialWithComplianceMixin(child_base_class):
    """Adds a 'material' attribute to an `ItemWithComplianceResult` class and populates it with child materials.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_materials : list of `models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance`
        The materials returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.

    Attributes
    ----------
    materials : list of `MaterialWithComplianceResult`
        The material result objects that are direct children of this part.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.materials: List[MaterialWithComplianceResult] = []

    def _add_child_materials(
        self,
        child_materials: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
    ):
        """Populate the `materials` attribute based on a provided list of low-level API materials with compliance
        results.

        Operates recursively, i.e. also adds any substances with compliance that are children of each material.

        Parameters
        ----------
        child_materials : list of `models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance`
            A list of materials with compliance returned from the low-level API
        """

        for child_material in child_materials:
            child_material_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="materialWithCompliance",
                result_with_compliance=child_material,
                indicator_definitions=self._indicator_definitions,
            )
            child_material_with_compliance._add_child_substances(child_material.substances)
            self.materials.append(child_material_with_compliance)


class ChildSpecificationWithComplianceMixin(child_base_class):
    """Adds a 'specification' attribute to an `ItemWithComplianceResult` class and populates it with child
    specifications.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_specifications : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance`
        The specifications returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.

    Attributes
    ----------
    specifications : list of `SpecificationWithComplianceResult`
        The specification result objects that are direct children of this item.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.specifications: List[SpecificationWithComplianceResult] = []

    def _add_child_specifications(
        self,
        child_specifications: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
    ):
        """Populate the `specifications` attribute based on a provided list of low-level API specifications with
        compliance results.

        Operates recursively, i.e. also adds any specifications, materials, coatings, and substances with compliance
        that are children of each specification.

        Parameters
        ----------
        child_specifications : list of `models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance`
            A list of specifications with compliance returned from the low-level API
        """

        for child_specification in child_specifications:
            child_specification_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="specificationWithCompliance",
                result_with_compliance=child_specification,
                indicator_definitions=self._indicator_definitions,
            )
            child_specification_with_compliance._add_child_materials(child_specification.materials)
            child_specification_with_compliance._add_child_specifications(child_specification.specifications)
            child_specification_with_compliance._add_child_coatings(child_specification.coatings)
            child_specification_with_compliance._add_child_substances(child_specification.substances)
            self.specifications.append(child_specification_with_compliance)


class ChildPartWithComplianceMixin(child_base_class):
    """Adds a 'part' attribute to an `ItemWithComplianceResult` class and populates it with child parts.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_parts : list of `models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance`
        The parts returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.

    Attributes
    ----------
    parts : list of `PartWithComplianceResult`
        The part result objects that are direct children of this part.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parts: List[PartWithComplianceResult] = []

    def _add_child_parts(
        self,
        child_parts: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
    ):
        """Populate the `parts` attribute based on a provided list of low-level API parts with compliance
        results.

        Operates recursively, i.e. also adds any parts, materials, coatings, and substances with compliance
        that are children of each part.

        Parameters
        ----------
        child_parts : list of `models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance`
            A list of parts with compliance returned from the low-level API
        """

        for child_part in child_parts:
            child_part_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="partWithCompliance",
                result_with_compliance=child_part,
                indicator_definitions=self._indicator_definitions,
            )
            child_part_with_compliance._add_child_parts(child_part.parts)
            child_part_with_compliance._add_child_specifications(child_part.specifications)
            child_part_with_compliance._add_child_materials(child_part.materials)
            child_part_with_compliance._add_child_substances(child_part.substances)
            self.parts.append(child_part_with_compliance)


class ChildCoatingWithComplianceMixin(child_base_class):
    """Adds a 'coating' attribute to an `ItemWithComplianceResult` class and populates it with child coatings.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_coatings : list of `models.GrantaBomAnalyticsServicesInterfaceCommonCoatingWithCompliance`
         The coatings returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.

    Attributes
    ----------
    coatings : list of `CoatingWithComplianceResult`
         The coating result objects that are direct children of this specification.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coatings: List[CoatingWithComplianceResult] = []

    def _add_child_coatings(
        self,
        child_coatings: List[models.GrantaBomAnalyticsServicesInterfaceCommonCoatingWithCompliance],
    ):
        """Populate the `coatings` attribute based on a provided list of low-level API coatings with compliance
        results.

        Operates recursively, i.e. also adds any substances with compliance that are children of each coating.

        Parameters
        ----------
        child_coatings : list of `models.GrantaBomAnalyticsServicesInterfaceCommonCoatingWithCompliance`
            A list of coatings with compliance returned from the low-level API
        """

        for child_coating in child_coatings:
            child_coating_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="coatingWithCompliance",
                result_with_compliance=child_coating,
                indicator_definitions=self._indicator_definitions,
            )
            child_coating_with_compliance._add_child_substances(child_coating.substances)
            self.coatings.append(child_coating_with_compliance)


@ItemResultFactory.register("substanceWithCompliance")
class SubstanceWithComplianceResult(ComplianceResultMixin, BaseSubstanceReference):
    pass


@ItemResultFactory.register("materialWithCompliance")
class MaterialWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, MaterialDefinition):
    pass


@ItemResultFactory.register("partWithCompliance")
class PartWithComplianceResult(
    ChildPartWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSubstanceWithComplianceMixin,
    ComplianceResultMixin,
    PartDefinition,
):
    pass


@ItemResultFactory.register("specificationWithCompliance")
class SpecificationWithComplianceResult(
    ChildCoatingWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSubstanceWithComplianceMixin,
    ComplianceResultMixin,
    SpecificationDefinition,
):
    pass


@ItemResultFactory.register("coatingWithCompliance")
class CoatingWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, CoatingDefinition):
    pass


@ItemResultFactory.register("bom1711WithCompliance")
class BoM1711WithComplianceResult(
    ChildPartWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSubstanceWithComplianceMixin,
    ComplianceResultMixin,
    BoM1711Definition,
):
    pass
