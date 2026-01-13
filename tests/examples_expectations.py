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

def example_0_basic_usage():
    assert len(result.impacted_substances) == 8

    assert len(result.impacted_substances_by_material) == 1
    assert result.impacted_substances_by_material[0].material_id == "plastic-abs-high-impact"

    assert len(result.impacted_substances_by_legislation) == 1
    assert "Candidate_AnnexXV" in result.impacted_substances_by_legislation

    assert len(result.messages) == 0

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3, 4, 5, 6, 7, 8, 9, 10, 11}


def example_1_database_config():
    assert cxn._table_names["inhouse_materials_table_name"] == "ACME Materials"
    assert spec_query._data.batch_size == 5
    assert cxn.maximum_spec_link_depth == 2

    # Expected cells with outputs
    assert set(Out.keys()) == {1, 2, 3, 4, 5}


def example_2_1_materials_impacted_substances():
    assert len(results.impacted_substances_by_material) == 2
    assert len(results.impacted_substances_by_legislation) == 2
    assert len(substances_by_material[PC_ID]) == 16
    assert len(substances_by_material[PPS_ID]) == 11

    assert len(results.impacted_substances_by_legislation[SIN_LIST]) == 27
    assert len(results.impacted_substances_by_legislation[REACH]) == 21

    assert len(results.impacted_substances) == 48

    # Expected cells with outputs
    assert set(Out.keys()) == {4}, str(Out)


def example_2_2_parts_impacted_substances():
    assert len(substances_by_part[DRILL]) == 81, len(substances_by_part[DRILL])
    assert len(substances_by_part[WING]) == 1, len(substances_by_part[WING])

    assert len(part_result.impacted_substances_by_legislation[SIN_LIST]) == 82
    assert len(part_result.impacted_substances) == 132, len(part_result.impacted_substances)

    # Expected cells with outputs
    assert set(Out.keys()) == {4}, str(Out)


def example_2_3_bom_impacted_substances():
    assert Out[2] is True
    assert Out[3] is False

    assert len(impacted_substances_result.impacted_substances) == 44

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3, 6}, str(Out)


def example_2_4_external_database_materials():
    assert len(material_result.equivalent_references) == 1
    assert (
        material_result.name
        == "Epoxy (EP) matrix, glass fiber (S-glass) unidirectional tape prepreg, 0° unidirectional lamina (unidirectional tape prepreg, fiber Vf:0.47-0.55, autoclave cure at 125°C, 3.5 bar)"
    )
    assert material_result.equivalent_references[0].record_history_guid == EPOXY_GLASS_GUID
    assert material_result.equivalent_references[0].database_key == EXTERNAL_DB_KEY
    assert len(rows) == 14

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3}, str(Out)


def example_3_1_substance_compliance():
    assert len(sub_result.compliance_by_substance_and_indicator) == 4
    assert set(compliant_cas_numbers) == {"50-00-0", "302-17-0", "7440-23-5"}
    assert set(non_compliant_cas_numbers) == {"110-00-9"}

    # Expected cells with outputs
    assert set(Out.keys()) == {4}, str(Out)


def example_3_2_material_compliance():
    assert set(mat_result.compliance_by_indicator.keys()) == {"SVHC", "SIN"}
    assert len(mat_result.compliance_by_material_and_indicator) == 3

    assert pa_66.indicators["SVHC"].flag.name == "WatchListHasSubstanceAboveThreshold"
    assert len(pa_66_svhcs) == 16
    assert pa_66.indicators["SIN"].flag.name == "WatchListHasSubstanceAboveThreshold"

    assert zn_pb_cd.indicators["SVHC"].flag.name == "WatchListAllSubstancesBelowThreshold"
    assert zn_pb_cd.indicators["SIN"].flag.name == "WatchListHasSubstanceAboveThreshold"
    assert len(zn_svhcs_below_threshold) == 2

    assert ss_316h.indicators["SVHC"].flag.name == "WatchListCompliant"
    assert ss_316h.indicators["SIN"].flag.name == "WatchListHasSubstanceAboveThreshold"
    assert len(ss_not_impacted) == 10

    # Expected cells with outputs
    assert set(Out.keys()) == {4}, str(Out)


def example_3_3_part_compliance():
    assert set(part_result.compliance_by_indicator.keys()) == {"SVHC"}
    assert len(part_result.compliance_by_part_and_indicator) == 2

    assert wing.indicators["SVHC"].flag.name == "WatchListHasSubstanceAboveThreshold"
    assert len(parts_contain_svhcs) == 1

    # Expected cells with outputs
    assert set(Out.keys()) == {4}, str(Out)


def example_3_4_bom_compliance():
    assert Out[2] is True
    assert Out[3] is False

    assert len(compliance_result.compliance_by_part_and_indicator) == 1

    assert root_part.input_part_number == "Placeholder Root Part"
    assert root_part.indicators["SVHC"].flag.name == "WatchListHasSubstanceAboveThreshold"

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3, 6}, str(Out)


