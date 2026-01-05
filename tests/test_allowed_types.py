# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from numbers import Number
from typing import Optional

import pytest

from ansys.grantami.bomanalytics._allowed_types import _check_type, validate_argument_type

valid_types = [
    (int,),
    (int, int),
    (int, str),
    ([int],),
    ([int, int],),
    ([int, str],),
    ((int,),),
    ((int, int),),
    ((int, str),),
    ({int: int},),
    ({int},),
]


class TestInitialization:
    @pytest.mark.parametrize("allowed_types", valid_types)
    def test_single_arg(self, allowed_types):
        @validate_argument_type("arg_1", *allowed_types)
        def func(arg_1):
            pass

    @pytest.mark.parametrize("allowed_types_arg_1", valid_types)
    @pytest.mark.parametrize("allowed_types_arg_2", valid_types)
    def test_two_args_both_checked(self, allowed_types_arg_1, allowed_types_arg_2):
        @validate_argument_type("arg_1", *allowed_types_arg_1)
        @validate_argument_type("arg_2", *allowed_types_arg_2)
        def func(arg_1, arg_2):
            pass

    @pytest.mark.parametrize("allowed_types", valid_types)
    def test_two_args_first_checked(self, allowed_types):
        @validate_argument_type("arg_1", *allowed_types)
        def func(arg_1, arg_2):
            pass

    @pytest.mark.parametrize("allowed_types", valid_types)
    def test_two_args_second_checked(self, allowed_types):
        @validate_argument_type("arg_2", *allowed_types)
        def func(arg_1, arg_2):
            pass

    def test_one_arg_invalid_arg_name_raises(self):
        with pytest.raises(ValueError, match="Argument 'invalid_arg' not found in signature for callable.+func"):

            @validate_argument_type("invalid_arg", int)
            def func(arg_1):
                pass

    def test_two_args_invalid_arg_name_raises(self):
        with pytest.raises(ValueError, match="Argument 'invalid_arg' not found in signature for callable.+func"):

            @validate_argument_type("invalid_arg", int)
            @validate_argument_type("arg_1", int)
            @validate_argument_type("arg_2", int)
            def func(arg_1, arg_2):
                pass

    @pytest.mark.parametrize(
        ["allowed_types", "msg"],
        [
            (({int, str},), r"<class 'set'> must contain exactly 1 item.+has length 2"),
            (({int: str, str: str},), r"<class 'dict'> must contain exactly 1 item.+has length 2"),
        ],
    )
    def test_invalid_types_raise(self, allowed_types, msg):
        with pytest.raises(ValueError, match=msg):

            @validate_argument_type("arg_1", *allowed_types)
            def func(arg_1):
                pass


class TestSingleArgSingleSimpleType:
    @staticmethod
    @validate_argument_type("arg_1", int)
    def func(arg_1: Optional[int] = 5):
        return arg_1

    def test_valid_value_positional(self):
        assert self.func(5) == 5

    def test_valid_value_keyword(self):
        assert self.func(arg_1=5) == 5

    def test_valid_value_not_provided(self):
        assert self.func() == 5

    def test_invalid_simple_type_positional(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value '5'. Expected '<class 'int'>'",
        ):
            self.func("5")

    def test_invalid_simple_type_keyword(self):
        with pytest.raises(
            TypeError,
            match="Incorrect type for argument 'arg_1' value '5'. Expected '<class 'int'>'",
        ):
            self.func(arg_1="5")

    def test_invalid_container_positional(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value \[5\]. Expected '<class 'int'>'",
        ):
            self.func([5])

    def test_invalid_container_keyword(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value \[5\]. Expected '<class 'int'>'",
        ):
            self.func(arg_1=[5])


class TestSingleArgMultipleSimpleType:
    @staticmethod
    @validate_argument_type("arg_1", int, str)
    def func(arg_1: Optional[int | str] = 5):
        return arg_1

    @pytest.mark.parametrize("value", [5, "five"])
    def test_valid_value_positional(self, value):
        assert self.func(value) == value

    @pytest.mark.parametrize("value", [5, "five"])
    def test_valid_value_keyword(self, value):
        assert self.func(arg_1=value) == value

    def test_valid_value_not_provided(self):
        assert self.func() == 5

    def test_invalid_simple_type_positional(self):
        with pytest.raises(
            TypeError,
            match=(
                r"Incorrect type for argument 'arg_1' value 28\.123. Expected one of '<class 'int'>', '<class 'str'>'"
            ),
        ):
            self.func(28.123)

    def test_invalid_simple_type_keyword(self):
        with pytest.raises(
            TypeError,
            match=(
                r"Incorrect type for argument 'arg_1' value 28\.123. Expected one of '<class 'int'>', '<class 'str'>'"
            ),
        ):
            self.func(arg_1=28.123)

    def test_invalid_container_positional(self):
        with pytest.raises(
            TypeError,
            match=(
                r"Incorrect type for argument 'arg_1' value \[5\]. Expected one of '<class 'int'>', '<class 'str'>'"
            ),
        ):
            self.func([5])

    def test_invalid_container_keyword(self):
        with pytest.raises(
            TypeError,
            match=(
                r"Incorrect type for argument 'arg_1' value \[5\]. Expected one of '<class 'int'>', '<class 'str'>'"
            ),
        ):
            self.func(arg_1=[5])


