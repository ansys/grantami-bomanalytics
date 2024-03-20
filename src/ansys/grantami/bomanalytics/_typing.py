from typing import Any, TypeVar, Union

from ansys.openapi.common import Unset_Type

T = TypeVar("T", bound=Any)


def _cast_unset_union_to_any(value: Union[T, Unset_Type]) -> T:
    """Cast any object that may be a union type including Unset_Type to a type not including
    Unset_Type.

    Parameters
    ----------
    value
        The object to cast.

    Returns
    -------
    Any
        The input value with a type that does not include Unset_Type.

    Raises
    ------
    ValueError
        If the object is an instance of Unset_Type.
    """
    new_value = _convert_unset_to_none(value)
    if new_value is None:
        raise ValueError
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
