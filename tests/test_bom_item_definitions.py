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

from ansys.grantami.bomanalytics_openapi import (
    GetComplianceForSubstancesSubstanceWithAmount as SubsRef,
)
from ansys.grantami.bomanalytics_openapi import CommonMaterialReference as MatRef
from ansys.grantami.bomanalytics_openapi import CommonPartReference as PartRef
from ansys.grantami.bomanalytics_openapi import CommonSpecificationReference as SpecRef
import pytest

from ansys.grantami.bomanalytics._item_definitions import (
    CoatingReference,
    MaterialDefinition,
    PartDefinition,
    ProcessReference,
    RecordReference,
    ReferenceType,
    SpecificationDefinition,
    SubstanceDefinition,
    TransportReference,
)

common_test_cases = [
    ({"reference_type": ReferenceType.MiRecordGuid, "reference_value": "TEST_GUID"}, "record_guid"),
    (
        {"reference_type": ReferenceType.MiRecordHistoryIdentity, "reference_value": "TEST_RH_ID"},
        "record_history_identity",
    ),
    ({"reference_type": ReferenceType.MiRecordHistoryGuid, "reference_value": "TEST_RH_GUID"}, "record_history_guid"),
]


@pytest.mark.parametrize(
    "kwargs, variable_name",
    common_test_cases,
)
@pytest.mark.parametrize("item_type", [RecordReference, ProcessReference, CoatingReference, TransportReference])
def test_base_record_references(kwargs, variable_name, item_type):
    item = item_type(**kwargs)
    assert getattr(item, variable_name) == kwargs["reference_value"]


@pytest.mark.parametrize(
    "kwargs, variable_name",
    [({"reference_type": ReferenceType.MaterialId, "reference_value": "TEST_MATERIAL_ID"}, "material_id")]
    + common_test_cases,
)
def test_material_definition(kwargs, variable_name):
    material_definition = MaterialDefinition(**kwargs)
    assert material_definition.__getattribute__(variable_name) == kwargs["reference_value"]

    mat_ref = MatRef(reference_type=kwargs["reference_type"].name, reference_value=kwargs["reference_value"])
    assert material_definition._definition == mat_ref


@pytest.mark.parametrize(
    "kwargs, variable_name",
    [({"reference_type": ReferenceType.PartNumber, "reference_value": "TEST_PART_NUMBER"}, "part_number")]
    + common_test_cases,
)
def test_part_definition(kwargs, variable_name):
    part_definition = PartDefinition(**kwargs)
    assert part_definition.__getattribute__(variable_name) == kwargs["reference_value"]

    part_ref = PartRef(reference_type=kwargs["reference_type"].name, reference_value=kwargs["reference_value"])
    assert part_definition._definition == part_ref


@pytest.mark.parametrize(
    "kwargs, variable_name",
    [({"reference_type": ReferenceType.SpecificationId, "reference_value": "TEST_SPEC_ID"}, "specification_id")]
    + common_test_cases,
)
def test_specification_definition(kwargs, variable_name):
    spec_definition = SpecificationDefinition(**kwargs)
    assert spec_definition.__getattribute__(variable_name) == kwargs["reference_value"]

    spec_ref = SpecRef(reference_type=kwargs["reference_type"].name, reference_value=kwargs["reference_value"])
    assert spec_definition._definition == spec_ref


@pytest.mark.parametrize(
    "kwargs, variable_name",
    [
        (
            {"reference_type": ReferenceType.MiRecordGuid, "reference_value": "TEST_GUID", "percentage_amount": 5},
            "record_guid",
        ),
        (
            {
                "reference_type": ReferenceType.MiRecordHistoryIdentity,
                "reference_value": "TEST_RH_ID",
                "percentage_amount": 20,
            },
            "record_history_identity",
        ),
        (
            {
                "reference_type": ReferenceType.MiRecordHistoryGuid,
                "reference_value": "TEST_RH_GUID",
                "percentage_amount": 100,
            },
            "record_history_guid",
        ),
        (
            {"reference_type": ReferenceType.CasNumber, "reference_value": "50-00-0", "percentage_amount": 5},
            "cas_number",
        ),
        ({"reference_type": ReferenceType.EcNumber, "reference_value": "12-34-5"}, "ec_number"),
        (
            {
                "reference_type": ReferenceType.ChemicalName,
                "reference_value": "TEST_Chemical_Name",
                "percentage_amount": 15,
            },
            "chemical_name",
        ),
    ],
)
def test_substance_definition(kwargs, variable_name):
    substance_definition = SubstanceDefinition(**kwargs)
    assert substance_definition.__getattribute__(variable_name) == kwargs["reference_value"]

    if "percentage_amount" not in kwargs:
        subs_ref = SubsRef(
            reference_type=kwargs["reference_type"].name,
            reference_value=kwargs["reference_value"],
            percentage_amount=100,
        )
    else:
        subs_ref = SubsRef(
            reference_type=kwargs["reference_type"].name,
            reference_value=kwargs["reference_value"],
            percentage_amount=kwargs["percentage_amount"],
        )
    assert substance_definition._definition == subs_ref


@pytest.mark.parametrize("percentage_amount", [-5, 150])
def test_substance_definition_out_of_range_value_error(percentage_amount):
    substance_definition = SubstanceDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value="12345")
    with pytest.raises(ValueError) as e:
        substance_definition.percentage_amount = percentage_amount
    assert f'percentage_amount must be between 0 and 100. Specified value was "{float(percentage_amount)}"' in str(
        e.value
    )


@pytest.mark.parametrize("percentage_amount", ["test", [50]])
def test_substance_definition_wrong_type_type_error(percentage_amount):
    substance_definition = SubstanceDefinition(reference_type=ReferenceType.MiRecordGuid, reference_value="12345")
    with pytest.raises(TypeError) as e:
        substance_definition.percentage_amount = percentage_amount
    assert f'percentage_amount must be a number. Specified type was "{type(percentage_amount)}"' in str(e.value)
