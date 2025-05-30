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
sustainability_summary

# The ``BomSustainabilitySummaryQueryResult`` object that is returned implements a ``messages`` property and properties
# showing the environmental impact of the items included in the BoM.
# Log messages are sorted by decreasing severity. The same messages are available in the MI Service Layer log file
# and are logged using the standard ``logging`` module.
# The next sections show examples of visualizations for the results of the sustainability summary query.
#

# +
import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"

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

# ## Transport phase
#
# The environmental contribution from the transport phase is summarized in the ``transport_details`` property. Results
# include the individual environmental impact for each transport stage included in the input BoM. A BoM may include
# many transport stages, each describing transportation throughout the product lifecycle. Print the first three only.

sustainability_summary.transport_details[:3]

# Convert all to a DataFrame and describe the result

# +
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

# <div class="alert alert-info">
#
# **Info:**
#
# This section requires Granta MI Restricted Substances and Sustainability Reports 2025 R2. Results will differ from
# published examples if older software versions are used.
# </div>

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

# <div class="alert alert-info">
#
# **Info:**
#
# This section requires Granta MI Restricted Substances and Sustainability Reports 2025 R2. Results will differ from
# published examples if older software versions are used.
# </div>

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
