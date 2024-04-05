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

from typing import Any, TypeVar, Union

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
