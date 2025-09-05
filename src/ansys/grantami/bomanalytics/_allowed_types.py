# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""BoM Analytics runtime type checker.

Provides a decorator that performs runtime type checking of the arguments passed into a function or method.

Attributes
----------
T
    Generic type to ensure static-type checking works as expected.
"""

import functools
import inspect
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def validate_argument_type(argument_name: str, *allowed_types: Any) -> Callable:
    """
    Validates the types of values passed into a callable.

    This decorator function accepts an argument name and one or more objects against which types are checked.

    * If one object is provided, the value must be of that object's type.
    * If multiple objects are provided, the value must be of at least one object's types.
    * If a container of objects is provided, the types are validated recursively.

      - To define a homogeneous tuple or list, provide a tuple or list with a single element.
      - To define a heterogeneous tuple or list, provide a tuple or list with the expected elements in the expected
        positions.
      - To define a homogeneous dictionary or set, provide a dictionary or set with a single element.
      - Heterogeneous dictionaries or sets are not supported.

    Parameters
    ----------
    argument_name : str
        The name of the argument to be validated.
    *allowed_types
        Objects whose type should match the corresponding function argument's type.

    Raises
    ------
    TypeError
        On validation, if the type of an object passed to the decorator does not match the type of the corresponding
        argument.
        On validation, if the number of objects passed to the decorator does not match the number of arguments passed to
        the wrapped function.
    ValueError
        On initialization, if ``argument_name`` doesn't match an argument name in the wrapped callable.
        On initialization, if a dictionary or set does not contain exactly one item.
        On validation, if a list or tuple does not contain either one item or a number of items equal to the container
        being checked.

    Examples
    --------
    >>> @validate_argument_type("records", [str]):
    >>> def process_records(self, records):
    >>>    ...

    >>> self.process_records(['Record 1', 'Record 2'])  # No error raised

    >>> self.process_records('Record 1')  # TypeError ('Record 1' is not a list)

    >>> self.process_records(['Record 1', 2])  # TypeError (2 is not a str)
    """

    for allowed_type in allowed_types:
        if isinstance(allowed_type, (dict, set)):
            if len(allowed_type) != 1:
                raise ValueError(
                    f"{type(allowed_type)} must contain exactly 1 item. '{allowed_type}' has length {len(allowed_type)}"
                )

    def decorator(callable_: Callable[..., T]) -> Callable[..., T]:
        callable_params = inspect.signature(callable_).parameters

        if argument_name not in callable_params:
            raise ValueError(f"Argument '{argument_name}' not found in signature for callable {repr(callable_)}")

        @functools.wraps(callable_)
        def check_types(*args: Any, **kwargs: Any) -> T:
            # First check if the argument was provided as a kwarg
            try:
                value = kwargs[argument_name]
            except KeyError:
                # If not, try to extract from the tuple of positional args
                for idx, param in enumerate(callable_params.keys()):
                    if param == argument_name:
                        break
                try:
                    value = args[idx]
                except IndexError:
                    # If there are not enough positional parameters, then this argument wasn't provided.
                    return callable_(*args, **kwargs)

            result = any([_check_type_wrapper(value, t) for t in allowed_types])
            if not result:
                allowed_types_str = ", ".join(f"'{repr(t)}'" for t in allowed_types)
                if len(allowed_types) != 1:
                    allowed_types_str = f"one of {allowed_types_str}"
                raise TypeError(
                    f"Incorrect type for argument '{argument_name}' value {repr(value)}. Expected {allowed_types_str}"
                )
            return callable_(*args, **kwargs)

        return check_types

    return decorator


def _check_type_wrapper(value_obj: Any, type_obj: Any) -> bool:
    try:
        _check_type(value_obj, type_obj)
        return True
    except AssertionError:
        return False


def _check_type(value_obj: Any, type_obj: Any) -> None:
    """Recursively checks the type of an object against an allowed type.

    Recursive checking is performed if the ``allowed_type`` parameter is a container. First the type of the
    container itself is checked. The contents of object are then checked against the contents of the
    ``allowed_type`` parameter.

    Parameters
    ----------
    value_obj
        Object to check.
    type_obj
        Object to checked against.

    Returns
    -------
    None
        This function never returns a value. It either returns ``None`` or raises an exception.

    Raises
    ------
    AssertionError
        If the type of ``obj`` does not match the type of ``allowed_type``.
    ValueError
        If a container's length is mismatched against the object being checked.
    """

    if isinstance(type_obj, (list, tuple)):
        if not isinstance(value_obj, type(type_obj)):
            raise AssertionError
        if len(type_obj) == 1:
            contained_type = type_obj[0]
            for value in value_obj:
                _check_type(value, contained_type)
        elif len(type_obj) == len(value_obj):
            for value, contained_type in zip(value_obj, type_obj):
                _check_type(value, contained_type)
        else:
            raise ValueError(
                "List or tuple containers must be either of length one or the same length as the "
                "object being checked."
                f"Container length: {len(type_obj)}, object length: {len(value_obj)}"
            )

    elif isinstance(type_obj, set):
        if not isinstance(value_obj, set):
            raise AssertionError
        contained_type = next(iter(type_obj))
        for value in value_obj:
            _check_type(value, contained_type)

    elif isinstance(type_obj, dict):
        if not isinstance(value_obj, dict):
            raise AssertionError
        contained_key_type = next(iter(type_obj.keys()))
        for key in value_obj.keys():
            _check_type(key, contained_key_type)
        contained_value_type = next(iter(type_obj.values()))
        for value in value_obj.values():
            _check_type(value, contained_value_type)

    else:
        if not isinstance(value_obj, type_obj):
            raise AssertionError
