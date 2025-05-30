# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Perform a BoM sustainability summary query
#
# The following supporting files are required for this example:
#
# * [sustainability-bom-2412.xml](supporting-files/sustainability-bom-2412.xml)

# <div class="alert alert-info">
#
# **Info:**
#
# This example uses an input file that is in the 24/12 XML BoM format. This structure requires Granta MI Restricted
# Substances and Sustainability Reports 2025 R2 or later.
#
# To run this example with an older version of the reports bundle, use
# [sustainability-bom-2301.xml](supporting-files/sustainability-bom-2301.xml) instead. Some sections of this example
# will produce different results from the published example when this BoM is used.
# </div>

# ## Run a BoM sustainability summary query
#
# First, connect to Granta MI.
#

from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_autologon().connect()

# Next, create a sustainability summary query. The query accepts a single BoM as argument and an optional
# configuration for units. If a unit is not specified, the default unit is used. Default units for the analysis are
# ``MJ`` for energy, ``kg`` for mass, and ``km`` for distance.

# +
xml_file_path = "supporting-files/sustainability-bom-2412.xml"
with open(xml_file_path) as f:
    bom = f.read()

from ansys.grantami.bomanalytics import queries

MASS_UNIT = "kg"
ENERGY_UNIT = "MJ"
DISTANCE_UNIT = "km"

sustainability_summary_query = (
    queries.BomSustainabilitySummaryQuery()
    .with_bom(bom)
    .with_units(mass=MASS_UNIT, energy=ENERGY_UNIT, distance=DISTANCE_UNIT)
)
# -

sustainability_summary = cxn.run(sustainability_summary_query)

# ## Data visualization
#
# ### Tabulated data
#
# To aid with data visualization, aggregate the sustainability summary results into a single dataframe and present it in
# a hierarchical chart. This highlights the largest contributors at each level. In this example, two levels are defined:
# first the phase and then the contributors in the phase.

import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"
DISTANCE_HEADER = f"Distance [{DISTANCE_UNIT}]"

# +
phases_df = pd.DataFrame.from_records(
    [
        {
            "Name": item.name,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
        }
        for item in sustainability_summary.phases_summary
    ]
)
materials_df = pd.DataFrame.from_records(
    [
        {
            "Name": item.identity,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
            f"Mass before processing [{MASS_UNIT}]": item.mass_before_processing.value,
            f"Mass after processing [{MASS_UNIT}]": item.mass_after_processing.value,
        }
        for item in sustainability_summary.material_details
    ]
)
transport_df = pd.DataFrame.from_records(
    [
        {
            "Name": item.name,
            DISTANCE_HEADER: item.distance.value,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
        }
        for item in sustainability_summary.transport_details
    ]
)
# -

# +
primary_process_df = pd.DataFrame.from_records(
    [
        {
            "Process name": item.process_name,
            "Material name": item.material_identity,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
        }
        for item in sustainability_summary.primary_processes_details
    ]
)
secondary_process_df = pd.DataFrame.from_records(
    [
        {
            "Process name": item.process_name,
            "Material name": item.material_identity,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
        }
        for item in sustainability_summary.secondary_processes_details
    ]
)
joining_and_finishing_processes_df = pd.DataFrame.from_records(
    [
        {
            "Name": item.process_name,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
        }
        for item in sustainability_summary.joining_and_finishing_processes_details
    ]
)
primary_process_df["Name"] = primary_process_df.apply(
    lambda row: f"{row['Process name']} - {row['Material name']}", axis=1
)
secondary_process_df["Name"] = secondary_process_df.apply(
    lambda row: f"{row['Process name']} - {row['Material name']}", axis=1
)
primary_process_df.loc[(primary_process_df["Name"] == "Other - None"), "Name"] = "Other primary processes"
secondary_process_df.loc[(secondary_process_df["Name"] == "Other - None"), "Name"] = "Other secondary processes"
joining_and_finishing_processes_df.loc[
    (joining_and_finishing_processes_df["Name"] == "Other - None"), "Name"] = "Other joining and finishing processes"


# First, rename the processes ``Other`` rows, so that they remain distinguishable after all processes have been
# grouped under a general ``Processes``.
#
# Use ``assign`` to add a ``parent`` column to each dataframe being concatenated.
# The ``join`` argument value ``inner`` specifies that only columns common to all dataframes are kept in the result.


def aggregate_small_values(df, aggregation_value_name):
    # Define the criterion
    criterion = (df["EE%"] < 5.0) | (df["CC%"] < 5.0)

    # Aggregate all rows that meet the criterion
    df_below_5_pct = df.loc[criterion].sum(numeric_only=True).to_frame().T
    df_below_5_pct["Name"] = aggregation_value_name

    # Sort all rows that do not meet the criterion by embodied energy
    df_over_5_pct = df.loc[~(criterion)].sort_values(by="EE%", ascending=False)

    # Concatenate the rows together
    df_aggregated = pd.concat([df_over_5_pct, df_below_5_pct], ignore_index=True)
    return df_aggregated


