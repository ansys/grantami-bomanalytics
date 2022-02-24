"""BoM Analytics BoM item result definitions.

Defines the representations of the items (materials, parts, specifications, and substances) that are returned from
queries. These are mostly extensions of the classes in the ``_item_definitions.py`` file.
"""
from typing import (
    List,
    Dict,
    Union,
    Callable,
    TYPE_CHECKING,
    Optional,
    overload,
    TypeVar,
    Type,
    Any,
)
from copy import deepcopy
from ansys.grantami.bomanalytics_openapi import models  # type: ignore[import]
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
        models.GetImpactedSubstancesForMaterialsMaterial,
        models.CommonMaterialWithCompliance,
    ],
)
Result_Model_Part = TypeVar(
    "Result_Model_Part",
    bound=Union[
        models.GetImpactedSubstancesForPartsPart,
        models.CommonPartWithCompliance,
    ],
)
Result_Model_Specification = TypeVar(
    "Result_Model_Specification",
    bound=Union[
        models.GetImpactedSubstancesForSpecificationsSpecification,
        models.CommonSpecificationWithCompliance,
    ],
)
Result_Model_Substance = TypeVar("Result_Model_Substance", bound=models.CommonSubstanceWithCompliance)
Result_Model_Coating = TypeVar("Result_Model_Coating", bound=models.CommonCoatingWithCompliance)
Result_Model_Bom = TypeVar("Result_Model_Bom", bound=models.GetImpactedSubstancesForBom1711Response)
Result_Model_Any = Union[
    Result_Model_Part,
    Result_Model_Material,
    Result_Model_Specification,
    Result_Model_Coating,
    Result_Model_Substance,
    Result_Model_Bom,
]
Item_Result = Union[Type["ImpactedSubstancesResultMixin"], Type["ComplianceResultMixin"]]
Indicator_Definitions = Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]


