"""BoM Analytics BoM item result definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are returned from
queries. These are mostly extensions of the classes in _item_definitions.py.
"""
from typing import List, Dict, Union, Callable, TYPE_CHECKING, Optional, overload, TypeVar, Type, Any
from copy import deepcopy
from ansys.grantami.bomanalytics_codegen import models  # type: ignore[import]
from ._item_definitions import (
    MaterialDefinition,
    PartDefinition,
    SpecificationDefinition,
    BaseSubstanceReference,
    ReferenceType,
    CoatingReference,
)
from .indicators import WatchListIndicator, RoHSIndicator

if TYPE_CHECKING:
    from ._query_results import MaterialImpactedSubstancesQueryResult  # noqa: F401

Result_Model_Material = TypeVar(
    "Result_Model_Material",
    bound=Union[
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForMaterialsMaterial,
        models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance,
    ],
)
Result_Model_Part = TypeVar(
    "Result_Model_Part",
    bound=Union[
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForPartsPart,
        models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance,
    ],
)
Result_Model_Specification = TypeVar(
    "Result_Model_Specification",
    bound=Union[
        models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForSpecificationsSpecification,
        models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance,
    ],
)
Result_Model_Substance = TypeVar(
    "Result_Model_Substance", bound=models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance
)
Result_Model_Coating = TypeVar(
    "Result_Model_Coating", bound=models.GrantaBomAnalyticsServicesInterfaceCommonCoatingWithCompliance
)
Result_Model_Bom = TypeVar(
    "Result_Model_Bom", bound=models.GrantaBomAnalyticsServicesInterfaceGetImpactedSubstancesForBom1711Response
)
Result_Model_Any = Union[Result_Model_Part,
                         Result_Model_Material,
                         Result_Model_Specification,
                         Result_Model_Coating,
                         Result_Model_Substance,
                         Result_Model_Bom]
Item_Result = Union[Type["ImpactedSubstancesResultMixin"], Type["ComplianceResultMixin"]]
Indicator_Definitions = Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]


