"""BoM Analytics runtime type checker.

Provides a decorator that performs runtime type checking of the arguments passed into a function / method.

Attributes
----------
T
    Generic type to ensure static type checking works as expected.
"""

# mypy: ignore-errors

from typing import TypeVar, Type, Any
import functools

T = TypeVar("T")


def allowed_types(*types):
    """Decorator function that validates the arguments to the main function against the type of the objects supplied to
     the decorator.

    Parameters
    ----------
    *types
        Tuple of objects who's type should match the corresponding function argument's type.

    Raises
    ------
    ValueError
        If the number of objects passed to the decorator does not match the number of arguments passed to the wrapped
        function.
    TypeError
        if the type of an object passed to the decorator does not match the type of the corresponding argument.

    Examples
    --------
    >>> @check_types([str], str):
    >>> def process_records(records, database_key):
    >>>    ...

    >>> process_records(['Record 1', 'Record 2'], 'MI_DB')  # No error raised

    >>> process_records(['Record 1', 'Record 2'], 12)  # TypeError (12 is not a str)

    >>> process_records('Record 1', 'MI_DB')  # TypeError ('Record 1' is not a list)

    >>> process_records(['Record 1', 2], 'MI_DB')  # TypeError (2 is not a str)
    """

    def decorator(method: Type[T]) -> T:
        @functools.wraps(method)
        def check_types(*args, **kwargs):
            values = list(args) + list(kwargs.values())

            if len(types) != len(values):
                raise ValueError(f"Number of types ({len(types)}) does not match number of arguments ({len(values)})")
            for value, allowed_type in zip(values, types):
                try:
                    _check_type(value, allowed_type)
                except AssertionError:
                    raise TypeError(f'Incorrect type for value "{value}". Expected "{allowed_type}"')
            return method(*args, **kwargs)

        return check_types

    return decorator


def _check_type(obj, allowed_type: Any):
    """Recursively checks the type of an object against an allowed type.

    Recursive checking is performed if `allowed_type` is a container; first the type of the container itself is checked,
    and then the contents of `obj` are checked against the contents of `allowed_type`.

    Parameters
    ----------
    obj
        The object to be checked
    allowed_type
        The object to be checked against

    Returns
    -------
    None
        This function never returns a value. It either returns `None` or raises an exception.

    Raises
    ------
    AssertionError
        If the type of `obj` does not match the type of `allowed_type`.

    Notes
    -----
    `typing.Any` is also allowed as a type. This effectively allows type checking to be skipped for a particular `obj`.
    """

    if isinstance(allowed_type, list):
        assert isinstance(obj, list)
        for value, item_type in zip(obj, allowed_type):
            _check_type(value, item_type)
    elif isinstance(allowed_type, tuple):
        assert isinstance(obj, tuple)
        for value, item_type in zip(obj, allowed_type):
            _check_type(value, item_type)
    elif isinstance(allowed_type, dict):
        assert isinstance(obj, dict)
        for key, key_type in zip(obj.keys(), allowed_type.keys()):
            _check_type(key, key_type)
        for value, value_type in zip(obj.values(), allowed_type.values()):
            _check_type(value, value_type)
    else:
        assert isinstance(obj, allowed_type)
