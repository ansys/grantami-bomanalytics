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

import pathlib

from .examples import examples_as_dicts, examples_as_strings

repository_root = pathlib.Path(__file__).parents[2]
inputs_dir = pathlib.Path(__file__).parent

_sample_bom_1711_path = inputs_dir / "bom.xml"
with open(_sample_bom_1711_path, "r", encoding="utf8") as f:
    sample_bom_1711 = f.read()

_sample_compliance_bom_1711_path = (
    repository_root / "examples" / "3_Advanced_Topics" / "supporting-files" / "bom-complex.xml"
)
with open(_sample_compliance_bom_1711_path, "r", encoding="utf8") as f:
    sample_compliance_bom_1711 = f.read()

sample_bom_custom_db = sample_compliance_bom_1711.replace(
    "MI_Restricted_Substances", "MI_Restricted_Substances_Custom_Tables"
)

sample_sustainability_bom_2301_path = (
    repository_root / "examples" / "4_Sustainability" / "supporting-files" / "bom-2301-assembly.xml"
)
with open(sample_sustainability_bom_2301_path, "r", encoding="utf8") as f:
    sample_sustainability_bom_2301 = f.read()

large_bom_2301_path = inputs_dir / "medium-test-bom.xml"
with open(large_bom_2301_path, "r", encoding="utf8") as f:
    large_bom_2301 = f.read()

bom_with_annotations_path = inputs_dir / "bom-with-annotations.xml"
with open(bom_with_annotations_path, "r", encoding="utf8") as f:
    bom_with_annotations = f.read()
