# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""BoM Analytics indicators.

There are two indicators supported by the BoM Analytics API. Each is implemented as a separate class. They are their
own result. All that is needed to convert a definition to a result is to add a result flag.

Notes
-----
Indicators define compliance in terms of one or more legislations and a concentration threshold. The flags (states) of
an indicator represent the compliance status of that indicator against a certain substance, material, specification,
or part.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

from ansys.grantami.bomanalytics_openapi import models

if TYPE_CHECKING:
    from ._query_results import MaterialComplianceQueryResult  # noqa: F401
    from .queries import MaterialComplianceQuery  # noqa: F401


class _Flag(Enum):
    """Base class for flags (result states) of indicators.

    This class implements `__le__` , but it relies on specific flag classes to implement other
    overloads to allow direct comparisons with the containing Indicator.

    Overrides `__new__` to populate the __doc__ on an enum member.
    """

    def __new__(cls, value: int, doc: str) -> "_Flag":
        obj: _Flag = object.__new__(cls)
        obj._value_ = value
        obj.__doc__ = " ".join(doc.split())
        return obj

    @abstractmethod
    def __lt__(self, other: "_Flag") -> bool:
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            Error to raise if the other object is an indicator and has no value.
        TypeError
            Error to raise if the other object isn't this flag's type or this flag's indicator's type.
        """

        pass

    def __le__(self, other: "_Flag") -> bool:
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            Error to raise if the other object is an indicator and has no value.
        TypeError
            Error to raise if the other object isn't this flag's type or this flag's indicator's type.
        """

        return self.__eq__(other) or self < other


