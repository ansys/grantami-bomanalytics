from numbers import Number

import pytest

from ansys.grantami.bomanalytics._allowed_types import _check_type, validate_argument_type


def test_allowed_types_args():
    @validate_argument_type(int)
    def test_function(*args):
        return args

    # The function is expected to be a method, so "self" fills the expected role of self as the first positional arg
    result = test_function("self", 23)
    assert result == ("self", 23)


def test_allowed_types_kwargs():
    @validate_argument_type(int)
    def test_function(*args, **kwargs):
        return kwargs

    result = test_function("self", value=23)
    assert result == {"value": 23}


def test_different_lengths_type_error():
    @validate_argument_type(int)
    def test_function(*args):
        return args

    with pytest.raises(TypeError) as e:
        test_function("self", 23, 34)
    assert 'The method "test_function" was called with 2 arguments.' in str(e.value)


def test_different_types_type_error():
    @validate_argument_type(int)
    def test_function(*args):
        return args

    with pytest.raises(TypeError) as e:
        test_function("self", "test")
    assert f'Incorrect type for value "test". Expected "(<class \'int\'>,)"' in str(e.value)


@pytest.mark.parametrize(
    "obj, allowed_type",
    [
        ("test", str),
        (123, int),
        (123, Number),
        ([1, 2], [int]),
        ([1, "2"], [int, str]),
        ((1, 2), (int,)),
        ((1, 2), (int, int)),
        ({1, 2}, {int}),
        ({1, 2}, {int, int}),
        ({"a": 5.5, "b": 10.0}, {str: float}),
        ({"a": [1, 2], "b": [3, 4]}, {str: [int]}),
        ({"a": [1, 2], "b": [3, 4]}, object),
        ({"a": [1, 2], "b": [3, 4]}, {str: [object]}),
    ],
)
def test_check_type_success(obj, allowed_type):
    _check_type(obj, allowed_type)


@pytest.mark.parametrize(
    "obj, allowed_type",
    [
        ("test", int),
        (123, str),
        ([1, 2], [float]),
        ([1, 2], [int, str]),
        (["1", 2], [int, str]),
        ((5, 10), (str,)),
        ({1, 2}, {str}),
        ({"a": 5.5, "b": 10.0}, []),
        ({"a": 5.5, "b": 10.0}, {str: int}),
        ({"a": [1, 2], "b": [3, 4]}, {str: [str]}),
    ],
)
def test_check_type_wrong_type(obj, allowed_type):
    with pytest.raises(AssertionError):
        _check_type(obj, allowed_type)


@pytest.mark.parametrize(
    "obj, allowed_type",
    [
        (("test",), (str, str)),
        (("test", "test2"), (str, str, str)),
        (("test", "test2", "test3"), (str, str)),
        ({"a": 5.5, "b": 10.0}, {}),
        ({1, 2.5}, {int, float}),
    ],
)
def test_check_type_wrong_container_length(obj, allowed_type):
    with pytest.raises(ValueError):
        _check_type(obj, allowed_type)
