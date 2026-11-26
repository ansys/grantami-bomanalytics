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

# # Material phase
#
# This example shows how to explore the material phase results of a sustainability summary query.
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

# ## Materials phase
#
# The environmental contribution from the material phase is summarized in the ``material_details`` property. The results
# are aggregated: each item in ``material_details`` represents the total environmental impact of a material summed
# from all its occurrences in the BoM. Listed materials contribute more than 2% of the total impact for the material
# phase. Materials that do not contribute at least 2% of the total are aggregated under the ``Other`` item.

sustainability_summary.material_details

# +
import pandas as pd

EE_HEADER = f"EE [{ENERGY_UNIT}]"
CC_HEADER = f"CC [{MASS_UNIT}]"

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
# -

# Plot a pair of pie charts which show the "Embodied Energy" and "Climate Change CO<sub>2</sub> equivalent" impacts
# respectively.

# +
import plotly.graph_objects as go
from plotly.subplots import make_subplots


fig = make_subplots(
    rows=1,
    cols=2,
    specs=[[{"type": "domain"}, {"type": "domain"}]],
    subplot_titles=["Embodied Energy", "Climate Change"],
)
fig.add_trace(go.Pie(labels=materials_df["Name"], values=materials_df[EE_HEADER], name=ENERGY_UNIT), 1, 1)
fig.add_trace(go.Pie(labels=materials_df["Name"], values=materials_df[CC_HEADER], name=MASS_UNIT), 1, 2)
fig.update_layout(title_text="Aggregated materials impact", legend=dict(orientation="h"))
fig.update_traces(textposition="inside", textinfo="percent+label", hoverinfo="value+name")
fig.show()
# -

# Mass before and mass after secondary processing can help determine if the material mass removed during processing
# contributes a significant fraction of the impact of the overall material phase.
#
# Plot the aggregated material masses as a bar chart.

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