class TestSingleArgSingleContainerType:
    @staticmethod
    @validate_argument_type("arg_1", [str])
    def func(arg_1: Optional[list[str]] = None):
        if arg_1 is None:
            arg_1 = ["test"]
        return arg_1

    def test_valid_value_positional(self):
        assert self.func(["blue"]) == ["blue"]

    def test_valid_value_keyword(self):
        assert self.func(arg_1=["blue"]) == ["blue"]

    def test_valid_value_not_provided(self):
        assert self.func() == ["test"]

    def test_invalid_simple_type_positional(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value 'blue'. Expected '\[<class 'str'>\]'",
        ):
            self.func("blue")

    def test_invalid_simple_type_keyword(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value 'blue'. Expected '\[<class 'str'>\]'",
        ):
            self.func(arg_1="blue")

    def test_invalid_container_positional(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value \{'blue'\}. Expected '\[<class 'str'>\]'",
        ):
            self.func({"blue"})

    def test_invalid_container_keyword(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value \{'blue'\}. Expected '\[<class 'str'>\]'",
        ):
            self.func(arg_1={"blue"})


class TestTwoArgsSingleSimpleTypes:
    @staticmethod
    @validate_argument_type("arg_1", int)
    @validate_argument_type("arg_2", str)
    def func(arg_1, arg_2: Optional[str] = "test"):
        return arg_1, arg_2

    def test_valid_value_positional(self):
        assert self.func(5, "red") == (5, "red")

    def test_valid_value_keyword(self):
        assert self.func(arg_1=5, arg_2="red") == (5, "red")

    def test_valid_value_mixed_args(self):
        assert self.func(5, arg_2="red") == (5, "red")

    def test_valid_value_not_provided(self):
        assert self.func(5) == (5, "test")

    def test_invalid_simple_type_first_arg(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value '5'. Expected '<class 'int'>'",
        ):
            self.func(arg_1="5", arg_2="red")

    def test_invalid_simple_type_second_arg(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_2' value 25.1. Expected '<class 'str'>'",
        ):
            self.func(arg_1=5, arg_2=25.1)

    def test_invalid_container_first_arg(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value \[5\]. Expected '<class 'int'>'",
        ):
            self.func(arg_1=[5], arg_2="red")

    def test_invalid_container_second_arg(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_2' value \['red'\]. Expected '<class 'str'>'",
        ):
            self.func(arg_1=5, arg_2=["red"])


class TestTwoArgsSingleSimpleAndContainerTypes:
    @staticmethod
    @validate_argument_type("arg_1", (int,))
    @validate_argument_type("arg_2", str)
    def func(arg_1, arg_2):
        return arg_1, arg_2

    def test_valid_value_positional(self):
        assert self.func((5, 7), "red") == ((5, 7), "red")

    def test_valid_value_keyword(self):
        assert self.func(arg_1=(5, 7), arg_2="red") == ((5, 7), "red")

    def test_valid_value_mixed_args(self):
        assert self.func((5, 7), arg_2="red") == ((5, 7), "red")

    def test_invalid_container_type_first_arg(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value '5'. Expected '\(<class 'int'>,\)'",
        ):
            self.func(arg_1="5", arg_2="red")

    def test_invalid_simple_type_second_arg(self):
        with pytest.raises(
            TypeError,
            match="Incorrect type for argument 'arg_2' value 25.1. Expected '<class 'str'>'",
        ):
            self.func(arg_1=(5,), arg_2=25.1)

    def test_invalid_container_first_arg(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_1' value \[5\]. Expected '\(<class 'int'>,\)'",
        ):
            self.func(arg_1=[5], arg_2="red")

    def test_invalid_container_second_arg(self):
        with pytest.raises(
            TypeError,
            match=r"Incorrect type for argument 'arg_2' value \['red'\]. Expected '<class 'str'>'",
        ):
            self.func(arg_1=(5,), arg_2=["red"])


class TestCheckType:
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
    def test_check_type_success(self, obj, allowed_type):
        _check_type(obj, allowed_type)

    @pytest.mark.parametrize(
        "obj, allowed_type",
        [
            ("test", int),
            (123, str),
            ([1, 2], [float]),
            ([1, 2], [int, str]),
            ([1, 2], {str: int}),
            (["1", 2], [int, str]),
            ((5, 10), (str,)),
            ({1, 2}, {str}),
            ({"a": 5.5, "b": 10.0}, []),
            ({"a": 5.5, "b": 10.0}, {float}),
            ({"a": 5.5, "b": 10.0}, {str: int}),
            ({"a": [1, 2], "b": [3, 4]}, {str: [str]}),
        ],
    )
    def test_check_type_wrong_type(self, obj, allowed_type):
        with pytest.raises(AssertionError):
            _check_type(obj, allowed_type)

    @pytest.mark.parametrize(
        "obj, allowed_type",
        [
            (("test",), (str, str)),
            (("test", "test2"), (str, str, str)),
            (("test", "test2", "test3"), (str, str)),
        ],
    )
    def test_check_type_wrong_container_length(self, obj, allowed_type):
        with pytest.raises(ValueError):
            _check_type(obj, allowed_type)
