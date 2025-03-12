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
# This example uses an input file that is in the 24/12 XML BoM format. This structure requires Granta MI Restricted Substances and Sustainability Reports
# 2025 R2 or later. 
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
cxn = Connection(server_url).with_credentials("user_name", "password").connect()

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
# ## Summary per phase
# The sustainability summary result object contains a ``phases_summary`` property. This property summarizes the
# environmental impact contributions by lifecycle phase: materials, processes, and transport phases. The results for
# each phase include their absolute and relative contributions to the product as a whole.

sustainability_summary.phases_summary

# Use the [pandas](https://pandas.pydata.org/) and [plotly](https://plotly.com/python/) libraries to visualize the
# results. First, the data is translated from the BoM Analytics ``BomSustainabilitySummaryQueryResult`` to a pandas
# ``Dataframe`` object.

# +
import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"

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
phases_df

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


plot_impact(phases_df, "BoM sustainability summary - By phase")
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

# ## Materials phase
#
# The environmental contribution from the material phase is summarized in the ``material_details`` property. The results
# are aggregated: each item in ``material_details`` represents the total environmental impact of a material summed
# from all its occurrences in the BoM. Listed materials contribute more than 2% of the total impact for the material
# phase. Materials that do not contribute at least 2% of the total are aggregated under the ``Other`` item.

sustainability_summary.material_details

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
materials_df

plot_impact(materials_df, "Aggregated materials impact")

# Mass before and mass after secondary processing can help determine if the material mass removed during processing
# contributes a significant fraction of the impact of the overall material phase.

fig = go.Figure(
    data=[
        go.Bar(
            name="Mass before secondary processing",
            x=materials_df["Name"],
            y=materials_df[f"Mass before processing [{MASS_UNIT}]"],
        ),
        go.Bar(
            name="Mass after secondary processing",
            x=materials_df["Name"],
            y=materials_df[f"Mass after processing [{MASS_UNIT}]"],
        ),
    ],
    layout=go.Layout(
        xaxis=go.layout.XAxis(title="Materials"),
        yaxis=go.layout.YAxis(title=f"Mass [{MASS_UNIT}]"),
        legend=dict(orientation="h")
    ),
)
fig.show()

# ## Material processing phase
#
# The environmental contributions from primary and secondary processing (applied to materials) and the joining and
# finishing processes (applied to parts) are summarized in the ``primary_processes_details``,
# ``secondary_processes_details``, and ``joining_and_finishing_processes_details`` properties respectively.
# Each of these properties lists the unique process-material pairs (for primary and secondary processing) or
# individual processes (for joining and finishing) that contribute at least 5% of the total impact for that
# category of process. The percentage contributions are relative to the total contribution of all processes
# from the same category. Processes that do not meet the contribution threshold are aggregated under the
# ``Other`` item, with the material set to ``None``.

# ### Primary processing

sustainability_summary.primary_processes_details

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
primary_process_df

# Add a ``Name`` to each item that represents the process-material pair name.

primary_process_df["Name"] = primary_process_df.apply(
    lambda row: f"{row['Process name']} - {row['Material name']}", axis=1
)
plot_impact(
    primary_process_df, "Aggregated primary processes impact", textinfo="percent", hoverinfo="value+name+label"
)

# ### Secondary processing

sustainability_summary.secondary_processes_details

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
secondary_process_df

# Add a ``Name`` to each item that represents the process-material pair name.

secondary_process_df["Name"] = secondary_process_df.apply(
    lambda row: f"{row['Process name']} - {row['Material name']}", axis=1
)
plot_impact(
    secondary_process_df, "Aggregated secondary processes impact", textinfo="percent", hoverinfo="value+name+label"
)

# ### Joining and finishing
#
# Joining and finishing processes apply to parts or assemblies and therefore don't include a material identity.

sustainability_summary.joining_and_finishing_processes_details

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
joining_and_finishing_processes_df

plot_impact(
    joining_and_finishing_processes_df, "Aggregated secondary processes impact",
    textinfo="percent", hoverinfo="value+name+label"
)

# ## Hierarchical view
#
# Finally, aggregate the sustainability summary results into a single dataframe and present it in a hierarchical
# chart. This highlights the largest contributors at each level. In this example, two levels are defined:
# first the phase and then the contributors in the phase.

# First, rename the processes ``Other`` rows, so that they remain distinguishable after all processes have been
# grouped under a general ``Processes``.
#
# Use ``assign`` to add a ``parent`` column to each dataframe being concatenated.
# The ``join`` argument value ``inner`` specifies that only columns common to all dataframes are kept in the result.

# +
primary_process_df.loc[(primary_process_df["Name"] == "Other - None"), "Name"] = "Other primary processes"
secondary_process_df.loc[(secondary_process_df["Name"] == "Other - None"), "Name"] = "Other secondary processes"
joining_and_finishing_processes_df.loc[
    (joining_and_finishing_processes_df["Name"] == "Other - None"), "Name"] = "Other joining and finishing processes"

summary_df = pd.concat(
    [
        phases_df.assign(Parent=""),
        transport_df.assign(Parent="Transport"),
        materials_df.assign(Parent="Material"),
        primary_process_df.assign(Parent="Processes"),
        secondary_process_df.assign(Parent="Processes"),
        joining_and_finishing_processes_df.assign(Parent="Processes"),
    ],
    join="inner",
)
summary_df

# A sunburst chart presents hierarchical data radially.

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
