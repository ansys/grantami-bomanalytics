"""BoM Analytics indicators.

There are two indicators supported by the BoM Analytics API. Each is implemented as a separate class. They are their
own result, i.e. all that is needed to convert a definition to a result is to add a result flag.

Notes
-----
Indicators define compliance in terms of one or more legislations and a concentration threshold. The flags (states) of
an indicator represent the compliance status of that indicator against a certain substance, material, specification,
or part.
"""

from enum import Enum
from abc import ABC
from typing import List, Union, Optional, TYPE_CHECKING

from ansys.grantami.bomanalytics_codegen import models

if TYPE_CHECKING:
    from ._query_results import MaterialComplianceQueryResult  # noqa: F401
    from .queries import MaterialComplianceQuery  # noqa: F401


class _Flag(Enum):
    """Base class for flags (result states) of indicators.

    Implements `__le__` , but relies on specific flag classes to implement other overloads to allow direct comparisons
    with the containing Indicator.

    Overrides `__new__` to populate the __doc__ on an enum member.
    """

    def __new__(cls, value: int, doc: str) -> "_Flag":
        obj = object.__new__(cls)
        obj._value_ = value
        obj.__doc__ = doc
        return obj

    def __le__(self, other):
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            If the other object is an indicator and has no value.
        TypeError
            If the other object isn't this flag's type or this flag's indicator's type.
        """

        return self.__eq__(other) or self < other


class RoHSFlag(_Flag):
    """Permitted RoHS flag states. Increasing value means 'worse' compliance, i.e. the compliance result is worse the
    further down the list the result appears.

    See the Restricted Substances User Guide (available on the Ansys customer download site) for more details.
    """

    RohsNotImpacted = (
        1,
        """This substance is not impacted by the specified legislations. *Substance is not
    impacted.*""",
    )
    RohsBelowThreshold = (
        2,
        """This substance is impacted by the specified legislations, but appears in the parent item
    in a quantity below that specified by the indicator. *Substance is below threshold.*""",
    )
    RohsCompliant = (
        3,
        """This item either does not contain any substances impacted by the specified legislations, or
    contains no substances above the specified threshold. *Item is compliant.*""",
    )
    RohsCompliantWithExemptions = (
        4,
        """This item contains substances impacted by the specified legislations, but an
    exemption has been declared either on itself or a child item. *Item is compliant with exemptions.*""",
    )
    RohsAboveThreshold = (
        5,
        """This substance is impacted by the specified legislations and is present in a quantity
    above that specified by the indicator. *Exemption for use required.*""",
    )
    RohsNonCompliant = (
        6,
        """This item contains one or more substances impacted by the specified legislations. *Item is
    non-compliant.*""",
    )
    RohsUnknown = (
        7,
        """One or more declarations are missing, and so there is not enough information to determine
    compliance. *Compliance is unknown.*""",
    )

    def __lt__(self, other):
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            If the other object is an indicator and has no value.
        TypeError
            If the other object isn't this flag's type or this flag's indicator's type.
        """

        if self.__class__ is other.__class__:
            return self.value < other.value
        elif isinstance(other, RoHSIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                return self.value < other.flag.value
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")

    def __eq__(self, other):
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            If the other object is an indicator and has no value.
        TypeError
            If the other object isn't this flag's type or this flag's indicator's type.
        """

        if self.__class__ is other.__class__:
            return self is other
        elif isinstance(other, RoHSIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                return self is other.flag
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")


class WatchListFlag(_Flag):
    """Permitted Watch List flag states. Increasing value means 'worse' compliance, i.e. the compliance result is worse
    the further down the list the result appears.

    See the Restricted Substances User Guide (available on the Ansys customer download site) for more details.
    """

    WatchListNotImpacted = (
        1,
        """This substance is not impacted by the specified legislations. *Substance is not
    impacted.*""",
    )
    WatchListCompliant = (
        2,
        """This item does not contain any substances impacted by the specified legislations. *Item
    is compliant.*""",
    )
    WatchListBelowThreshold = (
        3,
        """This substance is impacted by the specified legislations, but appears in the parent
    item in a quantity below that specified by the indicator. *Substance is below threshold.*""",
    )
    WatchListAllSubstancesBelowThreshold = (
        4,
        """This item contains no substances above the specified threshold.
    *Item is compliant.*""",
    )
    WatchListAboveThreshold = (
        5,
        """This substance is impacted by the specified legislations and appears in the parent
    item in a quantity above that specified by the indicator. *Substance is impacted.*""",
    )
    WatchListHasSubstanceAboveThreshold = (
        6,
        """This item contains one or more substances impacted by the specified
    legislations. *Item is non-compliant.*""",
    )
    WatchListUnknown = 7, """There is not enough information to determine compliance. *Compliance is unknown.*"""

    def __lt__(self, other):
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            If the other object is an indicator and has no value.
        TypeError
            If the other object isn't this flag's type or this flag's indicator's type.
        """

        if self.__class__ is other.__class__:
            return self.value < other.value
        elif isinstance(other, WatchListIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                return self.value < other.flag.value
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")

    def __eq__(self, other):
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            If the other object is an indicator and has no value.
        TypeError
            If the other object isn't this flag's type or this flag's indicator's type.
        """

        if self.__class__ is other.__class__:
            return self is other
        elif isinstance(other, WatchListIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                return self is other.flag
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")


class _Indicator(ABC):
    """Base class for all indicators.

    Allows for comparison of same-typed indicators that both have results.
    """

    available_flags = None

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        self.name: str = name
        self.legislation_names: List[str] = legislation_names
        self.default_threshold_percentage: float = default_threshold_percentage
        self._indicator_type: Union[str, None] = None
        self._flag: Union[_Flag, None] = None

    @property
    def _definition(self):
        """The low-level API representation of this Indicator."""
        return models.GrantaBomAnalyticsServicesInterfaceCommonIndicatorDefinition(
            name=self.name,
            legislation_names=self.legislation_names,
            default_threshold_percentage=self.default_threshold_percentage,
            type=self._indicator_type,
        )

    def __repr__(self):
        if not self._flag:
            return f"<{self.__class__.__name__}, name: {self.name}>"
        else:
            return f"<{self.__class__.__name__}, name: {self.name}, flag: {str(self.flag)}>"

    def __str__(self):
        result = self.name
        if self.flag:
            result = f"{result}, {self.flag.name}"
        return result

    @property
    def flag(self) -> _Flag:
        """The state of this indicator. If the indicator is a definition only, this property is `None`.

        Raises
        ------
        KeyError
            If the value being set is not valid for this Indicator.
        """
        return self._flag

    @flag.setter
    def flag(self, flag: str):
        try:
            self._flag: _Flag = self.__class__.available_flags[flag]
        except KeyError as e:
            raise KeyError(f'Unknown flag "{flag}" for indicator "{repr(self)}"').with_traceback(e.__traceback__)

    def __eq__(self, other):
        """Allows comparison both to another indicator and to a flag of the correct type for the concrete class.

        Raises
        ------
        ValueError
            If either this indicator or the other indicator has no value.
        TypeError
            If the other object isn't this indicator's type or this indicator's flag's type.
        """

        if not self.flag:
            raise ValueError(f"Indicator {str(self)} has no flag, so cannot be compared")
        if isinstance(other, self.available_flags):
            return self.flag is other
        if self.__class__ is not other.__class__:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        if self.flag and other.flag:
            return self.flag is other.flag
        elif not other.flag:
            raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")

    def __lt__(self, other):
        """Allows comparison both to another indicator and to a flag of the correct type for the concrete class.

        Raises
        ------
        ValueError
            If either this indicator or the other indicator has no value.
        TypeError
            If the other object isn't this indicator's type or this indicator's flag's type.
        """

        if not self.flag:
            raise ValueError(f"Indicator {str(self)} has no flag, so cannot be compared")
        if isinstance(other, self.available_flags):
            return self.flag < other
        if self.__class__ is not other.__class__:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        if self.flag and other.flag:
            return self.flag < other.flag
        else:
            raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")

    def __le__(self, other):
        """Allows comparison both to another indicator and to a flag of the correct type for the concrete class.

        Raises
        ------
        ValueError
            If either this indicator or the other indicator has no value.
        TypeError
            If the other object isn't this indicator's type or this indicator's flag's type.
        """

        return self == other or self < other


class RoHSIndicator(_Indicator):  # TODO Think about the class hierarchy here, IndicatorDefinition vs Result
    """Indicator object that represents RoHS-type compliance of a BoM object against one or more legislations.

    Other `RoHSIndicator` objects with results can be compared, with 'less compliant' indicators being greater than
    'more compliant' indicators.

    Parameters
    ----------
    name
        The name of the indicator. Used to identify the indicator in the query result.
    legislation_names
        The legislations against which compliance will be determined.
    default_threshold_percentage
        The concentration of substance that will be determined to be non-compliant. Is only used if the legislation
        doesn't define a specific threshold for the substance.

    Raises
    ------
    TypeError
        If two differently-typed indicators are compared
    ValueError
        If two indicators are compared which both don't have a result flag

    Examples
    --------
    >>> indicator = RoHSIndicator(name='RoHS substances',
    ...                           legislation_names=["EU Directive 2011/65/EU (RoHS 2)"],
    ...                           default_threshold_percentage=0.1)
    >>> indicator
    <RoHSIndicator, name: Tracked substances>

    >>> query = MaterialComplianceQuery.with_indicators([indicator])...
    >>> result: MaterialComplianceQueryResult  # Perform a compliance query
    >>> indicator_result = result.compliance_by_material_and_indicator[0]['RoHS substances']
    >>> indicator_result.flag >= indicator.available_flags['RohsCompliantWithExemptions']
    True  # The material is not compliant with the legislations in the indicator
    """

    available_flags = RoHSFlag

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Optional[float] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type: str = "Rohs"
        self._flag: Optional[RoHSFlag] = None


class WatchListIndicator(_Indicator):
    """Indicator object that represents Watch List-type compliance of a BoM object against one or more legislations.

    Other `WatchListIndicator` objects with results can be compared, with 'less compliant' indicator flagas being
    greater than 'more compliant' indicator flags.

    Parameters
    ----------
    name
        The name of the indicator. Used to identify the indicator in the query result.
    legislation_names
        The legislations against which compliance will be determined.
    default_threshold_percentage
        The concentration of substance that will be determined to be non-compliant. Is only used if the legislation
        doesn't define a specific threshold for the substance.

    Raises
    ------
    TypeError
        If two differently-typed indicators are compared
    ValueError
        If two indicators are compared which both don't have a result flag

    Examples
    --------
    >>> indicator = RoHSIndicator(name='Tracked substances',
    ...                           legislation_names=["The SIN List 2.1 (Substitute It Now!)"],
    ...                           default_threshold_percentage=0.1)
    >>> indicator
    <WatchListIndicator, name: Tracked substances>

    >>> query = MaterialComplianceQuery.with_indicators([indicator])...
    >>> result: MaterialComplianceQueryResult  # Perform a compliance query
    >>> indicator_result = result.compliance_by_material_and_indicator[0]['Tracked substances']
    >>> indicator_result.flag >= indicator.available_flags['WatchListAllSubstancesBelowThreshold']
    True  # The material is not compliant with the legislations in the indicator
    """

    available_flags = WatchListFlag

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Optional[float] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type: str = "WatchList"
        self._flag: Optional[WatchListFlag] = None