class ItemResultFactory:
    """Creates item results for a given type of API query. The key to control which result type is created is the name
    of the query class in `queries.py`.
    """

    registry: Dict[str, Item_Result] = {}
    """Mapping between an item result class and the query type it supports."""

    @classmethod
    def register(cls, name: str) -> Callable:
        """Decorator function to register a specific item result class with the name of a result type.

        Parameters
        ----------
        name
            The name of the result type to be registered.

        Returns
        -------
        Callable
            The function that's being decorated.
        """

        def inner(result_class: Item_Result) -> Item_Result:
            cls.registry[name] = result_class
            return result_class

        return inner

    @classmethod
    @overload
    def create_impacted_substances_result(
        cls, result_type_name: str, result_with_impacted_substances: Result_Model_Material
    ) -> "MaterialWithImpactedSubstancesResult":
        ...

    @classmethod
    @overload
    def create_impacted_substances_result(  # type: ignore[misc]
        cls, result_type_name: str, result_with_impacted_substances: Result_Model_Part
    ) -> "PartWithImpactedSubstancesResult":
        ...

    @classmethod
    @overload
    def create_impacted_substances_result(  # type: ignore[misc]
        cls, result_type_name: str, result_with_impacted_substances: Result_Model_Specification
    ) -> "SpecificationWithImpactedSubstancesResult":
        ...

    @classmethod
    @overload
    def create_impacted_substances_result(  # type: ignore[misc]
        cls, result_type_name: str, result_with_impacted_substances: Result_Model_Bom
    ) -> "BoM1711WithImpactedSubstancesResult":
        ...

    @classmethod
    def create_impacted_substances_result(cls, result_type_name: str, result_with_impacted_substances: Result_Model_Any) -> "ImpactedSubstancesResultMixin":
        """Factory method to return a specific impacted substances result.

        Parameters
        ----------
        result_type_name
            The name of the result for which an object is needed.
        result_with_impacted_substances
            The result from the REST API describing the impacted substances for this particular item.

        Returns
        -------
        Impacted Substances Item Result
            An object that describes the substances that impacted a material, part, specification, or BoM. Substances
            are grouped by legislation.

        Raises
        ------
        RuntimeError
            If a query type is not registered to any factory.
        """

        item_result_class = cls.registry[result_type_name]
        assert issubclass(item_result_class, ImpactedSubstancesResultMixin)
        try:
            reference_type = cls.parse_reference_type(result_with_impacted_substances.reference_type)
            item_result = item_result_class(
                reference_type=reference_type,
                reference_value=result_with_impacted_substances.reference_value,
                legislations=result_with_impacted_substances.legislations,
            )
        except AttributeError:
            # This is a Bom-type query result, and has no record reference
            item_result = item_result_class(legislations=result_with_impacted_substances.legislations)
        return item_result

    @classmethod
    @overload
    def create_compliance_result(
        cls, result_type_name: str, result_with_compliance: Result_Model_Material, indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]
    ) -> "MaterialWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls, result_type_name: str, result_with_compliance: Result_Model_Part, indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]
    ) -> "PartWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls, result_type_name: str, result_with_compliance: Result_Model_Specification, indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]
    ) -> "SpecificationWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls, result_type_name: str, result_with_compliance: Result_Model_Coating, indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]
    ) -> "CoatingWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls, result_type_name: str, result_with_compliance: Result_Model_Substance, indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]
    ) -> "SubstanceWithComplianceResult":
        ...

    @classmethod
    def create_compliance_result(
        cls,
        result_type_name: str,
        result_with_compliance: Result_Model_Any,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ) -> "ComplianceResultMixin":
        """Factory method to return a specific item result.

        Parameters
        ----------
        result_type_name
            The name of the result for which an object is needed.
        result_with_compliance
            The result from the REST API describing the compliance for this particular item.
        indicator_definitions
            The definitions of the indicators supplied to the original query. Required since the REST API does not
            provide them in the response.

        Returns
        -------
        Compliance Item Result
            An object that describes the compliance of a substance, material, part, specification, or BoM. Is defined
            recursively, with each level of the BoM having a reported compliance status for each indicator.

        Raises
        ------
        RuntimeError
            If a query type is not registered to any factory.
        """

        reference_type = cls.parse_reference_type(result_with_compliance.reference_type)
        item_result_class = cls.registry[result_type_name]
        assert issubclass(item_result_class, ComplianceResultMixin)
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
        reference_type
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
    """Represents a substance impacted by a specific legislation for a specific item.

    Examples
    --------
    >>> result: MaterialImpactedSubstancesQueryResult
    >>> substance = result.impacted_substances[4]
    >>> print(f"{substance.cas_number}: {substance.max_percentage_amount_in_material}")
    1333-86-4: 20.0 %
    """

    def __init__(
        self,
        reference_type: ReferenceType,
        reference_value: Union[int, str],
        max_percentage_amount_in_material: Optional[float],
        legislation_threshold: Optional[float],
    ):
        """
        Parameters
        ----------
        reference_type
            The type of the record reference value.
        reference_value
            The value of the record reference. All are `str`, except for record history identities which are `int`.
        max_percentage_amount_in_material
            The amount of this substance that occurs in the parent material. In the case where a range is specified in
             the declaration, only the maximum is reported here.
        legislation_threshold
            The substance concentration threshold over which the material is non-compliant with the legislation.
        """

        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.max_percentage_amount_in_material: Optional[float] = max_percentage_amount_in_material
        """The amount of this substance that occurs in the parent material. In the case where a range is specified in
        the declaration, only the maximum is reported here. `None` means the percentage amount has not been specified,
        not that the amount is 0 %."""

        self.legislation_threshold: Optional[float] = legislation_threshold
        """The substance concentration threshold over which the material is non-compliant with the legislation. `None`
        means the threshold has not been specified, not that the threshold is 0 %."""

    def __repr__(self) -> str:
        return (
            f'<ImpactedSubstance: {{"cas_number": {self.cas_number}, '
            f'"percent_amount": {self.max_percentage_amount_in_material}}}>'
        )


