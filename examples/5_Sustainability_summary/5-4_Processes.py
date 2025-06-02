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

# # Sustainability summary: Process phase
#
# The following supporting files are required for this example:
#
# * [sustainability-bom-2412.xml](../supporting-files/sustainability-bom-2412.xml)

# <div class="alert alert-info">
#
# **Info:**
#
# This example uses an input file that is in the 24/12 XML BoM format. This structure requires Granta MI Restricted
# Substances and Sustainability Reports 2025 R2 or later.
#
# To run this example with an older version of the reports bundle, use
# [sustainability-bom-2301.xml](../supporting-files/sustainability-bom-2301.xml) instead. Some sections of this example
# will produce different results from the published example when this BoM is used.
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

# ## Process phase
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

# +
import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"

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
# -

# Add a ``Name`` to each item that represents the process-material pair name.

primary_process_df["Name"] = primary_process_df.apply(
    lambda row: f"{row['Process name']} - {row['Material name']}", axis=1
)
primary_process_df

# This example produces multiple plots which all consist of a pair of pie charts representing the
# "Embodied Energy" and "Climate Change CO<sub>2</sub> equivalent" impacts respectively. Define a
# helper function to create these plots.

# +
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_impact(df, title):
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=["Embodied Energy", "Climate Change"],
    )
    fig.add_trace(go.Pie(labels=df["Name"], values=df[EE_HEADER], name=ENERGY_UNIT), 1, 1)
    fig.add_trace(go.Pie(labels=df["Name"], values=df[CC_HEADER], name=MASS_UNIT), 1, 2)
    fig.update_layout(title_text=title, legend=dict(orientation="h"))
    fig.update_traces(textposition="inside", textinfo="percent", hoverinfo="value+name+label")
    fig.show()
# -

plot_impact(primary_process_df, "Aggregated primary processes impact")

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
plot_impact(secondary_process_df, "Aggregated secondary processes impact")

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

plot_impact(joining_and_finishing_processes_df, "Aggregated joining and finishing processes impact")
