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

# # Transport phase
#
# This example shows how to explore the transport phase results of a sustainability summary query.
#
# The following supporting files are required for this example:
#
# * [sustainability-bom-2412.xml](../supporting-files/sustainability-bom-2412.xml)
#
# For help on constructing an XML BoM, see [BoM examples](../6_BoMs/index.rst).

# <div class="alert alert-info">
#
# **Info:**
#
# This example requires Granta MI Restricted Substances and Sustainability Reports 2025 R2 or later.
#
# If you would like to run an example of exploring the transport phase results of a summary query for an earlier version
# of the reports bundle, refer to the version of the documentation that corresponds to that version of the reports
# bundle.
# </div>

# ## Run a sustainability summary query

# +
from ansys.grantami.bomanalytics import Connection, queries

MASS_UNIT = "kg"
ENERGY_UNIT = "MJ"
DISTANCE_UNIT = "km"

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()

xml_file_path = "../supporting-files/sustainability-bom-2412.xml"
with open(xml_file_path) as f:
    bom = f.read()

sustainability_summary_query = (
    queries.BomSustainabilitySummaryQuery()
    .with_bom(bom)
    .with_units(mass=MASS_UNIT, energy=ENERGY_UNIT, distance=DISTANCE_UNIT)
)
sustainability_summary = cxn.run(sustainability_summary_query)
# -

# ## Transport phase
#
# The environmental contribution from the transport phase is summarized in the ``transport_details`` property. Results
# include the individual environmental impact for each transport stage included in the input BoM.
#
# A BoM may include many transport stages, each describing transportation throughout the product lifecycle. Print the
# first three only.

sustainability_summary.transport_details[:3]

# Convert all to a DataFrame. To see the distribution of results, use the `DataFrame.describe()` method.

# +
import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"
DISTANCE_HEADER = f"Distance [{DISTANCE_UNIT}]"

transport_df_full = pd.DataFrame.from_records(
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
transport_df_full.describe()
# -

# Most of these transport stages contribute little to the overall sustainability impact. To make a visualization more
# insightful, group all transport stages that contribute less than 5% of embodied energy or climate change in a single
# 'Other' transport stage.

# +
# Define the criterion
criterion = (transport_df_full["EE%"] < 5.0) | (transport_df_full["CC%"] < 5.0)

# Aggregate all rows that meet the criterion
transport_df_below_5_pct = transport_df_full.loc[criterion].sum(numeric_only=True).to_frame().T
transport_df_below_5_pct["Name"] = "Other"

# Sort all rows that do not meet the criterion by embodied energy
transport_df_over_5_pct = transport_df_full.loc[~(criterion)].sort_values(by="EE%", ascending=False)

# Concatenate the rows together
transport_df = pd.concat([transport_df_over_5_pct, transport_df_below_5_pct], ignore_index=True)
transport_df
# -

# This example produces multiple plots which all consist of a pair of pie charts representing the
# "Embodied Energy" and "Climate Change CO<sub>2</sub> equivalent" impacts respectively. Define a
# helper function to create these plots.

# +
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_impact(df, title, textinfo="percent+label", hoverinfo="value+name", labels=True):
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=["Embodied Energy", "Climate Change"],
    )
    fig.add_trace(go.Pie(labels=df["Name"], values=df[EE_HEADER], name=ENERGY_UNIT), 1, 1)
    fig.add_trace(go.Pie(labels=df["Name"], values=df[CC_HEADER], name=MASS_UNIT), 1, 2)
    fig.update_layout(title_text=title, legend=dict(orientation="h"))
    if labels:
        fig.update_traces(textposition="inside", textinfo=textinfo, hoverinfo=hoverinfo)
    fig.show()
# -

# Use this function to plot the environment impact for all transport stages.

plot_impact(transport_df, "Transport stages - environmental impact", labels=False)

# ### Transport impact per unit distance

# In some situations, it might be useful to calculate the environmental impact per distance travelled and add the
# results as new columns in the dataframe.

EE_PER_DISTANCE = f"EE [{ENERGY_UNIT}/{DISTANCE_UNIT}]"
CC_PER_DISTANCE = f"CC [{MASS_UNIT}/{DISTANCE_UNIT}]"
transport_df[EE_PER_DISTANCE] = transport_df.apply(lambda row: row[EE_HEADER] / row[DISTANCE_HEADER], axis=1)
transport_df[CC_PER_DISTANCE] = transport_df.apply(lambda row: row[CC_HEADER] / row[DISTANCE_HEADER], axis=1)
transport_df

fig = make_subplots(
    rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]], subplot_titles=[EE_PER_DISTANCE, CC_PER_DISTANCE]
)
fig.add_trace(
    go.Pie(labels=transport_df["Name"], values=transport_df[EE_PER_DISTANCE], name=f"{ENERGY_UNIT}/{DISTANCE_UNIT}"),
    1,
    1,
)
fig.add_trace(
    go.Pie(labels=transport_df["Name"], values=transport_df[CC_PER_DISTANCE], name=f"{MASS_UNIT}/{DISTANCE_UNIT}"), 1, 2
)
fig.update_layout(
    title_text="Transport stages impact - Relative to distance travelled",
    legend=dict(orientation="h")
)
fig.show()

# ### Transport impact aggregated by category

# The environmental impacts from transportation associated with distribution and manufacturing phases are summarized in
# the ``distribution_transport_summary`` and ``manufacturing_transport_summary`` properties.

sustainability_summary.distribution_transport_summary

# +
dist_summary = sustainability_summary.distribution_transport_summary
distribution = {
    "Name": "Distribution",
    DISTANCE_HEADER: dist_summary.distance.value,
    "EE%": dist_summary.embodied_energy_percentage,
    EE_HEADER: dist_summary.embodied_energy.value,
    "CC%": dist_summary.climate_change_percentage,
    CC_HEADER: dist_summary.climate_change.value,
}

manuf_summary = sustainability_summary.manufacturing_transport_summary
manufacturing = {
    "Name": "Manufacturing",
    DISTANCE_HEADER: manuf_summary.distance.value,
    "EE%": manuf_summary.embodied_energy_percentage,
    EE_HEADER: manuf_summary.embodied_energy.value,
    "CC%": manuf_summary.climate_change_percentage,
    CC_HEADER: manuf_summary.climate_change.value,
}

transport_by_category_df = pd.DataFrame.from_records([distribution, manufacturing])
transport_by_category_df
# -

plot_impact(transport_by_category_df, "Transport impact - grouped by category")

# ### Transport impact aggregated by part

# The environmental contributions from transportation are summarized by the associated part in the
# ``transport_details_aggregated_by_part`` property. This property groups parts that contribute less than 5% embodied
# energy or climate change automatically.

sustainability_summary.transport_details_aggregated_by_part

transport_by_part_df = pd.DataFrame.from_records(
    [
        {
            "Name": item.part_name,
            "Parent part name": item.parent_part_name,
            DISTANCE_HEADER: item.distance.value,
            "EE%": item.embodied_energy_percentage,
            EE_HEADER: item.embodied_energy.value,
            "CC%": item.climate_change_percentage,
            CC_HEADER: item.climate_change.value,
            "Transport types": "; ".join(item.transport_types),
        }
        for item in sustainability_summary.transport_details_aggregated_by_part
    ]
)
transport_by_part_df

plot_impact(transport_by_part_df, "Transport impact - grouped by part")