class LegislationResult:
    """Describes the result of an impacted substances query for a particular legislation.

    Examples
    --------
    >>> result: MaterialImpactedSubstancesQueryResult
    >>> result.impacted_substances_by_legislation["REACH - The Candidate List"]
    {'REACH - The Candidate List': [
        <ImpactedSubstance: {"cas_number": 90481-04-2}>, ...]
    }
    """

    def __init__(
        self,
        name: str,
        impacted_substances: List[models.GrantaBomAnalyticsServicesInterfaceCommonImpactedSubstance],
    ):
        """
        Parameters
        ----------
        name
            The name of the legislation.
        impacted_substances
            The result from the low-level API that describes which substances appear in the parent item.

        Raises
        ------
        RuntimeError
            If the substance returned by the low-level API does not contain a reference.
        """

        self.name: str = name
        self.substances: List[ImpactedSubstance] = []
        """ The substances found that are impacted by this legislation, along with the amount in the parent item
         if specified. """

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

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({{"name": {self.name}}}), {len(self.substances)} ImpactedSubstances>'


if TYPE_CHECKING:
    mixin_base_class = PartDefinition
else:
    mixin_base_class = object


class ImpactedSubstancesResultMixin(mixin_base_class):
    """Adds results from an impacted substances query to an `ItemDefinition` class, turning it into an
    `ItemWithImpactedSubstancesResult` class.

    Extensions to the constructor only, doesn't implement any additional methods.
    """

    def __init__(
        self,
        legislations: List[models.GrantaBomAnalyticsServicesInterfaceCommonLegislationWithImpactedSubstances],
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        legislations
            The substances that are found in the `ItemDefinition` item for the specified legislations.
        **kwargs
            Contains the `reference_type` and `reference_value` for `RecordDefinition`-based objects. Is empty for
            `BoM1711Definition`-based objects.
        """

        super().__init__(**kwargs)

        self._legislations: Dict[str, LegislationResult] = {}

        for legislation in legislations:
            new_legislation_result = LegislationResult(
                name=legislation.legislation_name,
                impacted_substances=legislation.impacted_substances,
            )
            self._legislations[legislation.legislation_name] = new_legislation_result

    @property
    def legislations(self) -> Dict[str, LegislationResult]:
        """
        Returns
        -------
            The substances impacted for a particular item, grouped by legislation name.

        Examples
        --------
        >>> result: MaterialImpactedSubstancesQueryResult
        >>> material_result = result.impacted_substances_by_material_and_legislation[0]
        >>> material_result.legislations
        {'California Proposition 65 List':
                <LegislationResult({"name": California Proposition 65 List}),
                    2 ImpactedSubstances>,
        ... }
        """

        return self._legislations

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.record_reference}), {len(self.legislations)} legislations>"


@ItemResultFactory.register("MaterialWithImpactedSubstances")
class MaterialWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, MaterialDefinition):
    pass


@ItemResultFactory.register("PartWithImpactedSubstances")
class PartWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, PartDefinition):
    pass


@ItemResultFactory.register("SpecificationWithImpactedSubstances")
class SpecificationWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, SpecificationDefinition):
    pass


@ItemResultFactory.register("Bom1711WithImpactedSubstances")
class BoM1711WithImpactedSubstancesResult(ImpactedSubstancesResultMixin):
    pass


class ComplianceResultMixin(mixin_base_class):
    """Adds results from a compliance query to a class deriving from `ItemDefinition`, turning it into an
    `[ItemType]WithComplianceResult` class.

    A compliance query returns a Bom-like result (see Notes for more background), with indicator results attached to
    each level of the Bom. This mixin implements only the indicator results for a given item; separate mixins
    instantiate and add the child items to the parent.

    Parameters
    ----------
    indicator_results
        Compliance of the `ItemDefinition` item for the specified indicators. Does not include the full indicator
        definition; only the indicator name
    indicator_definitions
        Used as a base to create the indicator results for both this item and the child substances.
    **kwargs
        Contains the `reference_type` and `reference_value` for `RecordDefinition`-based objects. Is empty
        for `BoM1711Definition`-based objects.

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

    _definition = None  # Required for linter, is supplied by the main RecordDefinition-derived class

    def __init__(
        self,
        indicator_results: List[models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorResult],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._indicator_definitions = indicator_definitions
        self.indicators: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]] = deepcopy(indicator_definitions)
        """Created as a copy of the `indicator_definitions` parameter, with each indicator definition augmented with the
        result returned by the low-level API."""

        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.record_reference}), {len(self.indicators)} indicators>"


