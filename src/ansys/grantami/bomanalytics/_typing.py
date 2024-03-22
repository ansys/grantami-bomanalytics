from typing import Any, Optional, TypeVar, Union

from ansys.openapi.common import Unset_Type

T = TypeVar("T", bound=Any)


def _raise_if_unset(value: Union[T, Unset_Type]) -> T:
    """Raise if the value is Unset.

    Parameters
    ----------
    value
        The value to check.

    Returns
    -------
    Any
        The input value if it is not Unset.

    Raises
    ------
    ValueError
        If the object is an instance of Unset_Type.
    """
    new_value = _convert_unset_to_none(value)
    if new_value is None:
        raise ValueError("Provided value cannot be 'Unset'")
    return new_value


def _convert_unset_to_none(value: Union[T, Unset_Type]) -> Union[T, None]:
    """Convert any object that may be a union type including Unset_Type to a union type including
    None.

    Parameters
    ----------
    value
        The object to cast.

    Returns
    -------
    Any, optional
        The input value with the Unset_Type substituted for None.
    """
    if isinstance(value, Unset_Type):
        return None
    else:
        return value