def example_3_5_compliance_for_external_data():
    assert material_ids == {
        "aluminum-6063-t6",
        "elastomer-pvc-shorea55",
        "glass-borosilicate-7050",
        "plastic-abs-pvc-flame",
        "plastic-pc-10glassfiber",
        "stainless-316-annealed",
    }
    assert component_results == {
        "FQC3RQKYE5": "WatchListHasSubstanceAboveThreshold",
        "3FF8CXIHWJ": "WatchListHasSubstanceAboveThreshold",
        "O676WZSGHA": "WatchListHasSubstanceAboveThreshold",
        "L8NTU4BZY2": "WatchListCompliant",
        "7N9EUBALU2": "WatchListCompliant",
        "U921IQSW6K": "WatchListCompliant",
        "TUSMQ1ZDFM": "WatchListHasSubstanceAboveThreshold",
    }
    assert results == {
        "FQC3RQKYE5": "Level 2 Approval Required",
        "3FF8CXIHWJ": "Level 2 Approval Required",
        "O676WZSGHA": "Level 2 Approval Required",
        "L8NTU4BZY2": "No Approval Required",
        "7N9EUBALU2": "No Approval Required",
        "U921IQSW6K": "No Approval Required",
        "TUSMQ1ZDFM": "Level 2 Approval Required",
    }

    # Expected cells with outputs
    assert set(Out.keys()) == {
        3,
        4,
        7,
        9,
    }, str(Out)


def example_3_6_compliance_to_dataframe():
    root = part_result.compliance_by_part_and_indicator[0]
    assert root.input_part_number == "asm_flap_mating"
    assert len(root.parts) == 12

    assert all(p.indicators["SVHC"].flag.name == "WatchListCompliant" for p in root.parts[:-1])
    assert root.parts[-1].input_part_number == "main_frame"
    assert root.parts[-1].indicators["SVHC"].flag.name == "WatchListHasSubstanceAboveThreshold"

    assert len(data) == 301
    assert len(df_non_compliant) == 18

    assert df_non_compliant["Item"].to_list() == [
        "P2",
        "S97",
        "S107",
        "S109",
        "R187",
        "R192",
        "S104",
        "S106",
        "R181",
        "R186",
        "S101",
        "S103",
        "R175",
        "R180",
        "S98",
        "S100",
        "R169",
        "R174",
    ]

    # Expected cells with outputs
    assert set(Out.keys()) == {6, 7}, str(Out)


def example_4_1_sustainability():
    assert len(records) == 50
    assert records[0]["type"] == "Part"
    assert records[0]["name"] == "Part1"
    assert round(records[0]["embodied energy [MJ]"]) == 593
    assert round(records[0]["climate change [kg CO2-eq]"]) == 48

    # Expected cells with outputs
    assert set(Out.keys()) == {
        3,
        5,
        6,
    }, str(Out)


def example_5_1_summary_and_messages():
    assert sustainability_summary.messages == []
    assert phases_df["Name"].to_list() == ["Material", "Processes", "Transport"]
    assert [round(i) for i in phases_df["EE%"].to_list()] == [56, 27, 17]
    assert [round(i) for i in phases_df["CC%"].to_list()] == [67, 19, 15]
    # Expected cells with outputs
    assert set(Out.keys()) == {
        3,
        4,
        5,
        6,
    }, str(Out)


def example_5_2_transports():
    assert len(transport_df_full) == 23
    assert len(transport_df) == 4
    assert transport_df["Name"].to_list() == [
        "Finished component 11B to warehouse",
        "Product from warehouse to distributor (air)",
        "Product from warehouse to distributor (truck 1)",
        "Other",
    ]
    assert transport_df["Distance [km]"].to_list() == [8000, 500, 350, 9375]
    assert [round(i) for i in transport_df["EE%"].to_list()] == [48, 23, 5, 24]

    assert [round(i, 3) for i in transport_df["EE [MJ/km]"].to_list()] == [0.006, 0.047, 0.015, 0.003]

    assert transport_by_category_df["Name"].to_list() == ["Distribution", "Manufacturing"]
    assert [round(i) for i in transport_by_category_df["EE%"].to_list()] == [30, 70]

    assert transport_by_part_df["Name"].to_list() == [
        "Component 11B",
        "Assembly",
        "Component 1C",
        "Component 11A",
        "Other",
    ]
    assert [round(i) for i in transport_by_part_df["EE%"].to_list()] == [49, 30, 6, 6, 8]

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3, 4, 7, 9, 10, 12, 13}, str(Out)


def example_5_3_materials():
    assert materials_df["Name"].to_list() == [
        "stainless-astm-cn-7ms-cast",
        "beryllium-beralcast191-cast",
        "steel-1010-annealed",
    ]
    assert [round(i) for i in materials_df["EE%"].to_list()] == [46, 35, 19]

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3}, str(Out)


