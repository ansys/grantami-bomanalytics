from enum import Enum, auto
from abc import ABC
from typing import List, Union, Dict

from ansys.granta.bomanalytics import models

Indicator_Definitions = Dict[str, Union["WatchListIndicator", "RoHSIndicator"]]


class _Flag(Enum):
    def __lt__(self, other):
        return self.value < other.value


class RoHSFlag(_Flag):
    RohsNotImpacted = auto()
    RohsBelowThreshold = auto()
    RohsCompliant = auto()
    RohsCompliantWithExemptions = auto()
    RohsAboveThreshold = auto()
    RohsNonCompliant = auto()
    RohsUnknown = auto()


class WatchListFlag(_Flag):
    WatchListNotImpacted = auto()
    WatchListCompliant = auto()
    WatchListBelowThreshold = auto()
    WatchListAllSubstancesBelowThreshold = auto()
    WatchListAboveThreshold = auto()
    WatchListHasSubstanceAboveThreshold = auto()
    WatchListUnknown = auto()


class _Indicator(ABC):
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
    available_flags = WatchListFlag

    def __init__(
        self,
        name: str,
        legislation_names: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        super().__init__(name, legislation_names, default_threshold_percentage)
        self._indicator_type: str = "WatchList"