if TYPE_CHECKING:
    child_base_class = ComplianceResultMixin
else:
    child_base_class = object


class ChildSubstanceWithComplianceMixin(child_base_class):
    """Adds a 'substance' attribute to an `ItemWithComplianceResult` class and populates it with child substances.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_substances
        The materials returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._substances: List[SubstanceWithComplianceResult] = []

    @property
    def substances(self) -> List["SubstanceWithComplianceResult"]:
        """The substance compliance result objects that are direct children of this item.

        Examples
        --------
        >>> material_result: MaterialWithComplianceResult
        >>> material_result.substances
        [SubstanceWithComplianceResult({"MiRecordHistoryIdentity": 77107}),
                1 indicators>, ...]
        """

        return self._substances

    def _add_child_substances(
        self, child_substances: List[models.GrantaBomAnalyticsServicesInterfaceCommonSubstanceWithCompliance]
    ) -> None:
        """Populate the `substances` attribute based on a provided list of low-level API substance with compliance
        results.

        Parameters
        ----------
        child_substances
            A list of substances with compliance returned from the low-level API
        """

        for child_substance in child_substances:
            child_substance_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="SubstanceWithCompliance",
                result_with_compliance=child_substance,
                indicator_definitions=self._indicator_definitions,
            )
            self._substances.append(child_substance_with_compliance)


class ChildMaterialWithComplianceMixin(child_base_class):
    """Adds a 'material' attribute to an `ItemWithComplianceResult` class and populates it with child materials.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_materials
        The materials returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._materials: List[MaterialWithComplianceResult] = []

    @property
    def materials(self) -> List["MaterialWithComplianceResult"]:
        """The material compliance result objects that are direct children of this part or substance.

        Examples
        --------
        >>> part_result: PartWithComplianceResult
        >>> part_result.materials
        [<MaterialWithComplianceResult({"MiRecordHistoryIdentity": "11774"}),
                1 indicators>, ...]
        """

        return self._materials

    def _add_child_materials(
        self,
        child_materials: List[models.GrantaBomAnalyticsServicesInterfaceCommonMaterialWithCompliance],
    ) -> None:
        """Populate the `materials` attribute based on a provided list of low-level API materials with compliance
        results.

        Operates recursively, i.e. also adds any substances with compliance that are children of each material.

        Parameters
        ----------
        child_materials
            A list of materials with compliance returned from the low-level API
        """

        for child_material in child_materials:
            child_material_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="MaterialWithCompliance",
                result_with_compliance=child_material,
                indicator_definitions=self._indicator_definitions,
            )
            child_material_with_compliance._add_child_substances(child_material.substances)
            self._materials.append(child_material_with_compliance)


