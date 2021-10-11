"""Bom Analytics indicators.

There are two indicators supported by the Bom Analytics API. Each is implemented as a separate class. They are their
own result, i.e. all that is needed to convert a definition to a result is to add a result flag.

Attributes
----------
Indicator_Definitions : TypeVar
    A shorthand for the `dict` of indicator definitions, used elsewhere in this package.

Notes
-----
Indicators define compliance in terms of one or more legislations and a concentration threshold. The flags (states) of
an indicator represent the compliance status of that indicator against a certain substance, material, specification,
or part.

"""

from enum import Enum, auto
from abc import ABC
from typing import List, Union, Dict

from ansys.granta.bomanalytics import models

Indicator_Definitions = Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]


class _Flag(Enum):
    """Base class for flags (result states) of indicators.

    Implements `__lt__`, allowing comparison of enum values.
    """

    def __lt__(self, other):
        return self.value < other.value


class RoHSFlag(_Flag):
    """Permitted RoHS flag states. Increasing value means 'worse' compliance."""

    RohsNotImpacted = auto()
    RohsBelowThreshold = auto()
    RohsCompliant = auto()
    RohsCompliantWithExemptions = auto()
    RohsAboveThreshold = auto()
    RohsNonCompliant = auto()
    RohsUnknown = auto()


class WatchListFlag(_Flag):
    """Permitted Watch List flag states. Increasing value means 'worse' compliance."""

    WatchListNotImpacted = auto()
    WatchListCompliant = auto()
    WatchListBelowThreshold = auto()
    WatchListAllSubstancesBelowThreshold = auto()
    WatchListAboveThreshold = auto()
    WatchListHasSubstanceAboveThreshold = auto()
    WatchListUnknown = auto()


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
    def definition(self):
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
        """The state of this indicator. If the indicator is a definition, the flag is `None`."""
        return self._flag

    @flag.setter
    def flag(self, flag: str):
        try:
            self._flag: _Flag = self.__class__.available_flags[flag]
        except KeyError as e:
            raise KeyError(f'Unknown flag "{flag}" for indicator "{repr(self)}"').with_traceback(e.__traceback__)

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        if self.flag and other.flag:
            return self.flag is other.flag
        elif not self.flag:
            raise ValueError(f"Indicator {str(self)} has no flag, so cannot be compared")
        elif not other.flag:
            raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")

    def __lt__(self, other):
        if self.__class__ is not other.__class__:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        if self.flag and other.flag:
            return self.flag < other.flag
        elif not self.flag:
            raise ValueError(f"Indicator {str(self)} has no flag, so cannot be compared")
        elif not other.flag:
            raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")

    def __le__(self, other):
        return self == other or self < other


class RoHSIndicator(_Indicator):  # TODO Think about the class hierarchy here, IndicatorDefinition vs Result
    """Indicator object that represents RoHS-type compliance of a Bom object against one or more legislations.

    Other `RoHSIndicator` objects with results can be compared, with 'less compliant' indicators being greater than
    'more compliant' indicators.

    Parameters
    ----------
    name : str
        The name of the indicator. Used to identify the indicator in the query result.
    legislation_names : list of str
        The legislations against which compliance will be determined.
    default_threshold_percentage : float, optional
        The concentration of substance that will be determined to be non-compliant. Is only used if the legislation
        doesn't define a specific threshold for the substance.

    Class Attributes
    ----------------
    available_flags : RoHSFlag
        The possible results for this Indicator.

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
    <RoHSIndicator, name: Tracked substances>

    >>> ...  # Perform a compliance query

    >>> indicator_result = result.compliance_by_material_and_indicator[0]['RoHS substances']
    >>> indicator_result.flag >= indicator.available_flags['RohsCompliantWithExemptions']
    True  # The material is not compliant with RoHS 2
    """

    available_flags = RoHSFlag

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type: str = "Rohs"


class WatchListIndicator(_Indicator):
    """Indicator object that represents Watch List-type compliance of a Bom object against one or more legislations.

    Other `WatchListIndicator` objects with results can be compared, with 'less compliant' indicators being greater than
    'more compliant' indicators.

    Parameters
    ----------
    name : str
        The name of the indicator. Used to identify the indicator in the query result.
    legislation_names : list of str
        The legislations against which compliance will be determined.
    default_threshold_percentage : float, optional
        The concentration of substance that will be determined to be non-compliant. Is only used if the legislation
        doesn't define a specific threshold for the substance.

    Class Attributes
    ----------------
    available_flags : WatchListFlag
        The possible results for this Indicator.

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
    <WatchListIndicator, name: Tracked substances>

    >>> ...  # Perform a compliance query

    >>> indicator_result = result.compliance_by_material_and_indicator[0]['Tracked substances']
    >>> indicator_result.flag >= indicator.available_flags['WatchListAllSubstancesBelowThreshold']
    True  # The material is not compliant with the SinList
    """

    available_flags = WatchListFlag

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type: str = "WatchList"
