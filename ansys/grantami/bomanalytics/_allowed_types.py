"""BoM Analytics runtime type checker.

Provides a decorator that performs runtime type checking of the arguments passed into a function / method.

Attributes
----------
T
    Generic type to ensure static type checking works as expected.
"""

from typing import TypeVar, Type, Any, Callable
import functools

T = TypeVar("T")


def allowed_types(*types: Any) -> Callable:
    """Decorator function that validates the types of values passed into a method. The decorator accepts one or more
    objects against which the types are checked.

     - If one object is provided, then the value must be of that object's type.
     - If multiple objects are provided, then the value must be of at least one object's types.
     - If a container of objects are provided, then the types are validated recursively.

     Tuples and lists can be heterogeneous, where the ordering of the items in the containers is taken into account.
     Dicts and sets must be homogeneous, if they are not exactly 1 item in length then a ValueError is raised.

    Parameters
    ----------
    *types
        Tuple of objects who's type should match the corresponding function argument's type.

    Raises
    ------
    TypeError
        If the type of an object passed to the decorator does not match the type of the corresponding argument.
        If the number of objects passed to the decorator does not match the number of arguments passed to the wrapped
        function.
    ValueError
        If a list or tuple does not contain either 1 item or a number of items equal to the container being checked.
        If a dict or set does not contain exactly 1 item.

    Examples
    --------
    >>> @check_types([str]):
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
                raise TypeError(f"The allowed_types decorator can only be used on a method called with exactly one "
                                f'argument. The method "{method.__name__}" was called with {len(values)} arguments.')
            value = values[0]
            result = any([_check_type_wrapper(value, allowed_type) for allowed_type in types])
            if not result:
                raise TypeError(f'Incorrect type for value "{value}". Expected "{types}"')
            return method(*args, **kwargs)  # type: ignore[call-arg]
        return check_types
    return decorator


def _check_type_wrapper(obj: Any, allowed_type: Any) -> bool:
    try:
        _check_type(obj, allowed_type)
        return True
    except AssertionError:
        return False


def _check_type(obj: Any, allowed_type: Any) -> None:
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
    ValueError
        If a container's length is mismatched against the object being checked.
    """

    if isinstance(allowed_type, (list, tuple)):
        assert isinstance(obj, (list, tuple))
        if len(allowed_type) == 1:
            contained_type = allowed_type[0]
            for value in obj:
                _check_type(value, contained_type)
        elif len(allowed_type) == len(obj):
            for value, contained_type in zip(obj, allowed_type):
                _check_type(value, contained_type)
        else:
            raise ValueError("List or tuple containers must be either of length 1 or the same length as the object"
                             "being checked."
                             f"Container length: {len(allowed_type)}, object length: {len(obj)}")
    elif isinstance(allowed_type, set):
        assert isinstance(obj, set)
        if len(allowed_type) != 1:
            raise ValueError("Sets must be homogeneous, i.e. they can only contain a single object against which the"
                             " type should be checked.")
        contained_type = next(iter(allowed_type))
        for value in obj:
            _check_type(value, contained_type)
    elif isinstance(allowed_type, dict):
        assert isinstance(obj, dict)
        if len(allowed_type) != 1:
            raise ValueError("Dictionaries must be homogeneous, i.e. they can only contain a single object against"
                             " which the type should be checked.")
        contained_key_type = next(iter(allowed_type.keys()))
        for key in obj.keys():
            _check_type(key, contained_key_type)
        contained_value_type = next(iter(allowed_type.values()))
        for value in obj.values():
            _check_type(value, contained_value_type)
    else:
        assert isinstance(obj, allowed_type)