class ChildSpecificationWithComplianceMixin(child_base_class):
    """Adds a 'specification' attribute to an `ItemWithComplianceResult` class and populates it with child
    specifications.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_specifications
        The specifications returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._specifications: List[SpecificationWithComplianceResult] = []

    @property
    def specifications(self) -> List["SpecificationWithComplianceResult"]:
        """The specification compliance result objects that are direct children of this item.

        Examples
        --------
        >>> part_result: PartWithComplianceResult
        >>> part_result.specifications
        [<SpecificationWithComplianceResult({"MiRecordHistoryIdentity": "123456"}),
                1 indicators>, ...]
        """

        return self._specifications

    def _add_child_specifications(
        self,
        child_specifications: List[models.GrantaBomAnalyticsServicesInterfaceCommonSpecificationWithCompliance],
    ) -> None:
        """Populate the `specifications` attribute based on a provided list of low-level API specifications with
        compliance results.

        Operates recursively, i.e. also adds any specifications, materials, coatings, and substances with compliance
        that are children of each specification.

        Parameters
        ----------
        child_specifications
            A list of specifications with compliance returned from the low-level API
        """

        for child_specification in child_specifications:
            child_specification_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="SpecificationWithCompliance",
                result_with_compliance=child_specification,
                indicator_definitions=self._indicator_definitions,
            )
            child_specification_with_compliance._add_child_materials(child_specification.materials)
            child_specification_with_compliance._add_child_specifications(child_specification.specifications)
            child_specification_with_compliance._add_child_coatings(child_specification.coatings)
            child_specification_with_compliance._add_child_substances(child_specification.substances)
            self._specifications.append(child_specification_with_compliance)


class ChildPartWithComplianceMixin(child_base_class):
    """Adds a 'part' attribute to an `ItemWithComplianceResult` class and populates it with child parts.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_parts
        The parts returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._parts: List[PartWithComplianceResult] = []

    @property
    def parts(self) -> List["PartWithComplianceResult"]:
        """The part compliance result objects that are direct children of this part.

        Examples
        --------
        >>> part_result: PartWithComplianceResult
        >>> part_result.parts
        [<PartWithComplianceResult({"MiRecordHistoryIdentity": "564777"}),
                1 indicators>, ...]
        """

        return self._parts

    def _add_child_parts(
        self,
        child_parts: List[models.GrantaBomAnalyticsServicesInterfaceCommonPartWithCompliance],
    ) -> None:
        """Populate the `parts` attribute based on a provided list of low-level API parts with compliance
        results.

        Operates recursively, i.e. also adds any parts, materials, coatings, and substances with compliance
        that are children of each part.

        Parameters
        ----------
        child_parts
            A list of parts with compliance returned from the low-level API
        """

        for child_part in child_parts:
            child_part_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="PartWithCompliance",
                result_with_compliance=child_part,
                indicator_definitions=self._indicator_definitions,
            )
            child_part_with_compliance._add_child_parts(child_part.parts)
            child_part_with_compliance._add_child_specifications(child_part.specifications)
            child_part_with_compliance._add_child_materials(child_part.materials)
            child_part_with_compliance._add_child_substances(child_part.substances)
            self._parts.append(child_part_with_compliance)


class ChildCoatingWithComplianceMixin(child_base_class):
    """Adds a 'coating' attribute to an `ItemWithComplianceResult` class and populates it with child coatings.

    See the `ComplianceResultMixin` notes for more background on Compliance query results and BoM structures.

    Parameters
    ----------
    child_coatings
         The coatings returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. Contains record references for
        `RecordDefinition`-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._coatings: List[CoatingWithComplianceResult] = []

    @property
    def coatings(self) -> List["CoatingWithComplianceResult"]:
        """The coating result objects that are direct children of this specification.

        Examples
        --------
        >>> specification_results: SpecificationWithComplianceResult
        >>> specification_results.coatings
        [<CoatingWithComplianceResult({"MiRecordHistoryIdentity": 83291}),
                1 indicators>, ...]
        """

        return self._coatings

    def _add_child_coatings(
        self,
        child_coatings: List[models.GrantaBomAnalyticsServicesInterfaceCommonCoatingWithCompliance],
    ) -> None:
        """Populate the `coatings` attribute based on a provided list of low-level API coatings with compliance
        results.

        Operates recursively, i.e. also adds any substances with compliance that are children of each coating.

        Parameters
        ----------
        child_coatings
            A list of coatings with compliance returned from the low-level API
        """

        for child_coating in child_coatings:
            child_coating_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="CoatingWithCompliance",
                result_with_compliance=child_coating,
                indicator_definitions=self._indicator_definitions,
            )
            child_coating_with_compliance._add_child_substances(child_coating.substances)
            self._coatings.append(child_coating_with_compliance)


@ItemResultFactory.register("SubstanceWithCompliance")
class SubstanceWithComplianceResult(ComplianceResultMixin, BaseSubstanceReference):
    pass


@ItemResultFactory.register("MaterialWithCompliance")
class MaterialWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, MaterialDefinition):
    pass


@ItemResultFactory.register("PartWithCompliance")
class PartWithComplianceResult(
    ChildPartWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSubstanceWithComplianceMixin,
    ComplianceResultMixin,
    PartDefinition,
):
    pass


@ItemResultFactory.register("SpecificationWithCompliance")
class SpecificationWithComplianceResult(
    ChildCoatingWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSubstanceWithComplianceMixin,
    ComplianceResultMixin,
    SpecificationDefinition,
):
    pass


@ItemResultFactory.register("CoatingWithCompliance")
class CoatingWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, CoatingReference):
    pass
