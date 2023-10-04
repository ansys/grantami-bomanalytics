# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Perform a BoM sustainability summary query
#
# The following supporting files are required for this example:
#
# * [bom-2301-jack-stand.xml](supporting-files/bom-2301-jack-stand.xml)

# ## Run a BoM sustainability summary query
#
# First, connect to Granta MI.
#

from ansys.grantami.bomanalytics import Connection

server_url = "http://my_grantami_server/mi_servicelayer"
cxn = Connection(server_url).with_credentials("user_name", "password").connect()

# Next, create a sustainability summary query. The query accepts a single BoM as argument, as well as optional
# configuration for units. If a unit is not specified, the default unit is used. Default units for the analysis are:
# `MJ` for energy, `kg` for mass, and `km` for distance.

# +
xml_file_path = "supporting-files/bom-2301-jack-stand.xml"
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

# The ``BomSustainabilitySummaryQueryResult`` object returned implements a ``messages`` property, and properties
# showing the environmental footprint of the items included in the BoM.
# Log messages are sorted by decreasing severity. The same messages are available on in the MI Service Layer log file,
# and are logged via the standard ``logging`` module.
# The next sections show examples of visualizations for the results of the sustainability summary query.
#
# ## Summary per phase
# The sustainability summary result object contains a `phases_summary` property. This property divides environmental
# footprint contributions into three categories: materials, processes, and transport phases. Each include their absolute
# and relative contributions to the product as a whole.

sustainability_summary.phases_summary

# Use the [pandas](https://pandas.pydata.org/) and [plotly](https://plotly.com/python/) libraries to visualize the
# results. The data will first be translated from the BoM Analytics ``BomSustainabilitySummaryQueryResult`` to a pandas
# ``Dataframe``

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


def plot_footprint(df, title, textinfo="percent+label", hoverinfo="value+name"):
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=["Embodied Energy", "Climate Change"],
    )
    fig.add_trace(go.Pie(labels=df["Name"], values=df[EE_HEADER], name=ENERGY_UNIT), 1, 1)
    fig.add_trace(go.Pie(labels=df["Name"], values=df[CC_HEADER], name=MASS_UNIT), 1, 2)
    fig.update_layout(title_text=title)
    fig.update_traces(textposition="inside", textinfo=textinfo, hoverinfo=hoverinfo)
    fig.show()


plot_footprint(phases_df, "BoM sustainability summary - By phase")
# -

# ## The transport phase
#
# The environmental contribution from the transport phase is summarized in the `transport_details` property. Results
# include the individual environmental footprint for each transport stage included in the input BoM.

sustainability_summary.transport_details

# +
DISTANCE_HEADER = f"Distance [{DISTANCE_UNIT}]"

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
transport_df
# -

plot_footprint(transport_df, "Transport stages - environmental footprint")

# In some situations, it may be useful to calculate the environmental footprint per distance travelled and add the
# results as new columns in the `DataFrame`.

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
fig.update_layout(title_text="Transport stages footprint - Relative to distance travelled")
fig.update_traces(textposition="inside", textinfo="percent+label", hoverinfo="value+name")
fig.show()

# ## The materials phase
#
# The environmental contribution from the material phase is summarized in the `material_details` property. The results
# are aggregated: each item in ``material_details`` represents the total environmental footprint of a material summed
# from all its occurrences in the BoM. Listed materials contribute more than 2% of the total footprint for the material
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

plot_footprint(materials_df, "Aggregated materials footprint")

# Mass before and mass after secondary processing can help determine if the material mass removed during processing
# contributes a significant fraction of the footprint of the overall material phase.

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
    ),
)
fig.show()

# ## The material processing phase
#
# The environmental contribution specifically from processing applied to raw materials is summarized in the
# `primary_processes_details`, `secondary_processes_details`, and `joining_and_finishing_processes_details` properties
# for primary, secondary, and joining and finishing process categories respectively. Each category lists unique
# process-material pairs, which contribute at least 5% of the total for the process category. The relative contributions
# describe the contribution of a process-material pair, relative to the total contributions of all processes from the
# same category. Processes that do meet the contribution threshold are aggregated under the ``Other`` item, with the
# material set to `None`.

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

# Add a `Name` to each item that represents the process-material pair name.

primary_process_df["Name"] = primary_process_df.apply(
    lambda row: f"{row['Process name']} - {row['Material name']}", axis=1
)
plot_footprint(
    primary_process_df, "Aggregated primary processes footprint", textinfo="percent", hoverinfo="value+name+label"
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

# Add a `Name` to each item that represents the process-material pair name.

secondary_process_df["Name"] = secondary_process_df.apply(
    lambda row: f"{row['Process name']} - {row['Material name']}", axis=1
)
plot_footprint(
    secondary_process_df, "Aggregated secondary processes footprint", textinfo="percent", hoverinfo="value+name+label"
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

plot_footprint(
    joining_and_finishing_processes_df, "Aggregated secondary processes footprint",
    textinfo="percent", hoverinfo="value+name+label"
)

# ## Hierarchical view
#
# Finally, aggregate the sustainability summary results into a single `DataFrame` and present it in a hierarchical
# chart. This highlights the largest contributors at each level. In this example, two levels are defined:
# first the phase and then the contributors in the phase.

# First, rename the processes ``Other`` rows, so that they remain distinguishable after all processes have been
# grouped under a general ``Processes``.
#
# Use `assign` to add a `parent` column to each `DataFrame` being concatenated
# The `join` argument value `inner` specifies that only columns common to all dataframes are kept in the result

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