summary_df = pd.concat(
    [
        phases_df.assign(Parent=""),
        aggregate_small_values(transport_df, "Other transport").assign(Parent="Transport"),
        aggregate_small_values(materials_df, "Other materials").assign(Parent="Material"),
        aggregate_small_values(primary_process_df, "Other primary processes").assign(Parent="Processes"),
        aggregate_small_values(secondary_process_df, "Other secondary processes").assign(Parent="Processes"),
        aggregate_small_values(
            joining_and_finishing_processes_df,
            "Other joining and finishing processes"
        ).assign(Parent="Processes"),
    ],
    join="inner",
)
summary_df.reset_index(inplace=True, drop=True)
# -

# ### Sunburst chart

# A sunburst chart presents hierarchical data radially.
import plotly.graph_objects as go

fig = go.Figure(
    go.Sunburst(
        labels=summary_df["Name"],
        parents=summary_df["Parent"],
        values=summary_df[EE_HEADER],
        branchvalues="total",
    ),
    layout_title_text=f"Embodied Energy [{ENERGY_UNIT}]",
)
fig.show()

# ### Icicle chart

# An icicle chart presents hierarchical data as rectangular sectors.

fig = go.Figure(
    go.Icicle(
        labels=summary_df["Name"],
        parents=summary_df["Parent"],
        values=summary_df[EE_HEADER],
        branchvalues="total",
    ),
    layout_title_text=f"Embodied Energy [{ENERGY_UNIT}]",
)
fig.show()

# ### Sankey diagram

# Sankey diagrams represent data as a network of nodes and links, with the relative sizes of these nodes and links
# representing their contributions to the flow of some quantity. In plotly, Sankey diagrams require nodes and links to
# be defined explicitly.
#
# First, prepare the node data. Copy the previous dataframe into a new dataframe and perform some additional processing
# required for a Sankey diagram.

node_df = summary_df.copy()

# Replace empty parent cells with a reference to a new "Product" row. This new row will be created in the next cell.

node_df["Parent"] = summary_df["Parent"].replace("", "Product")

# Add a new row to represent the entire product. Values for this row are computed based on the sum of all nodes that are
# direct children of this row.

# +
product_row = {
    "Name": "Product",

    # Sum the contributions for all rows which are a child of 'Product'
    "EE%": sum(node_df[node_df["Parent"] == "Product"]["EE%"]),
    "EE [MJ]": sum(node_df[node_df["Parent"] == "Product"]["EE [MJ]"]),
    "CC%": sum(node_df[node_df["Parent"] == "Product"]["CC%"]),
    "CC [kg]": sum(node_df[node_df["Parent"] == "Product"]["CC [kg]"]),
    "Parent": "",
}

# Add the row to the end of the dataframe
node_df.loc[len(node_df)] = product_row
# -

# Define colors for each node type in the Sankey diagram by mapping a built-in Plotly color swatch to node names. First,
# attempt to get the color for a node based on its name. If this fails, use the name of the parent node instead.

# +
import plotly.express as px

color_map = {
    "Product": px.colors.qualitative.Pastel1[0],
    "Material": px.colors.qualitative.Pastel1[1],
    "Transport": px.colors.qualitative.Pastel1[2],
    "Processes": px.colors.qualitative.Pastel1[3],
}


def get_node_color(x):
    name = x["Name"]
    parent = x["Parent"]

    try:
        return color_map[name]
    except KeyError:
        return color_map[parent]


node_df["Color"] = node_df.apply(get_node_color, axis=1)
node_df.head()
# -

# Next, create a new dataframe to store the link information. Each row in this dataframe represents a link on the Sankey
# diagram. All links have a 'source' and a 'target', and nodes may function as a source, as a target, or as both.
#
# First create an empty dataframe, and then copy the row index values from the node dataframe to the "Source" column
# in the new dataframe. Skip the "Product" row, since this node does not act as the source for any links.

# +
link_df = pd.DataFrame()

# Store all nodes which act as sources in a variable for repeated use
source_nodes = node_df[node_df["Name"] != "Product"]

link_df["Source"] = source_nodes.index
# -

# Now create a "Target" column by using the node dataframe as a cross-reference to infer the hierarchy.

link_df["Target"] = source_nodes["Parent"].apply(lambda x: node_df.index[node_df["Name"] == x].values[0])

# The size of the link is defined as the size of the source node. The color of the link is defined as the color of the
# target node. Take advantage of the fact that the link and node dataframes have the same index in the same order.

link_df["Value"] = node_df["EE [MJ]"]
link_df["Color"] = link_df["Target"].apply(lambda x: node_df.iloc[x]["Color"])
link_df.head()

# Finally, create the Sankey diagram.

fig = go.Figure(
    go.Sankey(
        valueformat = ".0f",
        valuesuffix = " MJ",
        node = dict(
            pad = 15,
            thickness = 15,
            line = dict(color = "black", width = 0.5),
            label = node_df["Name"],
            color = node_df["Color"]
        ),
        link = dict(
            source = link_df["Source"],
            target = link_df["Target"],
            value = link_df["Value"],
            color = link_df["Color"],
        )
    ),
    layout_title_text=f"Embodied Energy [{ENERGY_UNIT}]",
)
fig.show()
