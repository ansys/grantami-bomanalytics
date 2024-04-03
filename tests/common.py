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

from ansys.grantami.bomanalytics import indicators

LICENSE_RESPONSE = {"LogMessages": [], "RestrictedSubstances": True, "Sustainability": True}
LEGISLATIONS = ["SINList", "CCC"]


two_legislation_indicator = indicators.WatchListIndicator(
    name="Two legislations",
    legislation_ids=["GADSL", "Prop65"],
    default_threshold_percentage=2,
)
one_legislation_indicator = indicators.RoHSIndicator(
    name="One legislation",
    legislation_ids=["RoHS"],
    default_threshold_percentage=0.01,
)

INDICATORS = {"Two legislations": two_legislation_indicator, "One legislation": one_legislation_indicator}

CUSTOM_TABLES = [
    ("material_universe_table_name", "My Material Universe"),
    ("in_house_materials_table_name", "My Materials"),
    ("specifications_table_name", "specs"),
    ("products_and_parts_table_name", "Parts 'n' Products"),
    ("substances_table_name", "Chemicals"),
    ("coatings_table_name", "Coverings"),
    ("process_universe_table_name", "Methods"),
    ("location_table_name", "Places"),
    ("transport_table_name", "Locomotion"),
]