class ItemResultFactory:
    """Creates item results for a given type of API query. The key to controlling which result type is created is the
    name of the query class in ``queries.py``.
    """

    registry: Dict[str, Item_Result] = {}
    """Mapping between an item result class and the query type it supports."""

    @classmethod
    def register(cls, name: str) -> Callable:
        """Register a specific item result class with the name of a result type.

        Parameters
        ----------
        name
            Name of the result type to register.

        Returns
        -------
        Callable
            Function that's being decorated.
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
    def create_impacted_substances_result(
        cls, result_type_name: str, result_with_impacted_substances: Result_Model_Any
    ) -> "ImpactedSubstancesResultMixin":
        """Return a specific impacted substances result.

        Parameters
        ----------
        result_type_name
            Name of the result for which an object is needed.
        result_with_impacted_substances
            Result from the REST API describing the impacted substances for this particular item.

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
            # This is a BoM-type query result, and has no record reference
            item_result = item_result_class(legislations=result_with_impacted_substances.legislations)
        return item_result

    @classmethod
    @overload
    def create_compliance_result(
        cls,
        result_type_name: str,
        result_with_compliance: Result_Model_Material,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ) -> "MaterialWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls,
        result_type_name: str,
        result_with_compliance: Result_Model_Part,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ) -> "PartWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls,
        result_type_name: str,
        result_with_compliance: Result_Model_Specification,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ) -> "SpecificationWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls,
        result_type_name: str,
        result_with_compliance: Result_Model_Coating,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ) -> "CoatingWithComplianceResult":
        ...

    @classmethod
    @overload
    def create_compliance_result(  # type: ignore[misc]
        cls,
        result_type_name: str,
        result_with_compliance: Result_Model_Substance,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ) -> "SubstanceWithComplianceResult":
        ...

    @classmethod
    def create_compliance_result(
        cls,
        result_type_name: str,
        result_with_compliance: Result_Model_Any,
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
    ) -> "ComplianceResultMixin":
        """Returns a specific item result.

        Parameters
        ----------
        result_type_name
            Name of the result for which an object is needed.
        result_with_compliance
            Result from the REST API describing the compliance for this particular item.
        indicator_definitions
            Definitions of the indicators supplied to the original query. This is required because
            the REST API does not provide them in the response.

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
        """Parse the ``reference_type`` returned by the low-level API into a ``ReferenceType``.

        Parameters
        ----------
        reference_type
            Type of record reference returned from the API for a particular result.

        Returns
        -------
        ReferenceType
            Specific enum value for the ``reference_type`` string.

        Raises
        ------
        KeyError
            If the `reference_type` returned by the low-level API doesn't appear in ``ReferenceType``.
        """

        try:
            return ReferenceType[reference_type]
        except KeyError as e:
            raise KeyError(f"Unknown reference_type {reference_type} " f"returned.").with_traceback(e.__traceback__)


class ImpactedSubstance(BaseSubstanceReference):
    """Represents a substance impacted by a legislation. This object includes two categories of
    attributes:

      - The reference to the substance in Granta MI. These attributes are all populated if data for them exists in
        Granta MI.
      - The amount of the substance in the parent item and the threshold above which it is impacted.

    Attributes
    ----------
    cas_number : str, optional
    ec_number : str, optional
    chemical_name : str, optional
    record_history_identity : int, optional
    record_history_guid : str, optional
    record_guid : str, optional
    max_percentage_amount_in_material : float, optional
        Maximum amount this material can occur in the BoM item that it is declared against. This value is measured in
        wt. % and only populated if present in the declaration in Granta MI.
    legislation_threshold : float, optional
        Threshold above which the substance is impacted by the legislation. This value is measured in wt. % and is only
        populated if defined on the substance in Granta MI.

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
            Type of the record reference value.
        reference_value
            Value of the record reference. All are strings except for record history identities, which are integers.
        max_percentage_amount_in_material
            Amount of this substance that occurs in the parent material. In the case where a range is specified in
             the declaration, only the maximum is reported here.
        legislation_threshold
            Substance concentration threshold over which the material is non-compliant with the legislation.
        """

        super().__init__(
            reference_type=reference_type,
            reference_value=reference_value,
        )
        self.max_percentage_amount_in_material: Optional[float] = max_percentage_amount_in_material
        """Amount of this substance that occurs in the parent material. In the case where a range is specified in
        the declaration, only the maximum is reported here. ``None`` means that the percentage amount has not been
        specified, not that the amount is 0 %."""

        self.legislation_threshold: Optional[float] = legislation_threshold
        """Substance concentration threshold over which the material is non-compliant with the legislation. ``None``
        means that the threshold has not been specified, not that the threshold is 0 %."""

    def __repr__(self) -> str:
        return (
            f'<ImpactedSubstance: {{"cas_number": "{self.cas_number}", '
            f'"percent_amount": {self.max_percentage_amount_in_material}}}>'
        )


if TYPE_CHECKING:
    mixin_base_class = PartDefinition
else:
    mixin_base_class = object


class ImpactedSubstancesResultMixin(mixin_base_class):
    """Adds results from an impacted substances query to an ``ItemDefinition`` class, turning it into an
    ``ItemWithImpactedSubstancesResult`` class.

    This class is an extension to the constructor only. It doesn't implement any additional methods.
    """

    def __init__(
        self,
        legislations: List[models.CommonLegislationWithImpactedSubstances],
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        legislations
            Substances that are found in the ``ItemDefinition`` item for the specified legislations.
        **kwargs
            Contains the ``reference_type`` and ``reference_value`` for ``RecordDefinition``-based objects.
            It is empty for ``BoM1711Definition``-based objects.
        """

        super().__init__(**kwargs)

        self._substances_by_legislation: Dict[str, List[ImpactedSubstance]] = {}

        for legislation in legislations:
            new_substances = [
                self._create_impacted_substance(substance) for substance in legislation.impacted_substances
            ]
            self._substances_by_legislation[legislation.legislation_name] = new_substances

    @staticmethod
    def _create_impacted_substance(
        substance: models.CommonImpactedSubstance,
    ) -> ImpactedSubstance:

        """Create an ``ImpactedSubstance`` result object based on the corresponding object returned from the low-level
        API.

        Parameters
        ----------
        substance
            Impacted substance result object that the low-level API is to return.

        Returns
        -------
        impacted_substance
            Corresponding object in this API.
        """

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
                "of the base BoM Analytics package."
            )
        impacted_substance = ImpactedSubstance(
            max_percentage_amount_in_material=substance.max_percentage_amount_in_material,
            legislation_threshold=substance.legislation_threshold,
            reference_type=reference_type,
            reference_value=reference_value,
        )
        impacted_substance.ec_number = substance.ec_number
        impacted_substance.cas_number = substance.cas_number
        impacted_substance.chemical_name = substance.substance_name
        return impacted_substance

    @property
    def substances_by_legislation(self) -> Dict[str, List[ImpactedSubstance]]:
        return self._substances_by_legislation

    @property
    def substances(self) -> List[ImpactedSubstance]:
        results = []
        for legislation_result in self.substances_by_legislation.values():
            results.extend(legislation_result)
        return results

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}({self.record_reference}), {len(self.substances_by_legislation)} legislations>"
        )


