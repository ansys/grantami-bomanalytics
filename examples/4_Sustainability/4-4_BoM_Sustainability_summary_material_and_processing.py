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
