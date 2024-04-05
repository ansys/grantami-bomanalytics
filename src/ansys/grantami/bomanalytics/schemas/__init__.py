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

"""
Sub-package providing XML Schema Definition (XSD) files for Ansys Granta BoM formats.

XSD files can be used for validating XML files.
"""

from pathlib import Path

_schemas_dir = Path(__file__).parent

bom_schema_1711: Path = _schemas_dir / "BillOfMaterialsEco1711.xsd"
"""Path to the Ansys Granta 17/11 BoM XML Schema definition.

.. versionadded:: 2.0
"""

bom_schema_2301: Path = _schemas_dir / "BillOfMaterialsEco2301.xsd"
"""Path to the Ansys Granta 23/01 BoM XML Schema definition.

.. versionadded:: 2.0
"""