@ItemResultFactory.register("MaterialWithImpactedSubstances")
class MaterialWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, MaterialDefinition):
    """Retrieves an individual material that is included as part of an impacted substances query result.
    This object includes two categories of attributes:

      - The reference to the material in Granta MI
      - The impacted substances associated with this material, both as a flat list and separated by legislation

    Attributes
    ----------
    record_history_identity : int, optional
    material_id : str, optional
    record_history_guid : str, optional
    record_guid : str, optional
    substances_by_legislation : dict[str, list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]]
        Substances impacted for a particular material, grouped by legislation name.
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]
        Substances impacted for a particular material as a flattened list.

    Notes
    -----
    With the exception of ``record_history_identity``, the record reference attributes below are only populated if
    they were specified in the original query.

    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.

    Examples
    --------
    >>> result: MaterialImpactedSubstancesQueryResult
    >>> material_result = result.impacted_substances_by_material[0]
    >>> material_result.substances_by_legislation
    {'California Proposition 65 List': [<ImpactedSubstance: {"cas_number": 90481-04-2}>]}

    >>> result: MaterialImpactedSubstancesQueryResult
    >>> material_result = result.impacted_substances_by_material[0]
    >>> material_result.substances
    [<ImpactedSubstance: {"cas_number": 90481-04-2}>]
    """


@ItemResultFactory.register("PartWithImpactedSubstances")
class PartWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, PartDefinition):
    """Retrieves an individual part included as part of an impacted substances query result. This object includes
    two categories of attributes:

      - The reference to the part in Granta MI
      - The impacted substances associated with this part, both as a flat list and separated by legislation

    Attributes
    ----------
    record_history_identity : list, optional
    part_number : str, optional
    record_history_guid : str, optional
    record_guid : str, optional
    substances_by_legislation : dict[str, list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]]
        Substances impacted for a particular part, grouped by legislation name.
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]
        Substances impacted for a particular part as a flattened list.

    Notes
    -----
    With the exception of ``record_history_identity``, the record reference attributes below are only populated if
    they were specified in the original query.

    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.

    Examples
    --------
    >>> result: PartImpactedSubstancesQueryResult
    >>> part_result = result.impacted_substances_by_part[0]
    >>> part_result.substances_by_legislation
    {'California Proposition 65 List': [<ImpactedSubstance: {"cas_number": 90481-04-2}>]}

    >>> result: PartImpactedSubstancesQueryResult
    >>> part_result = result.impacted_substances_by_part[0]
    >>> part_result.substances
    [<ImpactedSubstance: {"cas_number": 90481-04-2}>]
    """


@ItemResultFactory.register("SpecificationWithImpactedSubstances")
class SpecificationWithImpactedSubstancesResult(ImpactedSubstancesResultMixin, SpecificationDefinition):
    """Retrieves an individual specification included as part of an impacted substances query result.
    This object includes two categories of attributes:

      - The reference to the specification in Granta MI
      - The impacted substances associated with this specification, both as a flat list and separated by legislation

    Attributes
    ----------
    record_history_identity : list, optional
    specification_id : str, optional
    record_history_guid : str, optional
    record_guid : str, optional
    substances_by_legislation : dict[str, list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]]
        Substances impacted for a particular specification, grouped by legislation name.
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]
        Substances impacted for a particular specification as a flattened list.

    Notes
    -----
    With the exception of ``record_history_identity``, the record reference attributes below are only populated if
    they were specified in the original query.

    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.

    Examples
    --------
    >>> result: SpecificationImpactedSubstancesQueryResult
    >>> specification_result = result.impacted_substances_by_specification[0]
    >>> specification_result.substances_by_legislation
    {'California Proposition 65 List': [<ImpactedSubstance: {"cas_number": 90481-04-2}>]}

    >>> result: SpecificationImpactedSubstancesQueryResult
    >>> specification_result = result.impacted_substances_by_specification[0]
    >>> specification_result.substances
    [<ImpactedSubstance: {"cas_number": 90481-04-2}>]
    """

    pass


