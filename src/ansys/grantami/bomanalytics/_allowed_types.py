"""BoM Analytics runtime type checker.

Provides a decorator that performs runtime type checking of the arguments passed into a function or method.

Attributes
----------
T
    Generic type to ensure static-type checking works as expected.
"""

from typing import TypeVar, Type, Any, Callable
import functools

T = TypeVar("T")


def validate_argument_type(*allowed_types: Any) -> Callable:
    """Validates the types of values passed into a method. This decorator function accepts one or more
    objects against which types are checked.

     - If one object is provided, the value must be of that object's type.
     - If multiple objects are provided, the value must be of at least one object's types.
     - If a container of objects are provided, the types are validated recursively.

     Tuples and lists can be heterogeneous, where the ordering of the items in the containers is taken into account.
     Dictionaries and sets must be homogeneous. If they are not exactly one item in length, a ``ValueError`` is raised.

    Parameters
    ----------
    *allowed_types
        Tuple of objects whose type should match the corresponding function argument's type.

    Raises
    ------
    TypeError
        If the type of an object passed to the decorator does not match the type of the corresponding argument.
        If the number of objects passed to the decorator does not match the number of arguments passed to the wrapped
        function.
    ValueError
        If a list or tuple does not contain either one item or a number of items equal to the container being checked.
        If a dictionary or set does not contain exactly one item.

    Examples
    --------
    >>> @validate_argument_type([str]):
    >>> def process_records(self, records):
    >>>    ...

    >>> self.process_records(['Record 1', 'Record 2'])  # No error raised

    >>> self.process_records('Record 1')  # TypeError ('Record 1' is not a list)

    >>> self.process_records(['Record 1', 2])  # TypeError (2 is not a str)
    """

    def decorator(method: Type[T]) -> Callable[[Any, Any], T]:
        @functools.wraps(method)
        def check_types(*args: Any, **kwargs: Any) -> T:
            values = list(args)[1:] + list(kwargs.values())
            if len(values) != 1:
                raise TypeError(
                    f"The allowed_types decorator can only be used on a method called with "
                    f'exactly one argument. The method "{method.__name__}" was called with {len(values)} '
                    f"arguments."
                )
            value = values[0]
            result = any([_check_type_wrapper(value, allowed_type) for allowed_type in allowed_types])
            if not result:
                raise TypeError(f'Incorrect type for value "{value}". Expected "{allowed_types}"')
            return method(*args, **kwargs)  # type: ignore[call-arg]

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

    Recursive checking is performed if ``allowed_type`` is a container. First the type of the container itself
    is checked. The contents of ``obj`` are then checked against the contents of ``allowed_type``.

    Parameters
    ----------
    value_obj
        Object to be checked.
    type_obj
        Object to be checked against.

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
        assert isinstance(value_obj, (list, tuple))
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
        assert isinstance(value_obj, set)
        if len(type_obj) != 1:
            raise ValueError(
                "Sets must be homogeneous: they can only contain a single object against "
                "which the type should be checked."
            )
        contained_type = next(iter(type_obj))
        for value in value_obj:
            _check_type(value, contained_type)
    elif isinstance(type_obj, dict):
        assert isinstance(value_obj, dict)
        if len(type_obj) != 1:
            raise ValueError(
                "Dictionaries must be homogeneous: they can only contain a single object "
                "against which the type should be checked."
            )
        contained_key_type = next(iter(type_obj.keys()))
        for key in value_obj.keys():
            _check_type(key, contained_key_type)
        contained_value_type = next(iter(type_obj.values()))
        for value in value_obj.values():
            _check_type(value, contained_value_type)
    else:
        assert isinstance(value_obj, type_obj)