def example_5_4_processes():
    assert primary_process_df["Name"].to_list() == [
        "Primary processing, Casting - stainless-astm-cn-7ms-cast",
        "Primary processing, Casting - steel-1010-annealed",
        "Primary processing, Metal extrusion, hot - steel-1010-annealed",
        "Other - None",
    ]
    assert [round(i) for i in primary_process_df["EE%"].to_list()] == [49, 34, 17, 0]

    assert secondary_process_df["Name"].to_list() == [
        "Secondary processing, Grinding - steel-1010-annealed",
        "Secondary processing, Machining, coarse - stainless-astm-cn-7ms-cast",
        "Machining, fine - steel-1010-annealed",
        "Secondary processing, Machining, fine - stainless-astm-cn-7ms-cast",
        "Other - None",
    ]
    assert [round(i) for i in secondary_process_df["EE%"].to_list()] == [45, 31, 15, 8, 2]

    assert joining_and_finishing_processes_df["Name"].to_list() == ["Joining and finishing, Welding, electric"]
    assert [round(i) for i in joining_and_finishing_processes_df["EE%"].to_list()] == [100]

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3, 4, 7, 8, 10, 11}, str(Out)


def example_5_5_hierarchical_plots():
    assert len(df) == 39
    assert round(df["EE [MJ]"].sum()) == 1186
    assert len(df_aggregated) == 14
    assert round(df_aggregated["EE [MJ]"].sum()) == 1186
    # Expected cells with outputs
    assert set(Out.keys()) == {2, 4, 10, 14}, str(Out)


def example_6_1_creating_an_xml_bom():
    assert len(rendered_bom.splitlines()) == 247
    assert root_part.indicators["EU REACH Candidate List"].flag.name == "WatchListUnknown"

    # Expected cells with outputs
    assert set(Out.keys()) == {10, 12}, str(Out)


def example_6_2_creating_an_xml_bom_from_json():
    assert len(bom_as_xml.splitlines()) == 263
    assert bom_as_xml.count("<ns0:Part>") == 8
    assert bom_as_xml.count("<ns0:Material>") == 6
    assert bom_as_xml.count("<ns0:Process>") == 13
    assert bom_as_xml.count("<ns0:TransportStage>") == 3

    assert len(bom.components) == 1
    assert len(bom.components[0].components) == 5
    assert len(bom.components[0].components[0].components) == 2
    assert len(bom.transport_phase) == 3

    # Expected cells with outputs
    assert set(Out.keys()) == {2, 3, 4, 5, 6, 7, 8, 9}, str(Out)


def example_6_3_creating_an_xml_bom_from_csv():
    assert len(bom_as_xml.splitlines()) == 340
    assert bom_as_xml.count("<ns0:Part>") == 15
    assert bom_as_xml.count("<ns0:Material>") == 11
    assert bom_as_xml.count("<ns0:Process>") == 0
    assert bom_as_xml.count("<ns0:TransportStage>") == 0

    # Expected cells with outputs
    assert set(Out.keys()) == {1}, str(Out)


examples_expectations = {
    "0_Basic_usage.py": example_0_basic_usage,
    "1_Database-specific_configuration.py": example_1_database_config,
    "2-1_Materials_impacted_substances.py": example_2_1_materials_impacted_substances,
    "2-2_Parts_impacted_substances.py": example_2_2_parts_impacted_substances,
    "2-3_BoM_impacted_substances.py": example_2_3_bom_impacted_substances,
    "2-4_External_database_materials.py": example_2_4_external_database_materials,
    "3-1_Substance_compliance.py": example_3_1_substance_compliance,
    "3-2_Material_compliance.py": example_3_2_material_compliance,
    "3-3_Part_compliance.py": example_3_3_part_compliance,
    "3-4_BoM_compliance.py": example_3_4_bom_compliance,
    "3-5_Compliance_for_external_data.py": example_3_5_compliance_for_external_data,
    "3-6_Writing_compliance_results_to_a_dataframe.py": example_3_6_compliance_to_dataframe,
    "4-1_Sustainability.py": example_4_1_sustainability,
    "5-1_Summary_and_messages.py": example_5_1_summary_and_messages,
    "5-2_Transports.py": example_5_2_transports,
    "5-3_Materials.py": example_5_3_materials,
    "5-4_Processes.py": example_5_4_processes,
    "5-5_Hierarchical_plots.py": example_5_5_hierarchical_plots,
    "6-1_Creating_an_XML_BoM.py": example_6_1_creating_an_xml_bom,
    "6-2_Creating_an_XML_BoM_from_JSON.py": example_6_2_creating_an_xml_bom_from_json,
    "6-3_Creating_an_XML_BoM_from_CSV.py": example_6_3_creating_an_xml_bom_from_csv,
}