@ItemResultFactory.register("BomWithImpactedSubstances")
class BoM1711WithImpactedSubstancesResult(ImpactedSubstancesResultMixin):
    """This class is instantiated, but since a BoM query can only return a single Impacted Substances result,
    this type is hidden and never seen by the user. As a result it is not documented.

    An individual BoM included as part of an impacted substances query result. This object includes only the impacted
    substances associated with the BoM, both as a flat list and separated by legislation. There is no item representing
    this BoM in Granta MI, and so there are no records to reference.

    Attributes
    ----------
    substances_by_legislation : dict[str, list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]]
        Substances impacted for a particular item, grouped by legislation name.
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.ImpactedSubstance`]
        Substances impacted for a particular item as a flattened list.

    Notes
    -----
    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(), {len(self.substances_by_legislation)} legislations>"


class ComplianceResultMixin(mixin_base_class):
    """Adds results from a compliance query to a class deriving from ``ItemDefinition``, turning it into an
    ``[ItemType]WithComplianceResult`` class.

    A compliance query returns a BoM-like results, with indicator results attached to each level of the BoM.
    (For more information, see the notes.) This mixin implements only the indicator results for a given item.
    Separate mixins instantiate and add the child items to the parent.

    Parameters
    ----------
    indicator_results
        Compliance of the ``ItemDefinition`` item for the specified indicators. This parameter does not include
        the full indicator definition, only the indicator name.
    indicator_definitions
        Used as a base to create the indicator results for both this item and the child substances.
    **kwargs
        Contains the ``reference_type`` and ``reference_value`` for ``RecordDefinition``-based objects. It is
        empty for ``BoM1711Definition``-based objects.

    Notes
    -----
    BoMs are recursively defined structures. The top-level item is always a 'Part'. 'Parts' can
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

    In addition to these items described above, a compliance query result adds ``Indicator`` objects to all items at
    every level.

    This mixin is applied to ``ItemDefinition`` objects to turn them into ``ItemWithCompliance`` objects, where
    'item' is a 'Part', 'Specification', 'Material', 'Coating', or 'Substance'.
    """

    _definition = None  # Required for linter, is supplied by the main RecordDefinition-derived class

    def __init__(
        self,
        indicator_results: List[models.CommonIndicatorResult],
        indicator_definitions: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._indicator_definitions = indicator_definitions
        self.indicators: Dict[str, Union["WatchListIndicator", "RoHSIndicator"]] = deepcopy(indicator_definitions)

        for indicator_result in indicator_results:
            self.indicators[indicator_result.name].flag = indicator_result.flag

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.record_reference}), {len(self.indicators)} indicators>"


if TYPE_CHECKING:
    child_base_class = ComplianceResultMixin
else:
    child_base_class = object


class ChildSubstanceWithComplianceMixin(child_base_class):
    """Adds a ``substance`` attribute to an ``ItemWithComplianceResult`` class and populates it with child substances.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_substances
        Materials returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._substances: List[SubstanceWithComplianceResult] = []

    @property
    def substances(self) -> List["SubstanceWithComplianceResult"]:
        """Substance compliance result objects that are direct children of this item in the BoM.

        Examples
        --------
        >>> material_result: MaterialWithComplianceResult
        >>> material_result.substances
        [SubstanceWithComplianceResult({"MiRecordHistoryIdentity": 77107}),
                1 indicators>, ...]
        """

        return self._substances

    def _add_child_substances(self, child_substances: List[models.CommonSubstanceWithCompliance]) -> None:
        """Populate the ``substances`` attribute based on a provided list of low-level API substance with compliance
        results.

        Parameters
        ----------
        child_substances
            List of substances with compliance returned from the low-level API.
        """

        for child_substance in child_substances:
            child_substance_with_compliance = ItemResultFactory.create_compliance_result(
                result_type_name="SubstanceWithCompliance",
                result_with_compliance=child_substance,
                indicator_definitions=self._indicator_definitions,
            )
            self._substances.append(child_substance_with_compliance)


