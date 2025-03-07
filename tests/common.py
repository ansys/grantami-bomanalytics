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
import os
from typing import cast

from defusedxml import ElementTree

from ansys.grantami.bomanalytics import Connection, indicators

sl_url = os.getenv("TEST_SL_URL", "http://localhost/mi_servicelayer")
read_username = os.getenv("TEST_USER")
read_password = os.getenv("TEST_PASS")

write_username = os.getenv("TEST_WRITE_USER")
write_password = os.getenv("TEST_WRITE_PASS")


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


def _get_connection(url, username, password):
    if username is not None:
        connection = Connection(api_url=url).with_credentials(username, password).connect()
    else:
        connection = Connection(api_url=url).with_autologon().connect()
    return connection


def get_mi_version():
    connection = _get_connection(sl_url, read_username, read_password)
    session = connection.rest_client
    response = session.get(connection._sl_url + "/SystemInfo/v4.svc/Versions/Mi")
    tree = ElementTree.fromstring(response.text)
    version = next(c.text for c in tree if c.tag.rpartition("}")[2] == "MajorMinorVersion")
    parsed_version = [int(v) for v in version.split(".")]
    assert len(parsed_version) == 2
    return cast(tuple[int, int], tuple(parsed_version))
