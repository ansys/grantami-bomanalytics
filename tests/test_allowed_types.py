import pytest
from numbers import Number
from typing import Any
from ansys.granta.bom_analytics.allowed_types import allowed_types, check_type


def test_allowed_types_args():
    @allowed_types(int, int, int)
    def test_function(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    result = test_function(12, 23, 34)["args"]
    assert result == (12, 23, 34)


def test_allowed_types_kwargs():
    @allowed_types(int, int, int)
    def test_function(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    result = test_function(a=12, b=23, c=34)["kwargs"]
    assert result == {"a": 12, "b": 23, "c": 34}


def test_allowed_types_args_kwargs():
    @allowed_types(int, int, int, int, int)
    def test_function(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    result = test_function(12, 23, a=34, b=45, c=56)
    assert result["args"] == (12, 23)
    assert result["kwargs"] == {"a": 34, "b": 45, "c": 56}


def test_different_lengths_value_error():
    @allowed_types(int)
    def test_function(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    with pytest.raises(ValueError) as e:
        test_function(12, 23)
    assert f"Number of types (1) does not match number of arguments (2)" == str(e.value)


def test_different_types_type_error():
    @allowed_types(int)
    def test_function(*args, **kwargs):
        return {"args": args, "kwargs": kwargs}

    with pytest.raises(TypeError) as e:
        test_function("test")
    assert f'Incorrect type for value "test". Expected "<class \'int\'>"' == str(e.value)


@pytest.mark.parametrize(
    "obj, allowed_type",
    [
        ("test", str),
        (123, int),
        (123, Number),
        ([1, 2], [int]),
        ((1, 2), (int,)),
        ((1, 2), (int, int)),
        ({"a": 5.5, "b": 10.0}, {}),
        ({"a": 5.5, "b": 10.0}, {str: float}),
        ({"a": [1, 2], "b": [3, 4]}, {str: [int]}),
        ({"a": [1, 2], "b": [3, 4]}, Any),
        ({"a": [1, 2], "b": [3, 4]}, {str: [Any]}),
    ],
)
def test_check_type_success(obj, allowed_type):
    check_type(obj, allowed_type)


@pytest.mark.parametrize(
    "obj, allowed_type",
    [
        ("test", int),
        (123, str),
        ([1, 2], [float]),
        ([1, 2], [int, str]),
        ((5, 10), (str,)),
        ({"a": 5.5, "b": 10.0}, []),
        ({"a": 5.5, "b": 10.0}, {str: int}),
        ({"a": [1, 2], "b": [3, 4]}, {str: [str]}),
    ],
)
def test_check_type_failure(obj, allowed_type):
    with pytest.raises(AssertionError):
        check_type(obj, allowed_type)