class ChildMaterialWithComplianceMixin(child_base_class):
    """Adds a ``material`` attribute to an ``ItemWithComplianceResult`` class and populates it with child materials.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_materials
        Materials returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._materials: List[MaterialWithComplianceResult] = []

    @property
    def materials(self) -> List["MaterialWithComplianceResult"]:
        """Material compliance result objects that are direct children of this part or specification in the BoM.

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
        child_materials: List[models.CommonMaterialWithCompliance],
    ) -> None:
        """Populates the ``materials`` attribute based on a provided list of low-level API materials with compliance
        results.

        This method operates recursively, adding any substances with compliance that are children of each material.

        Parameters
        ----------
        child_materials
            List of materials with compliance returned from the low-level API.
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
    """Adds a '`specification`' attribute to an ``ItemWithComplianceResult`` class and populates it with child
    specifications.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_specifications
        Specifications returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._specifications: List[SpecificationWithComplianceResult] = []

    @property
    def specifications(self) -> List["SpecificationWithComplianceResult"]:
        """Specification compliance result objects that are direct children of this item in the BoM.

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
        child_specifications: List[models.CommonSpecificationWithCompliance],
    ) -> None:
        """Populate the ``specifications`` attribute based on a provided list of low-level API specifications with
        compliance results.

        This method operates recursively, adding any specifications, materials, coatings, and substances with compliance
        that are children of each specification.

        Parameters
        ----------
        child_specifications
            List of specifications with compliance returned from the low-level API
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
    """Adds a ``part`` attribute to an ``ItemWithComplianceResult`` class and populates it with child parts.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_parts
        Parts returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._parts: List[PartWithComplianceResult] = []

    @property
    def parts(self) -> List["PartWithComplianceResult"]:
        """Part compliance result objects that are direct children of this part in the BoM.

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
        child_parts: List[models.CommonPartWithCompliance],
    ) -> None:
        """Populate the ``parts`` attribute based on a provided list of low-level API parts with compliance
        results.

        Operates recursively, adding any parts, materials, coatings, and substances with compliance
        that are children of each part.

        Parameters
        ----------
        child_parts
           List of parts with compliance returned from the low-level API
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
    """Adds a ``coating`` attribute to an ``ItemWithComplianceResult`` class and populates it with child coatings.

    See the ``ComplianceResultMixin`` notes for more background on compliance query results and BoM structures.

    Parameters
    ----------
    child_coatings
         Coatings returned by the low-level API that are children of this item.
    **kwargs
        Contains other result objects depending on the parent item. It contains record references for
        ``RecordDefinition``-based objects.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._coatings: List[CoatingWithComplianceResult] = []

    @property
    def coatings(self) -> List["CoatingWithComplianceResult"]:
        """Coating result objects that are direct children of this specification in the BoM.

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
        child_coatings: List[models.CommonCoatingWithCompliance],
    ) -> None:
        """Populate the ``coatings`` attribute based on a provided list of low-level API coatings with compliance
        results.

        Operates recursively, adding any substances with compliance that are children of each coating.

        Parameters
        ----------
        child_coatings
            List of coatings with compliance returned from the low-level API.
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
    """Retrieves an individual substance included as part of a compliance query result.
    This object includes two categories of attributes:

      - The reference to the substance in Granta MI
      - The compliance status of this substance, stored in a dictionary of one or more indicator objects

    Attributes
    ----------
    record_history_identity : int, optional
    cas_number : str, optional
    ec_number : str, optional
    chemical_name : str, optional
    record_history_guid : str, optional
    record_guid : str, optional
    indicators : dict[str, |WatchListIndicator| | |RoHSIndicator|]
        Compliance status of this item for each indicator included in the original query.

    Notes
    -----
    The record reference attributes below are only populated if they were specified in the original query.

    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.
    """


@ItemResultFactory.register("MaterialWithCompliance")
class MaterialWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, MaterialDefinition):
    """Retrieves an individual material included as part of a compliance query result.
    This object includes three categories of attributes:

      - The reference to the material in Granta MI
      - The compliance status of this material, stored in a dictionary of one or more indicator objects
      - Any substance objects that are a child of this material object

    Attributes
    ----------
    record_history_identity : int, optional
    material_id : str, optional
    record_history_guid : str, optional
    record_guid : str, optional
    indicators : dict[str, |WatchListIndicator| | |RoHSIndicator|]
        Compliance status of this item for each indicator included in the original query.
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.SubstanceWithComplianceResult`]

    Notes
    -----
    With the exception of ``record_history_identity``, the record reference attributes below are only populated if
    they were specified in the original query. As a result, if this object is included as the child of another
    compliance result object, only ``record_history_identity`` will be populated.

    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.
    """


