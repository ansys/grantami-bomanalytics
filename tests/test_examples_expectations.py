# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from . import examples_expectations as ee


class _Column(list):
    def to_list(self):
        return list(self)


class _Frame(dict):
    def __getitem__(self, item):
        return _Column(super().__getitem__(item))


def test_example_5_4_processes_allows_row_reordering():
    ee.primary_process_df = _Frame(
        {
            "Name": [
                "Other - None",
                "Primary processing, Metal extrusion, hot - steel-1010-annealed",
                "Primary processing, Casting - steel-1010-annealed",
                "Primary processing, Casting - stainless-astm-cn-7ms-cast",
            ],
            "EE%": [0.1, 16.6, 33.8, 49.4],
        }
    )
    ee.secondary_process_df = _Frame(
        {
            "Name": [
                "Other - None",
                "Secondary processing, Machining, fine - stainless-astm-cn-7ms-cast",
                "Machining, fine - steel-1010-annealed",
                "Secondary processing, Machining, coarse - stainless-astm-cn-7ms-cast",
                "Secondary processing, Grinding - steel-1010-annealed",
            ],
            "EE%": [2.4, 8.4, 14.6, 30.7, 44.7],
        }
    )
    ee.joining_and_finishing_processes_df = _Frame(
        {"Name": ["Joining and finishing, Welding, electric"], "EE%": [100.0]}
    )
    ee.Out = {2: "", 3: "", 4: "", 7: "", 8: "", 10: "", 11: ""}

    ee.example_5_4_processes()