class RoHSFlag(_Flag):
    """Provides permitted RoHS flag states.

    A larger value means that the item is less compliant. The further down the list the compliance
    result appears, the worse it is.

    For more information, see the
    :MI_docs:`Restricted Substances Reports User Guide <rs_and_sustainability/restricted_substances.html>`.
    """

    RohsNotImpacted = (
        1,
        """This substance is not impacted by the specified legislations. *Substance is not impacted.*""",
    )
    RohsBelowThreshold = (
        2,
        """This substance is impacted by the specified legislations, but it appears in the parent item in a quantity
        below that specified by the indicator. *Substance is below threshold.*""",
    )
    RohsCompliant = (
        3,
        """This item either does not contain any substances impacted by the specified legislations or contains no
        substances above the specified threshold. *Item is compliant.*""",
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
        """One or more declarations are missing, so there is not enough information to determine compliance.
        *Compliance is unknown.*""",
    )

    def __lt__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            result: bool = self.value < other.value
        elif isinstance(other, RoHSIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                result = self.value < other.flag.value
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        return result

    def __eq__(self, other: object) -> bool:
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            Error to raise if the other object is an indicator and has no value.
        TypeError
            Error to raise if the other object isn't the same type as this flag or this flag's indicator.
        """

        if isinstance(other, self.__class__):
            return self is other
        elif isinstance(other, RoHSIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                return self is other.flag
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")


class WatchListFlag(_Flag):
    """Provides permitted watch list flag states.

    An increasing value means less compliance. The further down the list the compliance result
    appears, the worse it is.

    For more information, see the
    :MI_docs:`Restricted Substances Reports User Guide <rs_and_sustainability/restricted_substances.html>`.
    """

    WatchListNotImpacted = (
        1,
        """This substance is not impacted by the specified legislations. *Substance is not impacted.*""",
    )
    WatchListCompliant = (
        2,
        """This item does not contain any substances impacted by the specified legislations. *Item is compliant.*""",
    )
    WatchListBelowThreshold = (
        3,
        """This substance is impacted by the specified legislations, but appears in the parent
        item in a quantity below that specified by the indicator. *Substance is below threshold.*""",
    )
    WatchListAllSubstancesBelowThreshold = (
        4,
        """This item contains no substances above the specified threshold. *Item is compliant.*""",
    )
    WatchListAboveThreshold = (
        5,
        """This substance is impacted by the specified legislations and appears in the parent
        item in a quantity above that specified by the indicator. *Substance is impacted.*""",
    )
    WatchListHasSubstanceAboveThreshold = (
        6,
        """This item contains one or more substances impacted by the specified legislations. *Item is
        non-compliant.*""",
    )
    WatchListUnknown = (
        7,
        """There is not enough information to determine compliance. *Compliance is unknown.*""",
    )

    def __lt__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            result: bool = self.value < other.value
        elif isinstance(other, WatchListIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                result = self.value < other.flag.value
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        return result

    def __eq__(self, other: object) -> bool:
        """Allows comparison both to another flag and to an indicator that has this flag set as its result.

        Raises
        ------
        ValueError
            Error to raise if the other object is an indicator and has no value.
        TypeError
            Error to raise if the other object isn't this flag's type or this flag's indicator's type.
        """

        if isinstance(other, self.__class__):
            return self is other
        elif isinstance(other, WatchListIndicator):
            if not other.flag:
                raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")
            else:
                return self is other.flag
        else:
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")


class _Indicator(ABC):
    """Provides all indicators.

    This base class allows for comparison of same-typed indicators that both have results.
    """

    available_flags: Type[_Flag]

    def __init__(
        self,
        name: str,
        legislation_ids: List[str],
        default_threshold_percentage: Union[float, None] = None,
    ):
        self.name = name
        self.legislation_ids = legislation_ids
        self.default_threshold_percentage = default_threshold_percentage
        self._indicator_type: Optional[str] = None
        self._flag: Optional[_Flag] = None

    @property
    @abstractmethod
    def _definition(self) -> models.CommonIndicatorDefinition:
        """Generates the low-level API indicator object."""
        pass

    def __repr__(self) -> str:
        if not self._flag:
            return f"<{self.__class__.__name__}, name: {self.name}>"
        else:
            return f"<{self.__class__.__name__}, name: {self.name}, flag: {str(self.flag)}>"

    def __str__(self) -> str:
        result = self.name
        if self.flag:
            result = f"{result}, {self.flag.name}"
        return result

    @property
    def flag(self) -> Optional[_Flag]:
        """State of the indicator. If the indicator is a definition only, this property is set to ``None``.

        Raises
        ------
        KeyError
            Error to raise if the value being set is not valid for this indicator.
        """
        return self._flag

    @flag.setter
    def flag(self, flag: str) -> None:
        try:
            self._flag = self.__class__.available_flags[flag]
        except KeyError as e:
            raise KeyError(f'Unknown flag "{flag}" for Indicator' f' "{repr(self)}"').with_traceback(e.__traceback__)

    def __eq__(self, other: object) -> bool:
        """Allows comparison both to another indicator and to a flag of the correct type for the concrete class.

        Raises
        ------
        ValueError
            Error to raise if either this indicator or the other indicator has no value.
        TypeError
            Error to raise if the other object isn't this indicator's type or this indicator's flag's type.
        """

        if not self.flag:
            raise ValueError(f"Indicator {str(self)} has no flag, so cannot be compared")
        other_flag = self._get_flag_from_object(other)
        return self.flag is other_flag

    def __lt__(self, other: object) -> bool:
        """Allows comparison both to another indicator and to a flag of the correct type for the concrete class.

        Raises
        ------
        ValueError
            Error to raise if either this indicator or the other indicator has no value.
        TypeError
            Error to raise if the other object isn't this indicator's type or this indicator's flag's type.
        """

        if not self.flag:
            raise ValueError(f"Indicator {str(self)} has no flag, so cannot be compared")
        other_flag = self._get_flag_from_object(other)
        return self.flag < other_flag

    def _get_flag_from_object(self, other: object) -> _Flag:
        """Get the flag from the other object, regardless of if it is an indicator or a flag.

        Returns
        -------
        Flag object extracted from ``other``.

        Raises
        ------
        RuntimeError
            Error to raise if an unhandled error occurs during the comparison. A descriptive ``TypeError`` or
            ``ValueError`` should always be raised instead.
        """
        self._check_type_and_value_compatibility(other)
        if isinstance(other, _Indicator) and other.flag:
            flag = other.flag
        elif isinstance(other, _Flag):
            flag = other
        else:
            raise RuntimeError
        return flag

    def _check_type_and_value_compatibility(self, other: object) -> None:
        """Check if the type and value of self and other are compatible such that they can be compared.

        Raises
        ------
        ValueError
            Error to raise if the other indicator has no flag, there is no basis for comparison.
        TypeError
            Error to raise if the other object is a different ``_Indicator`` subtype or an incompatible ``_Flag``
            subtype.
        """
        if isinstance(other, _Indicator) and not isinstance(other, self.__class__):
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        if isinstance(other, _Flag) and not isinstance(other, self.available_flags):
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        if isinstance(other, _Indicator) and not other.flag:
            raise ValueError(f"Indicator {str(other)} has no flag, so cannot be compared")

    def __le__(self, other: object) -> bool:
        """Allows comparison both to another indicator and to a flag of the correct type for the concrete class.

        Raises
        ------
        ValueError
            Error to raise if either this indicator or the other indicator has no value.
        TypeError
            Error to raise if the other object isn't this indicator's type or this indicator's flag's type.
        """

        return self == other or self < other


class RoHSIndicator(_Indicator):
    """Provides the indicator object that represents RoHS-type compliance of a BoM object against one or more
    legislations.

    Other ``RoHSIndicator`` objects with results can be compared, with 'less compliant' indicators being greater than
    'more compliant' indicators.

    Parameters
    ----------
    name : str
        Name of the indicator that is to identify the indicator in the query result.
    legislation_ids : list[str]
        Legislations against which compliance will be determined. Legislations are identified based
        on their ``Legislation ID`` attribute value.

        .. versionadded:: 2.0

        .. important::
           This argument replaces ``legislation_names``, which has been removed in version **2.0**.

           When updating scripts from version **1.x**, replace the ``legislation_names`` argument with the
           ``legislation_ids`` argument and ensure the value provided is a list of ``Legislation ID`` attribute values.
    default_threshold_percentage : float, optional
        Concentration of substance that is to be determined to be non-compliant. The default is ``None``.
        This parameter is only used if the legislation doesn't define a specific threshold for the substance.
    ignore_exemptions : bool, optional
        Whether to consider exemptions added to parts when determining compliance against this indicator.
        The default is ``True``.

    Attributes
    ----------
    available_flags : Type[:class:`~ansys.grantami.bomanalytics.indicators.RoHSFlag`]
        Possible states of this indicator.

    Raises
    ------
    TypeError
        Error to raise if two indicators of different types are compared.
    ValueError
        Error to raise if two indicators are compared and both don't have a result flag.

    Notes
    -----
    The RoHS indicator is designed to be used with RoHS-type legislations such as RoHS and RoHS China. However,
    usage is not enforced. Substances marked as ``Process Chemicals`` [1]_ are always ignored, and exceptions
    are supported (unless explicitly ignored by specifying ``ignore_exemptions=True`` when creating the indicator).
    The possible result flags for the indicator distinguish between an item being compliant, compliant with
    exemptions, or non-compliant.

    Examples
    --------
    >>> indicator = RoHSIndicator(name='RoHS substances',
    ...                           legislation_ids=["RoHS"],
    ...                           default_threshold_percentage=0.1,
    ...                           ignore_exemptions=True)
    >>> indicator
    <RoHSIndicator, name: Tracked substances>

    >>> query = MaterialComplianceQuery.with_indicators([indicator])...
    >>> result: MaterialComplianceQueryResult  # Perform a compliance query
    >>> indicator_result = result.compliance_by_indicator['Tracked substances']
    >>> indicator_result
    <RoHSIndicator, name: Tracked substances, flag: RoHSFlag.RohsNonCompliant>

    >>> indicator_result <= indicator.available_flags['RohsCompliantWithExemptions']
    False  # The material is not compliant with the legislations in the Indicator
    """

    available_flags = RoHSFlag

    def __init__(
        self,
        *,
        name: str,
        legislation_ids: List[str],
        default_threshold_percentage: Optional[float] = None,
        ignore_exemptions: bool = False,
    ) -> None:
        super().__init__(name, legislation_ids, default_threshold_percentage)
        self._ignore_exemptions: bool = ignore_exemptions
        self._indicator_type: str = "Rohs"
        self._flag: Optional[RoHSFlag] = None

    @property
    def _definition(self) -> models.CommonIndicatorDefinition:
        """Generate the low-level API indicator object."""
        kwargs: Dict[str, Any] = {
            "name": self.name,
            "legislation_ids": self.legislation_ids,
            "type": self._indicator_type,
        }
        if self.default_threshold_percentage is not None:
            kwargs["default_threshold_percentage"] = self.default_threshold_percentage
        if self._ignore_exemptions is not None:
            kwargs["ignore_exemptions"] = self._ignore_exemptions
        return models.CommonIndicatorDefinition(**kwargs)


class WatchListIndicator(_Indicator):
    """Provides the indicator object that represents watch list-type compliance of a BoM object against one or more
    legislations.

    Other ``WatchListIndicator`` objects with results can be compared, with 'less compliant' indicator flags being
    greater than 'more compliant' indicator flags.

    Parameters
    ----------
    name : str
        Name of the indicator that is used to identify the indicator in the query result.
    legislation_ids : list[str]
        Legislations against which compliance will be determined. Legislations are identified based
        on their ``Legislation ID`` attribute value.

        .. versionadded:: 2.0

        .. important::
           This argument replaces ``legislation_names``, which has been removed in version **2.0**.

           When updating scripts from version **1.x**, replace the ``legislation_names`` argument with the
           ``legislation_ids`` argument and ensure the value provided is a list of ``Legislation ID`` attribute values.
    default_threshold_percentage : float, optional
        Percentage of substance concentration that is to be determined to be non-compliant. The default is ``None``.
        This parameter is only used if the legislation doesn't define a specific threshold for the substance.
    ignore_process_chemicals : bool, optional
        Whether to ignore substances flagged as process chemicals when determining compliance against this indicator.
        The default is ``False``.

    Attributes
    ----------
    available_flags : Type[:class:`~ansys.grantami.bomanalytics.indicators.WatchListFlag`]
        Possible states of this indicator.

    Raises
    ------
    TypeError
        Error to raise if two indicators of different types are compared.
    ValueError
        Error to raise if two indicators are compared and both don't have a result flag.

    Notes
    -----
    The watch list indicator is designed to be used with REACH legislations or internal watch lists. However,
    usage is not enforced. Substances marked as ``Process Chemicals`` [1]_ are usually included, but they can be
    ignored by specifying ``ignore_process_chemicals=True`` when creating the indicator. Exemptions are always
    ignored. The possible result flags for the indicator distinguish between an item being compliant, compliant
    but with substances below the threshold, or non-compliant.

    Examples
    --------
    >>> indicator = RoHSIndicator(name='Tracked substances',
    ...                           legislation_ids=["SINList"],
    ...                           default_threshold_percentage=0.1,
    ...                           ignore_process_chemicals=True)
    >>> indicator
    <WatchListIndicator, name: Tracked substances>

    >>> query = MaterialComplianceQuery.with_indicators([indicator])...
    >>> result: MaterialComplianceQueryResult  # Perform a compliance query
    >>> indicator_result = result.compliance_by_indicator['Tracked substances']
    >>> indicator_result
    <WatchListIndicator, name: Tracked substances,
    flag: WatchListFlag.WatchListHasSubstanceAboveThreshold>

    >>> indicator_result <= indicator.available_flags['WatchListAllSubstancesBelowThreshold']
    False  # The material is not compliant with the legislations in the indicator
    """

    available_flags = WatchListFlag

    def __init__(
        self,
        *,
        name: str,
        legislation_ids: List[str],
        default_threshold_percentage: Optional[float] = None,
        ignore_process_chemicals: bool = False,
    ) -> None:
        super().__init__(name, legislation_ids, default_threshold_percentage)
        self._ignore_process_chemicals: bool = ignore_process_chemicals
        self._indicator_type: str = "WatchList"
        self._flag: Optional[WatchListFlag] = None

    @property
    def _definition(self) -> models.CommonIndicatorDefinition:
        """Generate the low-level API indicator object."""
        kwargs: Dict[str, Any] = {
            "name": self.name,
            "legislation_ids": self.legislation_ids,
            "type": self._indicator_type,
        }
        if self.default_threshold_percentage is not None:
            kwargs["default_threshold_percentage"] = self.default_threshold_percentage
        if self._ignore_process_chemicals is not None:
            kwargs["ignore_process_chemicals"] = self._ignore_process_chemicals
        return models.CommonIndicatorDefinition(**kwargs)