@ItemResultFactory.register("PartWithCompliance")
class PartWithComplianceResult(
    ChildPartWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSubstanceWithComplianceMixin,
    ComplianceResultMixin,
    PartDefinition,
):
    """Retrieves an individual part included as part of a compliance query result.
    This object includes three categories of attributes:

      - The reference to the part in Granta MI (if the part references a record)
      - The compliance status of this part, stored in a dictionary of one or more indicator objects
      - Any part, specification, material, or substance objects which are a child of this part object

    Attributes
    ----------
    record_history_identity : int, optional
    part_number : str, optional
    record_history_guid : str, optional
    record_guid : str, optional
    indicators : dict[str, |WatchListIndicator| | |RoHSIndicator|]
        Compliance status of this item for each indicator included in the original query.
    parts : list[:class:`~ansys.grantami.bomanalytics._item_results.PartWithComplianceResult`]
    specifications : list[:class:`~ansys.grantami.bomanalytics._item_results.SpecificationWithComplianceResult`]
    materials : list[:class:`~ansys.grantami.bomanalytics._item_results.MaterialWithComplianceResult`]
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.SubstanceWithComplianceResult`]

    Notes
    -----
    With the exception of ``record_history_identity``, the record reference attributes below are only populated if
    they were specified in the original query. As a result, if this object is included as the child of another
    compliance result object, only ``record_history_identity`` will be populated.

    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.
    """


@ItemResultFactory.register("SpecificationWithCompliance")
class SpecificationWithComplianceResult(
    ChildCoatingWithComplianceMixin,
    ChildSpecificationWithComplianceMixin,
    ChildMaterialWithComplianceMixin,
    ChildSubstanceWithComplianceMixin,
    ComplianceResultMixin,
    SpecificationDefinition,
):
    """Retrieves an individual specification included as part of a compliance query result.
    This object includes three categories of attributes:

      - The reference to the specification in Granta MI
      - The compliance status of this specification, stored in a dictionary of one or more indicator objects
      - Any specification, material, coating, or substance objects which are a child of this specification object

    Attributes
    ----------
    record_history_identity : int, optional
    specification_id : Optional[str]
    record_history_guid : Optional[str]
    record_guid : Optional[str]
    indicators : dict[str, |WatchListIndicator| | |RoHSIndicator|]
        The compliance status of this item for each indicator included in the original query.
    specifications : list[:class:`~ansys.grantami.bomanalytics._item_results.SpecificationWithComplianceResult`]
    materials : list[:class:`~ansys.grantami.bomanalytics._item_results.MaterialWithComplianceResult`]
    coatings : list[:class:`~ansys.grantami.bomanalytics._item_results.CoatingWithComplianceResult`]
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.SubstanceWithComplianceResult`]

    Notes
    -----
    With the exception of ``record_history_identity``, the record reference attributes below are only populated if
    they were specified in the original query. As a result, if this object is included as the child of another
    compliance result object, only ``record_history_identity`` will be populated.

    Objects of this class are only returned as the result of a query; the class is not intended to be instantiated
    directly.
    """


@ItemResultFactory.register("CoatingWithCompliance")
class CoatingWithComplianceResult(ChildSubstanceWithComplianceMixin, ComplianceResultMixin, CoatingReference):
    """An individual coating included as part of a compliance query result. This object includes three
    categories of attributes:

      - The reference to the coating in Granta MI
      - The compliance status of this coating, stored in one or more indicator objects
      - Any substance objects which are a child of this coating object

    Attributes
    ----------
    record_history_identity : int, optional
        Default reference type for compliance items returned as children of the queried item.
    indicators : dict[str, |WatchListIndicator| | |RoHSIndicator|]
        Compliance status of this item for each indicator included in the original query.
    substances : list[:class:`~ansys.grantami.bomanalytics._item_results.SubstanceWithComplianceResult`]

    Notes
    -----
    Objects of this class are only returned as the result of a query. The class is not intended to be instantiated
    directly.
    """
