# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # BoM sustainability summary: Hierarchical plotting
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

# + [markdown] jp-MarkdownHeadingCollapsed=true
# ## Example scope
#
# This example shows how to show all aspects of the sustainability summary result in single hierarchical plots.
# For more details about the different properties included in the sustainability summary result, see the other
# examples in this section:
#
# * BoM sustainability summary: messages and phase summary
#   * ``messages``
#   * ``phase_summary``
# * BoM sustainability summary: transport
#   * ``transport_details``
#   * ``distribution_transport_summary``
#   * ``manufacturing_transport_summary``
#   * ``transport_details_aggregated_by_part``
# * BoM sustainability summary: material
#   * ``material_details``
# * BoM sustainability summary: processes
#   * ``primary_processes_details``
#   * ``secondary_processes_details``
#   * ``joining_and_finishing_processes_details``
# -

# ## Run a BoM sustainability summary query
#
# For more context around executing the sustainability summary query, see the "BoM sustainability summary: messages
# and phase summary" example.

# +
from ansys.grantami.bomanalytics import Connection, queries

MASS_UNIT = "kg"
ENERGY_UNIT = "MJ"
DISTANCE_UNIT = "km"

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()

xml_file_path = "supporting-files/sustainability-bom-2412.xml"
with open(xml_file_path) as f:
    bom = f.read()

sustainability_summary_query = (
    queries.BomSustainabilitySummaryQuery()
    .with_bom(bom)
    .with_units(mass=MASS_UNIT, energy=ENERGY_UNIT, distance=DISTANCE_UNIT)
)
sustainability_summary = cxn.run(sustainability_summary_query)
# -

# ## Data visualization
#
# ### Tabulated data
#
# To plot data hierarchically, first create a dataframe that aggregates all data together. See the other notebooks in
# this section for more detail around converting these properties to dataframes.

# +
import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"


def create_dataframe_record(item, parent):
    record = {
        "Parent": parent,
        EE_HEADER: item.embodied_energy.value,
        CC_HEADER: item.climate_change.value,
    }

    if parent == "Material":
        record["Name"] = item.identity
    elif parent == "Processes":
        try:  # Joining and finishing processes
            record["Name"] = item.name
        except AttributeError:  # Primary and secondary processes
            record["Name"] = f"{item.process_name} - {item.material_identity}"
    else:
        record["Name"] = item.name
    return record


records = []
records.extend(
    [
        create_dataframe_record(item, "")
        for item in sustainability_summary.phases_summary
    ]
)
records.extend(
    [
        create_dataframe_record(item, "Material")
        for item in sustainability_summary.material_details
    ]
)
records.extend(
    [
        create_dataframe_record(item, "Transport")
        for item in sustainability_summary.transport_details
    ]
)
records.extend(
    [
        create_dataframe_record(item, "Processes")
        for item in (
            sustainability_summary.primary_processes_details +
            sustainability_summary.secondary_processes_details +
            sustainability_summary.joining_and_finishing_processes_details
        )
    ]
)

df = pd.DataFrame.from_records(records)
df.head()
# -

# A lot of the rows in the dataframe are small in the context of the overall sustainability impact of the
# product. Define a function to aggregate all rows that contribute less than 5% of their phase's
# sustainability impact into a single row.

def sort_and_aggregate_small_values(df: pd.DataFrame) -> pd.DataFrame:
    # Define the criterion
    total_embodied_energy = df[EE_HEADER].sum()
    criterion = df[EE_HEADER] / total_embodied_energy < 0.05

    # Find rows that meet the criterion
    small_rows = df.loc[criterion]

    # If no rows met the aggregation criterion, return the original dataframe and exit
    if len(small_rows) == 0:
        return df

    # Aggregate the rows to a new "Other" row
    df_below_5_pct = small_rows.sum(numeric_only=True).to_frame().T
    df_below_5_pct["Name"] = "Other"

    # Sort all rows that do not meet the criterion by embodied energy
    df_over_5_pct = df.loc[~(criterion)].sort_values(by=EE_HEADER, ascending=False)

    # Concatenate the rows together
    df_aggregated = pd.concat([df_over_5_pct, df_below_5_pct], ignore_index=True)
    return df_aggregated


# Apply this function to each sustainability phase, and then perform some additional tidying up of
# the dataframe.

# +
# Apply the function
df_aggregated = df.groupby("Parent").apply(sort_and_aggregate_small_values, include_groups=False)

# Convert the grouped dataframe back into a dataframe with a single index
df_aggregated.reset_index(inplace=True, level="Parent", drop=False)

# Rename the "Other" rows created by the function to include the parent name in the stage name
df_aggregated["Name"] = df_aggregated.apply(
    lambda x: f"Other {x['Parent']}" if x["Name"] == "Other" else x,
    axis="columns",
)["Name"]

# Reset the top-level numeric index
df_aggregated.reset_index(inplace=True, drop=True)

# Display the result
df_aggregated.head(10)
# -

# ### Sunburst chart

# A sunburst chart presents hierarchical data radially.

# +
import plotly.graph_objects as go

fig = go.Figure(
    go.Sunburst(
        labels=df_aggregated["Name"],
        parents=df_aggregated["Parent"],
        values=df_aggregated[EE_HEADER],
        branchvalues="total",
    ),
    layout_title_text=f"Embodied Energy [{ENERGY_UNIT}]",
)
fig.show()
# -

# ### Icicle chart

# An icicle chart presents hierarchical data as rectangular sectors.

fig = go.Figure(
    go.Icicle(
        labels=df_aggregated["Name"],
        parents=df_aggregated["Parent"],
        values=df_aggregated[EE_HEADER],
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

node_df = df_aggregated.copy()

# Replace empty parent cells with a reference to a new "Product" row. This new row will be created in the next cell.

node_df["Parent"] = df_aggregated["Parent"].replace("", "Product")

# Add a new row to represent the entire product. Values for this row are computed based on the sum of all nodes that are
# direct children of this row.

# +
product_row = {
    "Name": "Product",

    # Sum the contributions for all rows which are a child of 'Product'
    EE_HEADER: sum(node_df[node_df["Parent"] == "Product"][EE_HEADER]),
    CC_HEADER: sum(node_df[node_df["Parent"] == "Product"][CC_HEADER]),
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
